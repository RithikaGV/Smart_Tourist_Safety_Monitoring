"""
seed/seed.py
Populates SmartTouristDB with Nilgiri district geofences, emergency contacts,
and demo accounts. Run from the backend/ directory:

    python -m seed.seed
"""
import asyncio
import sys
import os
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv

load_dotenv()

from database.db import connect_db, close_db
from utils.id_generator import next_sequential_id
from controllers.auth_controller import hash_password
from blockchain.chain import issue_blockchain_id


def box_around(center: list[float], delta: float) -> list[list[list[float]]]:
    lng, lat = center
    return [
        [
            [lng - delta, lat - delta],
            [lng + delta, lat - delta],
            [lng + delta, lat + delta],
            [lng - delta, lat + delta],
            [lng - delta, lat - delta],  # close the ring
        ]
    ]


GEOFENCE_DEFS = [
    {
        "name": "Mudumalai Tiger Reserve Core Zone",
        "type": "wildlife_zone",
        "severity": "high",
        "center": [76.5341, 11.5661],
        "delta": 0.06,
        "alertMessage": "You are entering the Mudumalai core wildlife zone. Stay on designated safari routes only.",
    },
    {
        "name": "Toda Sacred Grove - Muthunad",
        "type": "tribal_sacred_site",
        "severity": "medium",
        "center": [76.6800, 11.4300],
        "delta": 0.015,
        "alertMessage": "This is a Toda tribal sacred site. Please be respectful; entry may require local permission.",
    },
    {
        "name": "Kotagiri Restricted Estate Zone",
        "type": "restricted",
        "severity": "medium",
        "center": [76.8664, 11.4256],
        "delta": 0.02,
        "alertMessage": "Private tea estate land - restricted for tourists without prior permission.",
    },
    {
        "name": "Pykara Falls High-Risk Slope",
        "type": "high_risk",
        "severity": "critical",
        "center": [76.6270, 11.4923],
        "delta": 0.01,
        "alertMessage": "Steep, slippery terrain near the falls - multiple past accidents reported. Extreme caution advised.",
    },
    {
        "name": "Ooty Town Safe Zone",
        "type": "safe_zone",
        "severity": "low",
        "center": [76.6932, 11.4064],
        "delta": 0.03,
        "alertMessage": "You are in a monitored safe zone.",
    },
]


