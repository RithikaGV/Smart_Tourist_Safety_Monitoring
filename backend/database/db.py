"""
database/db.py
--------------
Async MongoDB connection (Motor). Import `get_db()` anywhere you need a
collection handle, e.g. `get_db()["users"]`.
"""
import os
from motor.motor_asyncio import AsyncIOMotorClient

_client: AsyncIOMotorClient | None = None
_db = None


def connect_db():
    global _client, _db
    uri = os.getenv("MONGO_URI", "mongodb://127.0.0.1:27017")
    db_name = os.getenv("MONGO_DB_NAME", "SmartTouristDB")

    _client = AsyncIOMotorClient(uri)
    _db = _client[db_name]
    print(f"[db] MongoDB client created -> db='{db_name}'")
    return _db


def get_db():
    if _db is None:
        raise RuntimeError("Database not initialized yet - call connect_db() first (done in app.py startup).")
    return _db


async def close_db():
    global _client
    if _client:
        _client.close()
        print("[db] MongoDB connection closed")


async def ensure_indexes():
    """Creates the geospatial + uniqueness indexes each collection needs."""
    db = get_db()

    await db["users"].create_index("email", unique=True)
    await db["users"].create_index("userId", unique=True)
    await db["users"].create_index("blockchainId", unique=True, sparse=True)

    await db["admins"].create_index("email", unique=True)
    await db["admins"].create_index("adminId", unique=True)

    await db["officers"].create_index("email", unique=True)
    await db["officers"].create_index("officerId", unique=True)
    await db["officers"].create_index("currentLocation", "2dsphere")

    await db["trips"].create_index("tripId", unique=True)
    await db["trips"].create_index("userId")

    await db["kyc"].create_index("kycId", unique=True)
    await db["kyc"].create_index("userId")

    await db["blockchain_ids"].create_index("blockchainId", unique=True)
    await db["blockchain_ids"].create_index("userId")
    await db["blockchain_ids"].create_index("createdAt")

    await db["geofences"].create_index("geofenceId", unique=True)
    await db["geofences"].create_index([("area", "2dsphere")])

    await db["incidents"].create_index("incidentId", unique=True)
    await db["incidents"].create_index([("location", "2dsphere")])
    await db["incidents"].create_index("userId")

    await db["efir"].create_index("efirId", unique=True)
    await db["efir"].create_index("incidentId")

    await db["sos_requests"].create_index("sosId", unique=True)
    await db["sos_requests"].create_index([("location", "2dsphere")])
    await db["sos_requests"].create_index("userId")

    await db["emergency_contacts"].create_index([("location", "2dsphere")], sparse=True)

    await db["notifications"].create_index("userId")

    await db["ai_safety"].create_index("aiSafetyId", unique=True)
    await db["ai_safety"].create_index("tripId")

    await db["Live locations"].create_index([("rawLocation", "2dsphere")])
    await db["Live locations"].create_index([("userId", 1), ("recordedAt", -1)])
    await db["Live locations"].create_index("recordedAt", expireAfterSeconds=60 * 60 * 24 * 7)

    print("[db] indexes ensured")
