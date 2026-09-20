"""
seed/smoketest_admin.py
------------------------
End-to-end check of every ADMIN PANEL endpoint, using mongomock-motor (an
in-process, in-memory stand-in for MongoDB) so it runs with zero external
services.

Covers: admin login -> dashboard cards -> incident stats -> zone creation with
instant alert -> heatmap/density -> SOS monitoring + assignment + status ->
AI analytics detection + dispatch -> E-FIR filing and copy-text rendering.

Run from the backend/ directory:
    python -m seed.smoketest_admin
"""
import asyncio
import os
import sys
from datetime import datetime, timedelta

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
    db_module._db = AsyncMongoMockClient()["SmartTouristDB"]
    db = db_module.get_db()
    print("[smoketest-admin] in-memory mock MongoDB ready\n")

    from httpx import AsyncClient, ASGITransport
    from app import app
    from controllers.auth_controller import hash_password
    from utils.id_generator import next_sequential_id

    now = datetime.utcnow()

    # --- seed an admin + officer directly (login paths are covered elsewhere) ---
    await db["admins"].insert_one(
        {
            "adminId": "ADM001",
            "name": "Nilgiris Command Center Admin",
            "email": "admin@safetour.gov.in",
            "passwordHash": hash_password("Admin@123"),
            "role": "district_admin",
            "district": "Nilgiris",
            "isActive": True,
            "createdAt": now,
        }
    )
    await db["officers"].insert_one(
        {
            "officerId": "OFF001",
            "name": "Head Constable R. Selvam",
            "badgeNumber": "TN-NLG-0142",
            "email": "officer@safetour.gov.in",
            "passwordHash": hash_password("Officer@123"),
            "station": "Ooty Town Police Station",
            "jurisdiction": "Nilgiris",
            "currentLocation": {"type": "Point", "coordinates": [76.6932, 11.4064]},
            "onDuty": True,
            "createdAt": now,
        }
    )

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test", timeout=30) as client:
        print("--- Admin login ---")
        r = await client.post("/api/admin/login", json={"email": "admin@safetour.gov.in", "password": "Admin@123"})
        check(r.status_code == 200, f"admin login returns 200 (got {r.status_code}: {r.text[:200]})")
        admin_token = r.json()["token"]
        H = {"Authorization": f"Bearer {admin_token}"}

        r = await client.post("/api/officer/login", json={"email": "officer@safetour.gov.in", "password": "Officer@123"})
        check(r.status_code == 200, "officer login returns 200")

        # --- create a tourist + trip + location pings so there's data to analyse ---
        print("\n--- Seeding a tourist with movement ---")
        r = await client.post(
            "/api/auth/create-account",
            json={
                "fullName": "Anita Desai",
                "email": "anita.desai@example.com",
                "mobileNumber": "9876543210",
                "password": "Password@123",
                "gender": "Female",
                "nationality": "Indian",
            },
        )
        check(r.status_code == 201, f"tourist signup (got {r.status_code})")
        tourist = r.json()
        user_id = tourist["user"]["userId"]
        TH = {"Authorization": f"Bearer {tourist['token']}"}

        r = await client.post(
            "/api/trips/",
            json={
                "destination": "Ooty",
                "destinationCoords": {"lat": 11.4064, "lng": 76.6932},
                "travelDate": datetime.utcnow().date().isoformat(),
                "numberOfTravelers": 2,
                "travelType": "Family",
            },
            headers=TH,
        )
        trip_id = r.json()["trip"]["tripId"]
        await client.post(f"/api/trips/{trip_id}/start", headers=TH)

        # Pings: several at the same spot so the inactivity detector has something real to find.
        for i in range(6):
            await db["Live locations"].insert_one(
                {
                    "userId": user_id,
                    "tripId": trip_id,
                    "rawLocation": {"type": "Point", "coordinates": [76.6932, 11.4064]},
                    "snappedLocation": {"type": "Point", "coordinates": [76.6932, 11.4064]},
                    "insideGeofenceIds": [],
                    "recordedAt": now - timedelta(minutes=120 - i * 20),
                    "createdAt": now,
                }
            )
        check(True, "seeded a stationary location trail for the tourist")

        # --- Dashboard ---
        print("\n--- Dashboard ---")
        r = await client.get("/api/admin/dashboard/overview", headers=H)
        check(r.status_code == 200, f"dashboard overview 200 (got {r.status_code}: {r.text[:200]})")
        cards = r.json()["cards"]
        check(cards["totalTourists"] == 1, f"totalTourists card counts the tourist (got {cards['totalTourists']})")

        r = await client.get("/api/admin/dashboard/incident-stats", headers=H)
        check(r.status_code == 200, "incident stats 200")
        cats = [s["category"] for s in r.json()["stats"]]
        check("theft" in cats and "harassment" in cats, "incident stats returns all UI categories")

        # --- Incidents (manual filing) ---
        print("\n--- Incidents ---")
        r = await client.post(
            "/api/admin/incidents",
            json={
                "userId": user_id,
                "category": "theft",
                "lat": 11.4131,
                "lng": 76.6961,
                "locationName": "Ooty - Botanical Gardens",
                "description": "Wallet reported stolen near the main gate.",
                "severity": "high",
            },
            headers=H,
        )
        check(r.status_code == 201, f"manual incident filed (got {r.status_code}: {r.text[:200]})")
        incident = r.json()["incident"]
        incident_id = incident["incidentId"]
        check(incident["priority"] == "high", "severity maps to High priority badge")
        check(incident["uiStatus"] == "pending", "new incident shows as Pending in the UI")

        r = await client.get("/api/admin/dashboard/incident-stats", headers=H)
        theft = next(s for s in r.json()["stats"] if s["category"] == "theft")
        check(theft["count"] == 1, "the new theft incident appears in the monthly stats chart")

        r = await client.post(f"/api/admin/incidents/{incident_id}/assign", json={"officerId": "OFF001"}, headers=H)
        check(r.status_code == 200 and r.json()["incident"]["uiStatus"] == "investigating",
              "assigning an officer moves the incident to Investigating")

        r = await client.patch(f"/api/admin/incidents/{incident_id}/status", json={"status": "closed"}, headers=H)
        check(r.json()["incident"]["uiStatus"] == "closed", "status button closes the incident")

        # --- E-FIR ---
        print("\n--- E-FIR ---")
        r = await client.post(
            f"/api/admin/incidents/{incident_id}/efir",
            json={"stationJurisdiction": "Ooty Town Police Station"},
            headers=H,
        )
        check(r.status_code == 201, f"E-FIR filed against the incident (got {r.status_code}: {r.text[:200]})")
        efir_id = r.json()["efir"]["efirId"]

        r = await client.get("/api/admin/efir", headers=H)
        check(r.json()["count"] == 1, "E-FIR appears in the monitoring table")
        row = r.json()["efirs"][0]
        check(row["firReference"].startswith("FIR-OT-"), f"FIR reference uses the station code ({row['firReference']})")
        check(row["categoryLabel"] == "Theft of Property", "FIR row shows the incident category label")

        r = await client.get(f"/api/admin/efir/{efir_id}", headers=H)
        check("FIRST INFORMATION REPORT" in r.json()["efir"]["copyText"], "'View & Copy FIR' returns paste-ready text")

        # --- Zone management ---
        print("\n--- Zone Management ---")
        r = await client.post(
            "/api/admin/zones",
            json={
                "name": "Doddabetta Slopes",
                "type": "landslide_area",
                "status": "active",
                "latitude": 11.4064,
                "longitude": 76.6932,
                "radiusMeters": 600,
                "severity": "high",
                "pushInstantAlert": True,
            },
            headers=H,
        )
        check(r.status_code == 201, f"zone created (got {r.status_code}: {r.text[:200]})")
        zone = r.json()["zone"]
        geofence_id = zone["geofenceId"]
        check(zone["radiusMeters"] == 600, "zone stores its radius for the UI table")
        check(r.json()["touristsAlerted"] == 1, f"instant alert reached the tourist inside the zone (got {r.json()['touristsAlerted']})")

        notif = await db["notifications"].find_one({"userId": user_id, "type": "geofence_alert"})
        check(notif is not None, "tourist received the zone alert notification")

        r = await client.get("/api/geofences/", headers=TH)
        check(any(g["geofenceId"] == geofence_id for g in r.json()["geofences"]),
              "admin-created zone is immediately live for the tourist app")

        r = await client.patch(f"/api/admin/zones/{geofence_id}", json={"status": "draft"}, headers=H)
        check(r.json()["zone"]["zoneStatus"] == "draft", "zone can be switched to Draft")

        r = await client.post(f"/api/admin/zones/{geofence_id}/alert", json={"message": "Fresh landslide warning."}, headers=H)
        check(r.status_code == 200, "per-zone Alert button works")

        # --- Heatmap ---
        print("\n--- Risk Heatmap ---")
        r = await client.get("/api/admin/heatmap", params={"timeRange": "24h"}, headers=H)
        check(r.status_code == 200, f"heatmap 200 (got {r.status_code}: {r.text[:200]})")
        body = r.json()
        check(len(body["spots"]) >= 1, "heatmap clusters the tourist into a spot")
        check(set(body["legend"].keys()) == {"safe", "crowded", "danger"}, "heatmap legend has the three risk buckets")

        r = await client.get("/api/admin/heatmap/density", params={"timeRange": "24h"}, headers=H)
        check(r.json()["density"][0]["band"] in ("GREEN", "YELLOW", "RED"), "density bars carry a colour band")

        r = await client.get("/api/admin/heatmap/live-positions", headers=H)
        check(r.status_code == 200, "live positions endpoint responds")

        # --- SOS monitoring ---
        print("\n--- SOS Monitoring ---")
        r = await client.post(
            "/api/sos/",
            json={"lat": 11.4131, "lng": 76.6961, "tripId": trip_id, "triggerMethod": "app_button"},
            headers=TH,
        )
        check(r.status_code == 201, "tourist triggers SOS")
        sos_id = r.json()["sos"]["sosId"]

        r = await client.get("/api/admin/sos", headers=H)
        check(r.json()["count"] == 1, "SOS appears in the monitoring table")
        sos_row = r.json()["requests"][0]
        check(sos_row["reference"].startswith("SOS-"), f"SOS reference rendered ({sos_row['reference']})")
        check(sos_row["tourist"]["name"] == "Anita Desai", "SOS row joins the tourist's name")
        check(sos_row["uiStatus"] == "pending", "new SOS shows as Pending")

        r = await client.get(f"/api/admin/sos/{sos_id}", headers=H)
        detail = r.json()["request"]
        check(len(detail["trail"]) > 0, "SOS detail includes the tourist's movement trail")
        check(len(detail["availableOfficers"]) == 1, "SOS detail lists assignable officers")

        r = await client.post(f"/api/admin/sos/{sos_id}/assign", json={"officerId": "OFF001"}, headers=H)
        check(r.json()["request"]["uiStatus"] == "investigating", "assigning an officer moves SOS to Investigating")

        notif = await db["notifications"].find_one({"userId": user_id, "type": "sos_update"})
        check(notif is not None, "tourist is notified that an officer was dispatched")

        r = await client.get("/api/admin/sos", params={"status": "investigating"}, headers=H)
        check(r.json()["count"] == 1, "status filter finds the investigating SOS")

        r = await client.patch(f"/api/admin/sos/{sos_id}/status", json={"status": "closed"}, headers=H)
        check(r.json()["request"]["uiStatus"] == "closed", "SOS can be closed")

        # --- AI analytics ---
        print("\n--- AI Analytics ---")
        r = await client.post("/api/admin/ai/analyze", params={"windowHours": 6}, headers=H)
        check(r.status_code == 200, f"AI analysis runs (got {r.status_code}: {r.text[:200]})")
        analysis = r.json()
        check(analysis["touristsAnalysed"] >= 1, "analysis examined the tourist's trail")
        check(analysis["alertCount"] >= 1, f"detectors produced alerts (got {analysis['alertCount']})")
        kinds = {a["kind"] for a in analysis["alerts"]}
        check("prolonged_inactivity" in kinds, f"inactivity detector fired on the stationary tourist (kinds: {kinds})")

        alert = analysis["alerts"][0]
        check(0 <= alert["score"] <= 100, "alert carries a 0-100 score")
        check(alert["severity"] in ("low", "medium", "high"), "alert carries a severity badge")

        r = await client.get("/api/admin/ai/alerts", headers=H)
        check(r.json()["count"] >= 1, "alerts listed for the AI Analytics screen")
        alert_id = r.json()["alerts"][0]["alertId"]

        r = await client.post(
            f"/api/admin/ai/alerts/{alert_id}/action",
            json={"action": "dispatch", "officerId": "OFF001"},
            headers=H,
        )
        check(r.status_code == 200 and r.json()["alert"]["status"] == "dispatched", "Dispatch button works")
        check("incidentId" in r.json(), "dispatching an AI alert creates a real incident")

        r = await client.get("/api/admin/officers", headers=H)
        check(r.json()["count"] == 1, "officer roster endpoint works")
        check("activeAssignments" in r.json()["officers"][0], "officer roster reports active assignment load")

        # --- auth guard ---
        print("\n--- Auth guard ---")
        # A tourist token is signed with JWT_SECRET, admin routes verify against
        # ADMIN_JWT_SECRET - so it fails at the signature check (401), never even
        # reaching the role comparison. Separate secrets per role is what makes
        # privilege escalation impossible here, not just a role string check.
        r = await client.get("/api/admin/dashboard/overview", headers=TH)
        check(r.status_code == 401, f"a tourist token cannot reach admin endpoints (got {r.status_code})")

        r = await client.get("/api/admin/dashboard/overview")
        check(r.status_code == 401, "admin endpoints reject requests with no token at all")

    print(f"\n[smoketest-admin] {'ALL PASSED' if failures == 0 else f'{failures} FAILED'}")
    sys.exit(0 if failures == 0 else 1)


if __name__ == "__main__":
    asyncio.run(run())
