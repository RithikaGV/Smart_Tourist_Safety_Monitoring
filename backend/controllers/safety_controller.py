from fastapi import HTTPException
from database.db import get_db
from utils.id_generator import next_sequential_id
from utils.safety_score import compute_safety_score


async def get_trip_safety(trip_id: str) -> dict:
    db = get_db()
    latest = await db["ai_safety"].find_one({"tripId": trip_id}, sort=[("generatedAt", -1)])
    if not latest:
        raise HTTPException(status_code=404, detail="No safety score yet for this trip")
    latest["_id"] = str(latest["_id"])
    return {"success": True, "safety": latest}


async def get_live_safety(user_id: str, lat: float, lng: float, trip_id: str | None = None) -> dict:
    score = await compute_safety_score(lat, lng)

    if trip_id:
        db = get_db()
        ai_safety_id = await next_sequential_id("ai_safety", "aiSafetyId", "AI")
        await db["ai_safety"].insert_one({"aiSafetyId": ai_safety_id, "tripId": trip_id, "userId": user_id, **score})

    return {"success": True, "safety": score}
