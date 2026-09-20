from datetime import datetime
from bson import ObjectId
from fastapi import HTTPException
from database.db import get_db


async def list_notifications(user_id: str) -> dict:
    db = get_db()
    notifications = await db["notifications"].find({"userId": user_id}).sort("createdAt", -1).limit(50).to_list(length=50)
    for n in notifications:
        n["_id"] = str(n["_id"])
    return {"success": True, "notifications": notifications}


async def mark_read(user_id: str, notification_id: str) -> dict:
    db = get_db()
    try:
        oid = ObjectId(notification_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid notification id")

    notification = await db["notifications"].find_one_and_update(
        {"_id": oid, "userId": user_id}, {"$set": {"read": True, "updatedAt": datetime.utcnow()}}, return_document=True
    )
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    notification["_id"] = str(notification["_id"])
    return {"success": True, "notification": notification}
