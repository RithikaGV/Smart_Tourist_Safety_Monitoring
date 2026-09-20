"""
controllers/incident_controller.py
-----------------------------------
Incident management for the admin panel - manual filing, the filterable list,
the Pending/Investigating/Closed workflow, and officer assignment.
"""
from datetime import datetime, timedelta

from fastapi import HTTPException

from database.db import get_db
from utils.id_generator import next_sequential_id
from utils.socket_manager import sio
from utils.status_map import to_ui_status, to_priority, FROM_UI_INCIDENT
from utils.efir_generator import generate_efir
from models.incident import IncidentCreateRequest

TIME_FILTERS = {"all": None, "24h": 1440, "7d": 10080, "30d": 43200}


async def _shape_incident(incident: dict, db) -> dict:
    user = await db["users"].find_one({"userId": incident["userId"]}, {"fullName": 1, "mobileNumber": 1})
    officer = None
    if incident.get("assignedOfficerId"):
        officer = await db["officers"].find_one({"officerId": incident["assignedOfficerId"]}, {"name": 1, "station": 1})

    coords = incident["location"]["coordinates"]
    return {
        "incidentId": incident["incidentId"],
        "userId": incident["userId"],
        "touristName": (user or {}).get("fullName", incident["userId"]),
        "touristPhone": (user or {}).get("mobileNumber"),
        "type": incident["type"],
        "category": incident.get("category", "other"),
        "severity": incident.get("severity", "medium"),
        "priority": to_priority(incident.get("severity", "medium")),
        "status": incident["status"],
        "uiStatus": to_ui_status(incident["status"]),
        "description": incident.get("description"),
        "location": {"lat": coords[1], "lng": coords[0], "name": incident.get("locationName")},
        "assignedOfficer": {"officerId": incident.get("assignedOfficerId"), "name": (officer or {}).get("name"), "station": (officer or {}).get("station")} if officer else None,
        "efirId": incident.get("efirId"),
        "tripId": incident.get("tripId"),
        "createdAt": incident["createdAt"].isoformat() if hasattr(incident.get("createdAt"), "isoformat") else incident.get("createdAt"),
    }


async def create_incident(payload: IncidentCreateRequest, actor_id: str) -> dict:
    db = get_db()
    user = await db["users"].find_one({"userId": payload.userId})
    if not user:
        raise HTTPException(status_code=404, detail="Tourist not found")

    incident_id = await next_sequential_id("incidents", "incidentId", "INC")
    now = datetime.utcnow()

    incident = {
        "incidentId": incident_id,
        "userId": payload.userId,
        "tripId": payload.tripId,
        "type": "manual_report",
        "category": payload.category,
        "severity": payload.severity,
        "status": "open",
        "location": {"type": "Point", "coordinates": [payload.lng, payload.lat]},
        "locationName": payload.locationName,
        "description": payload.description,
        "assignedOfficerId": None,
        "reportedByAdminId": actor_id,
        "respondedAt": None,
        "resolvedAt": None,
        "efirId": None,
        "createdAt": now,
        "updatedAt": now,
    }
    await db["incidents"].insert_one(dict(incident))

    shaped = await _shape_incident(incident, db)
    await sio.emit("incident:new", shaped, room="admin-room")
    return {"success": True, "incident": shaped}


async def list_incidents(
    time_filter: str = "all",
    ui_status: str | None = None,
    category: str | None = None,
    limit: int = 200,
) -> dict:
    db = get_db()
    query: dict = {}

    minutes = TIME_FILTERS.get(time_filter)
    if minutes:
        query["createdAt"] = {"$gte": datetime.utcnow() - timedelta(minutes=minutes)}

    if ui_status and ui_status.lower() != "all":
        buckets = {
            "pending": ["open"],
            "investigating": ["acknowledged", "responding"],
            "closed": ["resolved", "false_alarm"],
        }
        if ui_status.lower() in buckets:
            query["status"] = {"$in": buckets[ui_status.lower()]}

    if category and category.lower() != "all":
        query["category"] = category.lower()

    rows = await db["incidents"].find(query).sort("createdAt", -1).limit(limit).to_list(length=limit)
    shaped = [await _shape_incident(i, db) for i in rows]
    return {"success": True, "count": len(shaped), "incidents": shaped}


