"""
controllers/officer_controller.py
----------------------------------
Officer accounts: login, the roster the admin panel's "Assign to officer"
dropdowns read from, and duty/location status.
"""
import os
from datetime import datetime, timedelta

from fastapi import HTTPException
from jose import jwt

from database.db import get_db
from controllers.auth_controller import verify_password
from models.officer import OfficerLoginRequest


def sign_officer_token(officer: dict) -> str:
    payload = {
        "id": officer["officerId"],
        "role": "officer",
        "email": officer["email"],
        "exp": datetime.utcnow() + timedelta(hours=12),
    }
    return jwt.encode(payload, os.getenv("OFFICER_JWT_SECRET"), algorithm=os.getenv("JWT_ALGORITHM", "HS256"))


async def officer_login(payload: OfficerLoginRequest) -> dict:
    db = get_db()
    officer = await db["officers"].find_one({"email": payload.email.lower()})
    if not officer or not verify_password(payload.password, officer["passwordHash"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = sign_officer_token(officer)
    return {
        "success": True,
        "token": token,
        "officer": {
            "officerId": officer["officerId"],
            "name": officer["name"],
            "badgeNumber": officer.get("badgeNumber"),
            "station": officer.get("station"),
            "jurisdiction": officer.get("jurisdiction"),
        },
    }


async def list_officers(on_duty_only: bool = False) -> dict:
    db = get_db()
    query = {"onDuty": True} if on_duty_only else {}
    officers = await db["officers"].find(query, {"passwordHash": 0}).to_list(length=None)

    results = []
    for o in officers:
        o["_id"] = str(o["_id"])
        assigned = await db["incidents"].count_documents(
            {"assignedOfficerId": o["officerId"], "status": {"$in": ["acknowledged", "responding"]}}
        )
        o["activeAssignments"] = assigned
        results.append(o)

    return {"success": True, "count": len(results), "officers": results}


async def set_duty_status(officer_id: str, on_duty: bool) -> dict:
    db = get_db()
    officer = await db["officers"].find_one_and_update(
        {"officerId": officer_id},
        {"$set": {"onDuty": on_duty, "updatedAt": datetime.utcnow()}},
        return_document=True,
    )
    if not officer:
        raise HTTPException(status_code=404, detail="Officer not found")
    officer["_id"] = str(officer["_id"])
    officer.pop("passwordHash", None)
    return {"success": True, "officer": officer}


async def update_officer_location(officer_id: str, lat: float, lng: float) -> dict:
    db = get_db()
    officer = await db["officers"].find_one_and_update(
        {"officerId": officer_id},
        {"$set": {"currentLocation": {"type": "Point", "coordinates": [lng, lat]}, "updatedAt": datetime.utcnow()}},
        return_document=True,
    )
    if not officer:
        raise HTTPException(status_code=404, detail="Officer not found")
    return {"success": True, "location": {"lat": lat, "lng": lng}}
