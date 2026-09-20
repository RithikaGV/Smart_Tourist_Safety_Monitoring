"""
seed/smoketest_integration.py
------------------------------
Proves the two halves connect: generates fake tourists through the TOURIST API,
then checks that the data they produce actually shows up correctly on every
ADMIN PANEL screen.

This is the test that would catch a mismatch between what the tourist side
writes and what the admin side reads - the most likely place for the two to
drift apart.

Run from the backend/ directory:
    python -m seed.smoketest_integration
"""
import asyncio
import os
import sys
from datetime import datetime

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
    print("[integration] in-memory mock MongoDB ready\n")

    from httpx import AsyncClient, ASGITransport
    from app import app
    from controllers.auth_controller import hash_password
    from utils.id_generator import next_sequential_id
    from seed.seed import GEOFENCE_DEFS, box_around
    from seed.generate_fake_tourists import create_one_tourist

    now = datetime.utcnow()

    # Seed zones + an admin + an officer
    for g in GEOFENCE_DEFS:
        gid = await next_sequential_id("geofences", "geofenceId", "GEO")
        await db["geofences"].insert_one(
            {
                "geofenceId": gid,
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
            "email": "officer@safetour.gov.in",
            "passwordHash": hash_password("Officer@123"),
            "station": "Ooty Town Police Station",
            "currentLocation": {"type": "Point", "coordinates": [76.6932, 11.4064]},
            "onDuty": True,
            "createdAt": now,
        }
    )

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test", timeout=30) as client:
        print("--- Generating 30 fake tourists through the tourist API ---")
        stats = {
            "signed_up": 0,
            "signup_failed": 0,
            "trips_created": 0,
            "trip_failed": 0,
            "pings_sent": 0,
            "incidents_triggered": 0,
            "sos_sent": 0,
        }
        # Serial rather than parallel - mongomock isn't built for concurrency and
        # the sequential-ID generator would race against itself.
        for i in range(1, 31):
            await create_one_tourist(client, i, "itg", stats)

        print()
        check(stats["signed_up"] == 30, f"all 30 tourists signed up (got {stats['signed_up']})")
        check(stats["trips_created"] == 30, f"all 30 trips created (got {stats['trips_created']})")
        check(stats["pings_sent"] == 180, f"location pings sent (got {stats['pings_sent']})")
        check(stats["incidents_triggered"] > 0, f"some tourists breached geofences (got {stats['incidents_triggered']})")

        print("\n--- Does the admin panel see it? ---")
        r = await client.post("/api/admin/login", json={"email": "admin@safetour.gov.in", "password": "Admin@123"})
        H = {"Authorization": f"Bearer {r.json()['token']}"}

        r = await client.get("/api/admin/dashboard/overview", headers=H)
        cards = r.json()["cards"]
        check(cards["totalTourists"] == 30, f"dashboard Total Tourists shows 30 (got {cards['totalTourists']})")
        check(cards["activeTourists"] > 0, f"dashboard Active Tourists is non-zero (got {cards['activeTourists']})")

        r = await client.get("/api/admin/dashboard/incident-stats", headers=H)
        total_incidents = r.json()["total"]
        check(total_incidents == stats["incidents_triggered"] + stats["sos_sent"],
              f"incident stats total matches what the tourists generated "
              f"({total_incidents} vs {stats['incidents_triggered']}+{stats['sos_sent']})")

        r = await client.get("/api/admin/heatmap", params={"timeRange": "24h"}, headers=H)
        heat = r.json()
        check(heat["totalTouristsTracked"] == 30, f"heatmap tracks all 30 tourists (got {heat['totalTouristsTracked']})")
        check(len(heat["spots"]) > 1, f"tourists cluster into multiple map spots (got {len(heat['spots'])})")
        check(sum(heat["legend"].values()) == len(heat["spots"]), "every spot is assigned a risk colour")

        r = await client.get("/api/admin/heatmap/density", headers=H, params={"timeRange": "24h"})
        density = r.json()["density"]
        check(len(density) > 0, "density bars populated")
        check(all(d["band"] in ("GREEN", "YELLOW", "RED") for d in density), "every density bar has a valid band")

        r = await client.get("/api/admin/incidents", headers=H)
        incidents = r.json()["incidents"]
        check(len(incidents) > 0, f"incident list populated ({len(incidents)} incidents)")
        check(all(i["uiStatus"] in ("pending", "investigating", "closed") for i in incidents),
              "every incident maps to a valid UI status")
        check(all(i["priority"] in ("low", "medium", "high") for i in incidents),
              "every incident maps to a valid priority badge")
        check(all(i["touristName"] and i["touristName"] != i["userId"] for i in incidents),
              "every incident row resolved the tourist's real name")

        if stats["sos_sent"] > 0:
            r = await client.get("/api/admin/sos", headers=H)
            sos_rows = r.json()["requests"]
            check(len(sos_rows) == stats["sos_sent"], f"SOS table shows all {stats['sos_sent']} SOS request(s)")
            check(all(s["reference"].startswith("SOS-") for s in sos_rows), "every SOS row has a formatted reference")

            sos_id = sos_rows[0]["sosId"]
            r = await client.get(f"/api/admin/sos/{sos_id}", headers=H)
            check(len(r.json()["request"]["trail"]) > 0, "SOS detail shows the tourist's real movement trail")

            r = await client.post(f"/api/admin/sos/{sos_id}/assign", json={"officerId": "OFF001"}, headers=H)
            check(r.json()["request"]["uiStatus"] == "investigating", "officer assignment works on generated data")
        else:
            print("  note: this run generated no SOS (they're random at ~5%) - SOS table checks skipped")

        print("\n--- AI analytics over the generated movement ---")
        # Normal generated tourists all ping "now", so the time-based detectors
        # have nothing to find. Add the anomalous ones so the detectors are
        # actually exercised rather than trivially passing on an empty set.
        from seed.generate_fake_tourists import create_anomalous_tourists

        await create_anomalous_tourists(client, db, "itg", stats)

        r = await client.post("/api/admin/ai/analyze", params={"windowHours": 24}, headers=H)
        analysis = r.json()
        check(analysis["touristsAnalysed"] > 0, f"AI analysed real trails (got {analysis['touristsAnalysed']})")
        check(all(0 <= a["score"] <= 100 for a in analysis["alerts"]), "every AI alert score is within 0-100")
        check(analysis["alertCount"] > 0, f"detectors produced alerts (got {analysis['alertCount']})")

        kinds = {a["kind"] for a in analysis["alerts"]}
        check("prolonged_inactivity" in kinds, f"inactivity detector fired (kinds found: {kinds})")
        check("repeated_looping" in kinds, f"looping detector fired (kinds found: {kinds})")
        check("suspicious_group" in kinds, f"cluster detector fired (kinds found: {kinds})")

        r = await client.get("/api/admin/ai/alerts", headers=H)
        listed = r.json()
        check(listed["count"] > 0, "AI Analytics screen would show alerts")
        check(all(a.get("title") and a.get("detail") for a in listed["alerts"]),
              "every alert carries a human-readable title and explanation")

        print("\n--- Admin-created zone reaches the tourists ---")
        r = await client.post(
            "/api/admin/zones",
            json={
                "name": "Integration Test Landslide Zone",
                "type": "landslide_area",
                "status": "active",
                "latitude": 11.4064,
                "longitude": 76.6932,
                "radiusMeters": 5000,
                "severity": "critical",
                "pushInstantAlert": True,
            },
            headers=H,
        )
        check(r.status_code == 201, f"zone created (got {r.status_code})")
        alerted = r.json()["touristsAlerted"]
        check(alerted > 0, f"instant alert reached tourists standing inside the new zone (got {alerted})")

        notif_count = await db["notifications"].count_documents({"type": "geofence_alert"})
        check(notif_count > 0, f"alert notifications written to the DB ({notif_count})")

    print(f"\n[integration] {'ALL PASSED' if failures == 0 else f'{failures} FAILED'}")
    sys.exit(0 if failures == 0 else 1)


if __name__ == "__main__":
    asyncio.run(run())
