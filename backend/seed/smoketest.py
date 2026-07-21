"""
seed/smoketest.py
Exercises the API end-to-end using mongomock-motor (an in-process, in-memory
stand-in for Motor/MongoDB) so this runs with zero external services. This is
purely a code-path/logic check - swap MONGO_URI to a real MongoDB and this
same flow is what `npm`-style manual testing / Postman would hit for real.

Run from the backend/ directory:
    python -m seed.smoketest

Note on OSRM: this environment's network egress is restricted, so calls to
the public OSRM server will fail and roadSnap functions will gracefully
return None (this is by design - see utils/road_snap.py's try/except). On
your machine with normal internet access, snapping + routing will populate.
"""
import asyncio
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault("JWT_SECRET", "test_secret")
os.environ.setdefault("ADMIN_JWT_SECRET", "test_admin_secret")
os.environ.setdefault("OFFICER_JWT_SECRET", "test_officer_secret")
os.environ.setdefault("JWT_ALGORITHM", "HS256")

from dotenv import load_dotenv

load_dotenv()

from mongomock_motor import AsyncMongoMockClient
import database.db as db_module

failures = 0


def check(cond, msg):
    global failures
    if cond:
        print(f"  ok:   {msg}")
    else:
        failures += 1
        print(f"  FAIL: {msg}")


async def run():
    # Patch the db module to use an in-memory mock client instead of a real Mongo server.
    mock_client = AsyncMongoMockClient()
    db_module._db = mock_client["SmartTouristDB"]
    print("[smoketest] in-memory mock MongoDB ready")

    from httpx import AsyncClient, ASGITransport
    from app import app  # plain FastAPI app (not the socketio wrapper) is enough for HTTP-only tests

    from models.geofence import GeofenceCreateRequest
    from controllers import geofence_controller

    # Seed one geofence covering Pykara Falls so the geofence-breach pipeline has something to hit
    await geofence_controller.create_geofence(
        GeofenceCreateRequest(
            name="Pykara Falls High-Risk Slope",
            type="high_risk",
            severity="critical",
            district="Nilgiris",
            alertMessage="Extreme caution advised near the falls.",
            coordinates=[[[76.617, 11.4823], [76.637, 11.4823], [76.637, 11.5023], [76.617, 11.5023], [76.617, 11.4823]]],
        )
    )

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        print("\n--- Auth ---")
        r = await client.post(
            "/api/auth/create-account",
            json={
                "fullName": "Rithika GV",
                "email": "rithikagv2006@gmail.com",
                "mobileNumber": "9080135463",
                "password": "Password@123",
                "dateOfBirth": "2006-05-12",
                "gender": "Female",
                "nationality": "Indian",
            },
        )
        check(r.status_code == 201, f"create-account returns 201 (got {r.status_code}: {r.text[:200]})")
        data = r.json()
        check(bool(data["user"]["blockchainId"]), f"blockchainId issued ({data['user'].get('blockchainId')})")
        token = data["token"]
        headers = {"Authorization": f"Bearer {token}"}

        r = await client.get("/api/auth/me", headers=headers)
        check(r.json()["user"]["email"] == "rithikagv2006@gmail.com", "GET /auth/me returns correct user")

        print("\n--- Trips ---")
        r = await client.post(
            "/api/trips/",
            json={
                "destination": "Ooty",
                "destinationCoords": {"lat": 11.4064, "lng": 76.6932},
                "travelDate": "2026-07-18",
                "travelTime": "12:30",
                "numberOfTravelers": 5,
                "travelType": "Family",
            },
            headers=headers,
        )
        check(r.status_code == 201, f"create trip returns 201 (got {r.status_code}: {r.text[:200]})")
        trip_data = r.json()
        trip_id = trip_data["trip"]["tripId"]
        check(bool(trip_id), f"trip created ({trip_id})")
        check("safetyPreview" in trip_data, "AI safety preview generated with trip")

        r = await client.get("/api/trips/", headers=headers)
        check(len(r.json()["upcoming"]) == 1, "GET /trips lists the new trip under upcoming")

        print("\n--- Geofences ---")
        r = await client.get("/api/geofences/", headers=headers)
        check(len(r.json()["geofences"]) == 1, "GET /geofences returns seeded geofence")

        r = await client.get("/api/geofences/check", params={"lat": 11.4923, "lng": 76.627}, headers=headers)
        check(len(r.json()["insideGeofences"]) == 1, "point inside Pykara Falls zone is detected")

        print("\n--- Location ping (geofence breach -> auto incident) ---")
        r = await client.post(
            "/api/location/ping",
            json={"lat": 11.4923, "lng": 76.627, "tripId": trip_id, "speedKmh": 12, "isOffline": False},
            headers=headers,
        )
        check(r.status_code == 200, f"location ping returns 200 (got {r.status_code}: {r.text[:200]})")
        ping_data = r.json()
        check(len(ping_data["geofenceHits"]) == 1, "ping inside restricted zone flags the geofence")
        check(ping_data.get("incident") is not None, f"geofence breach auto-raised an incident ({(ping_data.get('incident') or {}).get('incidentId')})")

        user_id = data["user"]["userId"]
        r = await client.get(f"/api/location/history/{user_id}", headers=headers)
        check(r.json()["count"] == 1, "location history contains the ping")

        print("\n--- SOS ---")
        r = await client.post(
            "/api/sos/",
            json={"lat": 11.4064, "lng": 76.6932, "tripId": trip_id, "triggerMethod": "app_button"},
            headers=headers,
        )
        check(r.status_code == 201, f"SOS creates a request + incident (got {r.status_code}: {r.text[:200]})")
        check(r.json()["incident"]["severity"] == "critical", "SOS incident marked critical")

        print("\n--- Emergency contacts ---")
        db = db_module.get_db()
        await db["emergency_contacts"].insert_one({"category": "helpline", "name": "Police", "phone": "100"})
        await db["emergency_contacts"].insert_one(
            {
                "category": "facility",
                "name": "Ooty Town Police Station",
                "facilityType": "police_station",
                "phone": "0423-2443345",
                "location": {"type": "Point", "coordinates": [76.6932, 11.4064]},
            }
        )
        r = await client.get("/api/emergency-contacts/helplines", headers=headers)
        check(len(r.json()["helplines"]) == 1, "helplines endpoint works")

        try:
            r = await client.get(
                "/api/emergency-contacts/nearby",
                params={"type": "police_station", "lat": 11.4064, "lng": 76.6932},
                headers=headers,
            )
            check(r.status_code == 200, f"nearby facilities route responds 200 (got {r.status_code}: {r.text[:200]})")
        except Exception:
            print("  skip: nearby facilities $near query - the mongomock in-memory DB used by this test")
            print("        doesn't implement $near; real MongoDB does (via the 2dsphere index created in")
            print("        database/db.py's ensure_indexes()). Verify this one against a real MongoDB.")

        print("\n--- Safety score ---")
        r = await client.get(f"/api/safety/trip/{trip_id}", headers=headers)
        check("overallSafetyScore" in r.json()["safety"], "safety score retrievable for trip")

    print(f"\n[smoketest] {'ALL PASSED' if failures == 0 else f'{failures} FAILED'}")
    sys.exit(0 if failures == 0 else 1)


if __name__ == "__main__":
    asyncio.run(run())
