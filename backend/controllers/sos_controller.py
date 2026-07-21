from datetime import datetime
from fastapi import HTTPException

from database.db import get_db
from utils.id_generator import next_sequential_id
from utils.socket_manager import sio
from models.sos_request import SOSCreateRequest


async def create_sos(user_id: str, payload: SOSCreateRequest) -> dict:
    db = get_db()
    now = datetime.utcnow()

    sos_id = await next_sequential_id("sos_requests", "sosId", "SOS")
    incident_id = await next_sequential_id("incidents", "incidentId", "INC")

    incident = {
        "incidentId": incident_id,
        "userId": user_id,
        "tripId": payload.tripId,
        "type": "sos",
        "severity": "critical",
        "status": "open",
        "location": {"type": "Point", "coordinates": [payload.lng, payload.lat]},
        "description": "Tourist triggered SOS.",
        "assignedOfficerId": None,
        "respondedAt": None,
        "resolvedAt": None,
        "efirId": None,
        "createdAt": now,
        "updatedAt": now,
    }
    await db["incidents"].insert_one(dict(incident))

    sos = {
        "sosId": sos_id,
        "userId": user_id,
        "tripId": payload.tripId,
        "location": {"type": "Point", "coordinates": [payload.lng, payload.lat]},
        "triggerMethod": payload.triggerMethod,
        "batteryLevel": payload.batteryLevel,
        "isOffline": bool(payload.isOffline),
        "relayedBy": payload.relayedBy or [],
        "status": "pending",
        "incidentId": incident_id,
        "acknowledgedBy": None,
        "resolvedAt": None,
        "createdAt": now,
        "updatedAt": now,
    }
    await db["sos_requests"].insert_one(dict(sos))

    await sio.emit("sos:new", {"sos": sos, "incident": incident}, room="admin-room")

    return {"success": True, "sos": sos, "incident": incident}


async def my_sos(user_id: str) -> dict:
    db = get_db()
    sos_list = await db["sos_requests"].find({"userId": user_id}).sort("createdAt", -1).to_list(length=None)
    for s in sos_list:
        s["_id"] = str(s["_id"])
    return {"success": True, "sosList": sos_list}


async def list_sos(status: str | None = None) -> dict:
    db = get_db()
    filt = {"status": status} if status else {}
    sos_list = await db["sos_requests"].find(filt).sort("createdAt", -1).to_list(length=None)
    for s in sos_list:
        s["_id"] = str(s["_id"])
    return {"success": True, "sosList": sos_list}


async def acknowledge_sos(sos_id: str, officer_id: str) -> dict:
    db = get_db()
    sos = await db["sos_requests"].find_one_and_update(
        {"sosId": sos_id},
        {"$set": {"status": "acknowledged", "acknowledgedBy": officer_id, "updatedAt": datetime.utcnow()}},
        return_document=True,
    )
    if not sos:
        raise HTTPException(status_code=404, detail="SOS not found")
    sos["_id"] = str(sos["_id"])

    await sio.emit("sos:update", sos, room="admin-room")
    await sio.emit("sos:update", sos, room=f"user-{sos['userId']}")
    return {"success": True, "sos": sos}


async def resolve_sos(sos_id: str) -> dict:
    db = get_db()
    now = datetime.utcnow()
    sos = await db["sos_requests"].find_one_and_update(
        {"sosId": sos_id},
        {"$set": {"status": "resolved", "resolvedAt": now, "updatedAt": now}},
        return_document=True,
    )
    if not sos:
        raise HTTPException(status_code=404, detail="SOS not found")
    sos["_id"] = str(sos["_id"])

    await sio.emit("sos:update", sos, room="admin-room")
    await sio.emit("sos:update", sos, room=f"user-{sos['userId']}")
    return {"success": True, "sos": sos}