async def seed():
    db = connect_db()
    print("[seed] connected, wiping demo collections...")

    await db["geofences"].delete_many({})
    await db["emergency_contacts"].delete_many({})

    # ---------- Geofences ----------
    for g in GEOFENCE_DEFS:
        geofence_id = await next_sequential_id("geofences", "geofenceId", "GEO")
        now = datetime.utcnow()
        await db["geofences"].insert_one(
            {
                "geofenceId": geofence_id,
                "name": g["name"],
                "type": g["type"],
                "severity": g["severity"],
                "district": "Nilgiris",
                "alertMessage": g["alertMessage"],
                "area": {"type": "Polygon", "coordinates": box_around(g["center"], g["delta"])},
                "active": True,
                "createdAt": now,
                "updatedAt": now,
            }
        )
    print(f"[seed] created {len(GEOFENCE_DEFS)} geofences")

    # ---------- Emergency helplines ----------
    await db["emergency_contacts"].insert_many(
        [
            {"category": "helpline", "name": "Police", "phone": "100"},
            {"category": "helpline", "name": "Ambulance", "phone": "108"},
            {"category": "helpline", "name": "Fire Department", "phone": "101"},
            {"category": "helpline", "name": "Women's Helpline", "phone": "1091"},
            {"category": "helpline", "name": "Disaster Management", "phone": "1078"},
        ]
    )

    # ---------- Emergency facilities ----------
    await db["emergency_contacts"].insert_many(
        [
            {
                "category": "facility",
                "name": "Ooty Town Police Station",
                "facilityType": "police_station",
                "phone": "0423-2443345",
                "district": "Nilgiris",
                "location": {"type": "Point", "coordinates": [76.6932, 11.4064]},
                "address": "Commercial Road, Ooty",
            },
            {
                "category": "facility",
                "name": "Coonoor Police Station",
                "facilityType": "police_station",
                "phone": "0423-2230033",
                "district": "Nilgiris",
                "location": {"type": "Point", "coordinates": [76.7959, 11.3530]},
                "address": "Coonoor",
            },
            {
                "category": "facility",
                "name": "Government Headquarters Hospital, Ooty",
                "facilityType": "hospital",
                "phone": "0423-2443212",
                "district": "Nilgiris",
                "location": {"type": "Point", "coordinates": [76.6950, 11.4102]},
                "address": "Hospital Road, Ooty",
            },
            {
                "category": "facility",
                "name": "Coonoor Government Hospital",
                "facilityType": "hospital",
                "phone": "0423-2231050",
                "district": "Nilgiris",
                "location": {"type": "Point", "coordinates": [76.7965, 11.3505]},
                "address": "Coonoor",
            },
            {
                "category": "facility",
                "name": "Ooty Fire & Rescue Station",
                "facilityType": "fire_station",
                "phone": "0423-2442401",
                "district": "Nilgiris",
                "location": {"type": "Point", "coordinates": [76.6910, 11.4090]},
                "address": "Ooty",
            },
            {
                "category": "facility",
                "name": "Nilgiris District Pharmacy",
                "facilityType": "pharmacy",
                "phone": "0423-2442222",
                "district": "Nilgiris",
                "location": {"type": "Point", "coordinates": [76.6940, 11.4070]},
                "address": "Ooty Main Bazaar",
            },
            {
                "category": "facility",
                "name": "Tourist Help Center - Ooty",
                "facilityType": "tourist_help_center",
                "phone": "0423-2443977",
                "district": "Nilgiris",
                "location": {"type": "Point", "coordinates": [76.6945, 11.4110]},
                "address": "Charing Cross, Ooty",
            },
        ]
    )
    print("[seed] created emergency helplines + facilities")

    # ---------- Demo admin ----------
    if not await db["admins"].find_one({"email": "admin@safetour.gov.in"}):
        admin_id = await next_sequential_id("admins", "adminId", "ADM")
        await db["admins"].insert_one(
            {
                "adminId": admin_id,
                "name": "Nilgiris Command Center Admin",
                "email": "admin@safetour.gov.in",
                "passwordHash": hash_password("Admin@123"),
                "role": "district_admin",
                "district": "Nilgiris",
                "isActive": True,
                "createdAt": datetime.utcnow(),
            }
        )
        print("[seed] demo admin -> admin@safetour.gov.in / Admin@123")

    # ---------- Demo officer ----------
    if not await db["officers"].find_one({"email": "officer@safetour.gov.in"}):
        officer_id = await next_sequential_id("officers", "officerId", "OFF")
        await db["officers"].insert_one(
            {
                "officerId": officer_id,
                "name": "Head Constable R. Selvam",
                "badgeNumber": "TN-NLG-0142",
                "email": "officer@safetour.gov.in",
                "passwordHash": hash_password("Officer@123"),
                "phone": "9876543210",
                "station": "Ooty Town Police Station",
                "jurisdiction": "Nilgiris",
                "currentLocation": {"type": "Point", "coordinates": [76.6932, 11.4064]},
                "onDuty": True,
                "createdAt": datetime.utcnow(),
            }
        )
        print("[seed] demo officer -> officer@safetour.gov.in / Officer@123")

    # ---------- Demo tourist (mirrors "Rithika GV" from the walkthrough) ----------
    if not await db["users"].find_one({"email": "rithikagv2006@gmail.com"}):
        user_id = await next_sequential_id("users", "userId", "USER")
        now = datetime.utcnow()
        await db["users"].insert_one(
            {
                "userId": user_id,
                "fullName": "Rithika GV",
                "email": "rithikagv2006@gmail.com",
                "mobileNumber": "9080135463",
                "passwordHash": hash_password("Password@123"),
                "dateOfBirth": datetime(2006, 5, 12),
                "gender": "Female",
                "nationality": "Indian",
                "preferredLanguage": "English",
                "blockchainId": None,
                "kycStatus": "pending",
                "emergencyContacts": [],
                "isActive": True,
                "createdAt": now,
                "updatedAt": now,
            }
        )
        block = await issue_blockchain_id(user_id=user_id, kyc_payload={"userId": user_id, "seedDemo": True})
        await db["users"].update_one({"userId": user_id}, {"$set": {"blockchainId": block["blockchainId"]}})
        print(f"[seed] demo tourist -> rithikagv2006@gmail.com / Password@123 (blockchainId: {block['blockchainId']})")

    print("[seed] done.")
    await close_db()


if __name__ == "__main__":
    asyncio.run(seed())
