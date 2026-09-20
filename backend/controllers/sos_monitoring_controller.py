"""
controllers/sos_monitoring_controller.py
-----------------------------------------
Backs the admin panel's "SOS Monitoring" screen:
  - the filterable table (time / location / status) with SOS-2026-1001 style refs
  - the detail view with the tourist's live position + recent trail
  - "Accept / Assign Officer" and the Pending/Investigating/Closed buttons
"""
from datetime import datetime, timedelta

from fastapi import HTTPException

from database.db import get_db
from utils.socket_manager import sio
from utils.status_map import to_ui_status, to_priority, FROM_UI_SOS

TIME_FILTERS = {
    "all": None,
    "1h": 60,
    "24h": 1440,
    "7d": 10080,
    "30d": 43200,
}


def _sos_reference(sos: dict) -> str:
    """Renders SOS001 as the SOS-2026-1001 style reference shown in the UI."""
    created = sos.get("createdAt")
    year = created.year if hasattr(created, "year") else datetime.utcnow().year
    digits = "".join(ch for ch in sos["sosId"] if ch.isdigit()) or "0"
    return f"SOS-{year}-{1000 + int(digits)}"


async def _shape_sos(sos: dict, db) -> dict:
    user = await db["users"].find_one(
        {"userId": sos["userId"]}, {"fullName": 1, "mobileNumber": 1, "nationality": 1, "blockchainId": 1}
    )
    coords = sos["location"]["coordinates"]
    incident = None
    if sos.get("incidentId"):
        incident = await db["incidents"].find_one({"incidentId": sos["incidentId"]}, {"severity": 1, "category": 1})

    severity = (incident or {}).get("severity", "high")

    return {
        "sosId": sos["sosId"],
        "reference": _sos_reference(sos),
        "userId": sos["userId"],
        "tourist": {
            "name": (user or {}).get("fullName", sos["userId"]),
            "phone": (user or {}).get("mobileNumber"),
            "nationality": (user or {}).get("nationality"),
            "blockchainId": (user or {}).get("blockchainId"),
        },
        "location": {"lat": coords[1], "lng": coords[0], "name": sos.get("locationName")},
        "time": sos["createdAt"].isoformat() if hasattr(sos.get("createdAt"), "isoformat") else sos.get("createdAt"),
        "priority": to_priority(severity),
        "status": sos["status"],
        "uiStatus": to_ui_status(sos["status"]),
        "triggerMethod": sos.get("triggerMethod"),
        "isOffline": sos.get("isOffline", False),
        "assignedOfficerId": sos.get("assignedOfficerId"),
        "incidentId": sos.get("incidentId"),
        "tripId": sos.get("tripId"),
    }


async def list_sos_monitoring(
    time_filter: str = "all",
    ui_status: str | None = None,
    location: str | None = None,
    limit: int = 200,
) -> dict:
    db = get_db()
    query: dict = {}

    minutes = TIME_FILTERS.get(time_filter)
    if minutes:
        query["createdAt"] = {"$gte": datetime.utcnow() - timedelta(minutes=minutes)}

    if ui_status and ui_status.lower() != "all":
        internal = FROM_UI_SOS.get(ui_status.lower())
        if internal == "pending":
            query["status"] = "pending"
        elif internal == "dispatched":
            query["status"] = {"$in": ["acknowledged", "dispatched"]}
        elif internal == "resolved":
            query["status"] = {"$in": ["resolved", "cancelled"]}

    if location and location.lower() not in ("all", "all locations"):
        query["locationName"] = {"$regex": location, "$options": "i"}

    rows = await db["sos_requests"].find(query).sort("createdAt", -1).limit(limit).to_list(length=limit)
    shaped = [await _shape_sos(s, db) for s in rows]

    return {"success": True, "count": len(shaped), "requests": shaped}


