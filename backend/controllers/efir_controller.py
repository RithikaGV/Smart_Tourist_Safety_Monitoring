from fastapi import HTTPException
from database.db import get_db
from utils.efir_generator import generate_efir


async def generate_efir_for_incident(incident_id: str, station_jurisdiction: str) -> dict:
    db = get_db()
    incident = await db["incidents"].find_one({"incidentId": incident_id})
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    user = await db["users"].find_one({"userId": incident["userId"]})
    efir = await generate_efir(incident, user, station_jurisdiction)

    await db["incidents"].update_one({"incidentId": incident_id}, {"$set": {"efirId": efir["efirId"]}})

    efir["_id"] = str(efir["_id"])
    return {"success": True, "efir": efir}


async def list_efirs() -> dict:
    db = get_db()
    efirs = await db["efir"].find().sort("createdAt", -1).to_list(length=None)
    for e in efirs:
        e["_id"] = str(e["_id"])
    return {"success": True, "efirs": efirs}


async def get_efir(efir_id: str) -> dict:
    db = get_db()
    efir = await db["efir"].find_one({"efirId": efir_id})
    if not efir:
        raise HTTPException(status_code=404, detail="E-FIR not found")
    efir["_id"] = str(efir["_id"])
    return {"success": True, "efir": efir}
