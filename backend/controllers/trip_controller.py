"""
controllers/trip_controller.py
"""
from datetime import datetime
from fastapi import HTTPException

from database.db import get_db
from utils.id_generator import next_sequential_id
from utils.road_snap import get_route
from utils.safety_score import compute_safety_score
from models.trip import TripCreateRequest, TripUpdateRequest


async def create_trip(user_id: str, payload: TripCreateRequest) -> dict:
    db = get_db()
    trip_id = await next_sequential_id("trips", "tripId", "TRIP")

    planned_route = None
    if payload.originCoords:
        route = await get_route(
            [
                {"lng": payload.originCoords.lng, "lat": payload.originCoords.lat},
                {"lng": payload.destinationCoords.lng, "lat": payload.destinationCoords.lat},
            ]
        )
        if route:
            planned_route = {
                "distanceMeters": route["distanceMeters"],
                "durationSeconds": route["durationSeconds"],
                "geometry": route["geometry"],
            }

    now = datetime.utcnow()
    travel_date = datetime.fromisoformat(payload.travelDate)

    trip = {
        "tripId": trip_id,
        "userId": user_id,
        "destination": payload.destination,
        "destinationCoords": {
            "type": "Point",
            "coordinates": [payload.destinationCoords.lng, payload.destinationCoords.lat],
        },
        "travelDate": travel_date,
        "travelTime": payload.travelTime,
        "numberOfTravelers": payload.numberOfTravelers or 1,
        "travelType": payload.travelType or "Family",
        "status": "planned",
        "plannedRoute": planned_route,
        "startedAt": None,
        "endedAt": None,
        "shareTripEnabled": False,
        "sharedWithContacts": [],
        "createdAt": now,
        "updatedAt": now,
    }
    await db["trips"].insert_one(trip)

    # Seed an initial AI safety score for the destination
    score = await compute_safety_score(payload.destinationCoords.lat, payload.destinationCoords.lng, at=travel_date)
    ai_safety_id = await next_sequential_id("ai_safety", "aiSafetyId", "AI")
    await db["ai_safety"].insert_one(
        {"aiSafetyId": ai_safety_id, "tripId": trip_id, "userId": user_id, **score, "createdAt": now, "updatedAt": now}
    )

    trip["_id"] = str(trip.get("_id", ""))
    return {"success": True, "trip": trip, "safetyPreview": score}


async def list_my_trips(user_id: str) -> dict:
    db = get_db()
    trips = await db["trips"].find({"userId": user_id}).sort("travelDate", 1).to_list(length=None)
    for t in trips:
        t["_id"] = str(t["_id"])

    # Compare by calendar day (not exact time) so a trip scheduled for today still
    # shows under "upcoming" even if its stored travelDate is midnight and it's
    # currently later in the day.
    today_start = datetime.combine(datetime.utcnow().date(), datetime.min.time())
    upcoming = [t for t in trips if t["travelDate"] >= today_start and t["status"] != "cancelled"]
    past = [t for t in trips if t["travelDate"] < today_start or t["status"] == "completed"]
    return {"success": True, "upcoming": upcoming, "past": past}


async def get_trip(user_id: str, trip_id: str) -> dict:
    db = get_db()
    trip = await db["trips"].find_one({"tripId": trip_id, "userId": user_id})
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    trip["_id"] = str(trip["_id"])
    return {"success": True, "trip": trip}


async def update_trip(user_id: str, trip_id: str, payload: TripUpdateRequest) -> dict:
    db = get_db()
    updates = {k: v for k, v in payload.model_dump(exclude_unset=True).items() if v is not None}
    updates["updatedAt"] = datetime.utcnow()
    if "travelDate" in updates:
        updates["travelDate"] = datetime.fromisoformat(updates["travelDate"])

    result = await db["trips"].find_one_and_update(
        {"tripId": trip_id, "userId": user_id}, {"$set": updates}, return_document=True
    )
    if not result:
        raise HTTPException(status_code=404, detail="Trip not found")
    result["_id"] = str(result["_id"])
    return {"success": True, "trip": result}


async def delete_trip(user_id: str, trip_id: str) -> dict:
    db = get_db()
    result = await db["trips"].delete_one({"tripId": trip_id, "userId": user_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Trip not found")
    return {"success": True, "message": "Trip deleted"}


async def start_trip(user_id: str, trip_id: str) -> dict:
    db = get_db()
    now = datetime.utcnow()
    result = await db["trips"].find_one_and_update(
        {"tripId": trip_id, "userId": user_id},
        {"$set": {"status": "active", "startedAt": now, "updatedAt": now}},
        return_document=True,
    )
    if not result:
        raise HTTPException(status_code=404, detail="Trip not found")
    result["_id"] = str(result["_id"])
    return {"success": True, "trip": result}


async def end_trip(user_id: str, trip_id: str) -> dict:
    db = get_db()
    now = datetime.utcnow()
    result = await db["trips"].find_one_and_update(
        {"tripId": trip_id, "userId": user_id},
        {"$set": {"status": "completed", "endedAt": now, "updatedAt": now}},
        return_document=True,
    )
    if not result:
        raise HTTPException(status_code=404, detail="Trip not found")
    result["_id"] = str(result["_id"])
    return {"success": True, "trip": result}