async def sos_detail(sos_id: str) -> dict:
    db = get_db()
    sos = await db["sos_requests"].find_one({"sosId": sos_id})
    if not sos:
        raise HTTPException(status_code=404, detail="SOS request not found")

    shaped = await _shape_sos(sos, db)

    # Recent movement trail, so the officer can see where the tourist came from.
    trail_rows = await db["Live locations"].find({"userId": sos["userId"]}).sort("recordedAt", -1).limit(30).to_list(length=30)
    trail = []
    for row in reversed(trail_rows):
        coords = (row.get("snappedLocation") or {}).get("coordinates") or row["rawLocation"]["coordinates"]
        trail.append(
            {
                "lat": coords[1],
                "lng": coords[0],
                "recordedAt": row["recordedAt"].isoformat() if hasattr(row.get("recordedAt"), "isoformat") else row.get("recordedAt"),
            }
        )

    officers = await db["officers"].find({"onDuty": True}, {"officerId": 1, "name": 1, "station": 1}).to_list(length=None)
    for o in officers:
        o["_id"] = str(o["_id"])

    shaped["trail"] = trail
    shaped["availableOfficers"] = officers
    return {"success": True, "request": shaped}


async def assign_officer(sos_id: str, officer_id: str, admin_id: str) -> dict:
    db = get_db()
    officer = await db["officers"].find_one({"officerId": officer_id})
    if not officer:
        raise HTTPException(status_code=404, detail="Officer not found")

    now = datetime.utcnow()
    sos = await db["sos_requests"].find_one_and_update(
        {"sosId": sos_id},
        {"$set": {"assignedOfficerId": officer_id, "status": "dispatched", "acknowledgedBy": admin_id, "updatedAt": now}},
        return_document=True,
    )
    if not sos:
        raise HTTPException(status_code=404, detail="SOS request not found")

    # Keep the linked incident in step, so both screens agree.
    if sos.get("incidentId"):
        await db["incidents"].update_one(
            {"incidentId": sos["incidentId"]},
            {"$set": {"assignedOfficerId": officer_id, "status": "responding", "respondedAt": now, "updatedAt": now}},
        )

    await db["officers"].update_one({"officerId": officer_id}, {"$addToSet": {"assignedSosIds": sos_id}})

    payload = await _shape_sos(sos, db)
    await sio.emit("sos:update", payload, room="admin-room")
    await sio.emit("sos:update", payload, room=f"user-{sos['userId']}")

    await db["notifications"].insert_one(
        {
            "userId": sos["userId"],
            "title": "Help is on the way",
            "message": f"{officer['name']} from {officer.get('station', 'the nearest station')} has been dispatched to your location.",
            "type": "sos_update",
            "read": False,
            "meta": {"sosId": sos_id, "officerId": officer_id},
            "createdAt": now,
            "updatedAt": now,
        }
    )

    return {"success": True, "request": payload, "assignedTo": {"officerId": officer_id, "name": officer["name"]}}


async def update_sos_status(sos_id: str, ui_status: str, note: str | None, actor_id: str) -> dict:
    db = get_db()
    internal = FROM_UI_SOS.get(ui_status.lower())
    if not internal:
        raise HTTPException(status_code=400, detail="status must be one of: pending, investigating, closed")

    now = datetime.utcnow()
    updates: dict = {"status": internal, "updatedAt": now}
    if internal == "resolved":
        updates["resolvedAt"] = now
    if note:
        updates["officerNote"] = note

    sos = await db["sos_requests"].find_one_and_update({"sosId": sos_id}, {"$set": updates}, return_document=True)
    if not sos:
        raise HTTPException(status_code=404, detail="SOS request not found")

    if sos.get("incidentId"):
        incident_status = {"pending": "open", "dispatched": "responding", "resolved": "resolved"}[internal]
        incident_updates = {"status": incident_status, "updatedAt": now}
        if incident_status == "resolved":
            incident_updates["resolvedAt"] = now
        await db["incidents"].update_one({"incidentId": sos["incidentId"]}, {"$set": incident_updates})

    payload = await _shape_sos(sos, db)
    await sio.emit("sos:update", payload, room="admin-room")
    await sio.emit("sos:update", payload, room=f"user-{sos['userId']}")

    return {"success": True, "request": payload}
