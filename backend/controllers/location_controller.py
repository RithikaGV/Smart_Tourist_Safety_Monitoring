"""
controllers/location_controller.py
Core pipeline (mirrors the Node version's src/sockets/locationSocket.js):
  1. snap the raw GPS point to the nearest road (OSRM)
  2. check which geofences (if any) the point falls inside (shapely)
  3. persist a "Live locations" document
  4. auto-raise an incident + notification on restricted/tribal-sacred-site entry
  5. broadcast the update over Socket.io to the admin room + the user's own room
"""
from datetime import datetime
from fastapi import HTTPException

from database.db import get_db
from utils.id_generator import next_sequential_id
from utils.road_snap import snap_point_to_road, get_route
from utils.geofence_check import find_geofences_containing
from utils.socket_manager import sio

SEVERITY_RANK = {"low": 1, "medium": 2, "high": 3, "critical": 4}
RESTRICTED_TYPES = {"restricted", "tribal_sacred_site", "high_risk"}


async def ingest_location_ping(
    user_id: str,
    lat: float,
    lng: float,
    trip_id: str | None = None,
    speed_kmh: float | None = None,
    heading: float | None = None,
    accuracy_meters: float | None = None,
    battery_level: float | None = None,
    is_offline: bool = False,
) -> dict:
    db = get_db()

    snapped = await snap_point_to_road(lng, lat)
    geofence_hits = await find_geofences_containing(lat, lng)

    now = datetime.utcnow()
    doc = {
        "userId": user_id,
        "tripId": trip_id,
        "rawLocation": {"type": "Point", "coordinates": [lng, lat]},
        "snappedLocation": {"type": "Point", "coordinates": snapped["coordinates"]} if snapped else None,
        "speedKmh": speed_kmh,
        "heading": heading,
        "accuracyMeters": accuracy_meters,
        "batteryLevel": battery_level,
        "isOffline": bool(is_offline),
        "insideGeofenceIds": [g["geofenceId"] for g in geofence_hits],
        "recordedAt": now,
        "createdAt": now,
        "updatedAt": now,
    }
    insert_result = await db["Live locations"].insert_one(doc)
    doc["_id"] = str(insert_result.inserted_id)

    raised_incident = None
    restricted_hits = [g for g in geofence_hits if g["type"] in RESTRICTED_TYPES]

    if restricted_hits:
        worst = sorted(restricted_hits, key=lambda g: SEVERITY_RANK.get(g["severity"], 0), reverse=True)[0]

        incident_id = await next_sequential_id("incidents", "incidentId", "INC")
        raised_incident = {
            "incidentId": incident_id,
            "userId": user_id,
            "tripId": trip_id,
            "type": "geofence_breach",
            "severity": worst["severity"],
            "status": "open",
            "location": {"type": "Point", "coordinates": [lng, lat]},
            "description": f"Entered geofence \"{worst['name']}\" ({worst['type']}). {worst.get('alertMessage', '')}",
            "assignedOfficerId": None,
            "respondedAt": None,
            "resolvedAt": None,
            "efirId": None,
            "createdAt": now,
            "updatedAt": now,
        }
        await db["incidents"].insert_one(dict(raised_incident))

        await db["notifications"].insert_one(
            {
                "userId": user_id,
                "title": "Safety Alert",
                "message": worst.get("alertMessage") or f"You have entered a sensitive zone: {worst['name']}",
                "type": "geofence_alert",
                "read": False,
                "meta": {"geofenceId": worst["geofenceId"], "incidentId": incident_id},
                "createdAt": now,
                "updatedAt": now,
            }
        )

    payload = {
        "userId": user_id,
        "tripId": trip_id,
        "raw": {"lat": lat, "lng": lng},
        "snapped": (
            {"lat": snapped["coordinates"][1], "lng": snapped["coordinates"][0], "roadName": snapped["roadName"]}
            if snapped
            else None
        ),
        "speedKmh": speed_kmh,
        "heading": heading,
        "isOffline": bool(is_offline),
        "insideGeofences": [
            {"id": g["geofenceId"], "name": g["name"], "type": g["type"], "severity": g["severity"]} for g in geofence_hits
        ],
        "incidentRaised": raised_incident["incidentId"] if raised_incident else None,
        "recordedAt": now.isoformat(),
    }

    await sio.emit("location:update", payload, room="admin-room")
    await sio.emit("location:update", payload, room=f"user-{user_id}")
    if raised_incident:
        await sio.emit("incident:new", raised_incident, room="admin-room")

    for g in geofence_hits:
        g["_id"] = str(g["_id"])

    return {"location": doc, "geofenceHits": geofence_hits, "incident": raised_incident}


async def get_current_location(user_id: str) -> dict:
    db = get_db()
    last = await db["Live locations"].find_one({"userId": user_id}, sort=[("recordedAt", -1)])
    if not last:
        raise HTTPException(status_code=404, detail="No location data yet")
    last["_id"] = str(last["_id"])
    return {"success": True, "location": last}


async def get_location_history(user_id: str, limit: int = 100) -> dict:
    db = get_db()
    limit = min(limit, 500)
    cursor = db["Live locations"].find({"userId": user_id}).sort("recordedAt", -1).limit(limit)
    history = await cursor.to_list(length=limit)
    for h in history:
        h["_id"] = str(h["_id"])
    history.reverse()
    return {"success": True, "count": len(history), "history": history}


async def route_preview(from_lat: float, from_lng: float, to_lat: float, to_lng: float) -> dict:
    route = await get_route([{"lng": from_lng, "lat": from_lat}, {"lng": to_lng, "lat": to_lat}])
    if not route:
        raise HTTPException(status_code=502, detail="Routing service unavailable")
    return {"success": True, "route": route}


async def snap_debug(lat: float, lng: float) -> dict:
    snapped = await snap_point_to_road(lng, lat)
    hits = await find_geofences_containing(lat, lng)
    return {"success": True, "snapped": snapped, "insideGeofences": [g["name"] for g in hits]}
