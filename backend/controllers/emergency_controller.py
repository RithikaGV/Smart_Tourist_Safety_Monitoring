from fastapi import HTTPException
from database.db import get_db


async def list_helplines() -> dict:
    db = get_db()
    helplines = await db["emergency_contacts"].find({"category": "helpline"}).to_list(length=None)
    for h in helplines:
        h["_id"] = str(h["_id"])
    return {"success": True, "helplines": helplines}


async def nearby_facilities(facility_type: str, lat: float, lng: float, radius_km: float = 15) -> dict:
    if not facility_type:
        raise HTTPException(status_code=400, detail="type is required")

    db = get_db()
    cursor = db["emergency_contacts"].find(
        {
            "category": "facility",
            "facilityType": facility_type,
            "location": {
                "$near": {
                    "$geometry": {"type": "Point", "coordinates": [lng, lat]},
                    "$maxDistance": radius_km * 1000,
                }
            },
        }
    )
    facilities = await cursor.to_list(length=None)
    for f in facilities:
        f["_id"] = str(f["_id"])
    return {"success": True, "facilities": facilities}
