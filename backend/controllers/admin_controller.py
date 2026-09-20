import os
from datetime import datetime, timedelta
from fastapi import HTTPException
from jose import jwt

from database.db import get_db
from controllers.auth_controller import verify_password
from models.admin import AdminLoginRequest


def sign_admin_token(admin: dict) -> str:
    payload = {
        "id": admin["adminId"],
        "role": "admin",
        "email": admin["email"],
        "exp": datetime.utcnow() + timedelta(hours=12),
    }
    return jwt.encode(payload, os.getenv("ADMIN_JWT_SECRET"), algorithm=os.getenv("JWT_ALGORITHM", "HS256"))


async def admin_login(payload: AdminLoginRequest) -> dict:
    db = get_db()
    admin = await db["admins"].find_one({"email": payload.email.lower()})
    if not admin or not verify_password(payload.password, admin["passwordHash"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = sign_admin_token(admin)
    return {
        "success": True,
        "token": token,
        "admin": {
            "adminId": admin["adminId"],
            "name": admin["name"],
            "role": admin["role"],
            "district": admin.get("district"),
        },
    }


async def dashboard_summary() -> dict:
    db = get_db()
    since = datetime.utcnow() - timedelta(minutes=15)  # active = pinged in last 15 min

    active_tourist_ids = await db["Live locations"].distinct("userId", {"recordedAt": {"$gte": since}})
    open_incidents = await db["incidents"].find({"status": {"$in": ["open", "acknowledged", "responding"]}}).sort(
        "createdAt", -1
    ).to_list(length=None)
    pending_sos = await db["sos_requests"].find({"status": {"$in": ["pending", "acknowledged"]}}).sort(
        "createdAt", -1
    ).to_list(length=None)
    active_trips = await db["trips"].count_documents({"status": "active"})

    for i in open_incidents:
        i["_id"] = str(i["_id"])
    for s in pending_sos:
        s["_id"] = str(s["_id"])

    return {
        "success": True,
        "summary": {
            "activeTourists": len(active_tourist_ids),
            "activeTrips": active_trips,
            "openIncidents": len(open_incidents),
            "pendingSOS": len(pending_sos),
        },
        "openIncidents": open_incidents,
        "pendingSOS": pending_sos,
    }