async def incident_detail(incident_id: str) -> dict:
    db = get_db()
    incident = await db["incidents"].find_one({"incidentId": incident_id})
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    shaped = await _shape_incident(incident, db)

    trail_rows = await db["Live locations"].find({"userId": incident["userId"]}).sort("recordedAt", -1).limit(30).to_list(length=30)
    shaped["trail"] = [
        {
            "lat": ((r.get("snappedLocation") or {}).get("coordinates") or r["rawLocation"]["coordinates"])[1],
            "lng": ((r.get("snappedLocation") or {}).get("coordinates") or r["rawLocation"]["coordinates"])[0],
            "recordedAt": r["recordedAt"].isoformat() if hasattr(r.get("recordedAt"), "isoformat") else r.get("recordedAt"),
        }
        for r in reversed(trail_rows)
    ]

    officers = await db["officers"].find({"onDuty": True}, {"officerId": 1, "name": 1, "station": 1}).to_list(length=None)
    for o in officers:
        o["_id"] = str(o["_id"])
    shaped["availableOfficers"] = officers

    return {"success": True, "incident": shaped}


async def assign_officer_to_incident(incident_id: str, officer_id: str) -> dict:
    db = get_db()
    officer = await db["officers"].find_one({"officerId": officer_id})
    if not officer:
        raise HTTPException(status_code=404, detail="Officer not found")

    now = datetime.utcnow()
    incident = await db["incidents"].find_one_and_update(
        {"incidentId": incident_id},
        {"$set": {"assignedOfficerId": officer_id, "status": "responding", "respondedAt": now, "updatedAt": now}},
        return_document=True,
    )
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    shaped = await _shape_incident(incident, db)
    await sio.emit("incident:update", shaped, room="admin-room")
    return {"success": True, "incident": shaped}


async def update_incident_status(incident_id: str, ui_status: str, note: str | None, actor_id: str) -> dict:
    db = get_db()
    internal = FROM_UI_INCIDENT.get(ui_status.lower())
    if not internal:
        raise HTTPException(status_code=400, detail="status must be one of: pending, investigating, closed")

    now = datetime.utcnow()
    updates: dict = {"status": internal, "updatedAt": now, "lastUpdatedBy": actor_id}
    if internal == "resolved":
        updates["resolvedAt"] = now
    if note:
        updates["officerNote"] = note

    incident = await db["incidents"].find_one_and_update({"incidentId": incident_id}, {"$set": updates}, return_document=True)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    shaped = await _shape_incident(incident, db)
    await sio.emit("incident:update", shaped, room="admin-room")
    return {"success": True, "incident": shaped}


async def generate_efir_for_incident(incident_id: str, station_jurisdiction: str) -> dict:
    """Files an E-FIR against an existing incident (admin-side trigger)."""
    db = get_db()
    incident = await db["incidents"].find_one({"incidentId": incident_id})
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    if incident.get("efirId"):
        raise HTTPException(status_code=409, detail=f"An E-FIR already exists for this incident ({incident['efirId']})")

    user = await db["users"].find_one({"userId": incident["userId"]})
    efir = await generate_efir(incident, user, station_jurisdiction)

    await db["incidents"].update_one({"incidentId": incident_id}, {"$set": {"efirId": efir["efirId"], "updatedAt": datetime.utcnow()}})
    efir["_id"] = str(efir["_id"])

    await sio.emit("efir:new", {"efirId": efir["efirId"], "incidentId": incident_id}, room="admin-room")
    return {"success": True, "efir": efir}
