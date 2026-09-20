from datetime import datetime
from fastapi import HTTPException

from database.db import get_db
from utils.id_generator import next_sequential_id
from utils.geofence_check import find_geofences_containing
from models.geofence import GeofenceCreateRequest, GeofenceUpdateRequest


async def list_geofences() -> dict:
    db = get_db()
    geofences = await db["geofences"].find({"active": True}).to_list(length=None)
    for g in geofences:
        g["_id"] = str(g["_id"])
    return {"success": True, "geofences": geofences}


async def check_point(lat: float, lng: float) -> dict:
    hits = await find_geofences_containing(lat, lng)
    for h in hits:
        h["_id"] = str(h["_id"])
    return {"success": True, "insideGeofences": hits}


async def create_geofence(payload: GeofenceCreateRequest) -> dict:
    db = get_db()
    geofence_id = await next_sequential_id("geofences", "geofenceId", "GEO")
    now = datetime.utcnow()
    geofence = {
        "geofenceId": geofence_id,
        "name": payload.name,
        "type": payload.type,
        "description": payload.description,
        "severity": payload.severity,
        "district": payload.district,
        "alertMessage": payload.alertMessage,
        "area": {"type": "Polygon", "coordinates": payload.coordinates},
        "active": True,
        "createdAt": now,
        "updatedAt": now,
    }
    await db["geofences"].insert_one(geofence)
    geofence["_id"] = str(geofence["_id"])
    return {"success": True, "geofence": geofence}


async def update_geofence(geofence_id: str, payload: GeofenceUpdateRequest) -> dict:
    db = get_db()
    updates = {k: v for k, v in payload.model_dump(exclude_unset=True).items() if v is not None}
    updates["updatedAt"] = datetime.utcnow()

    geofence = await db["geofences"].find_one_and_update(
        {"geofenceId": geofence_id}, {"$set": updates}, return_document=True
    )
    if not geofence:
        raise HTTPException(status_code=404, detail="Geofence not found")
    geofence["_id"] = str(geofence["_id"])
    return {"success": True, "geofence": geofence}


async def delete_geofence(geofence_id: str) -> dict:
    db = get_db()
    await db["geofences"].delete_one({"geofenceId": geofence_id})
    return {"success": True, "message": "Geofence deleted"}
