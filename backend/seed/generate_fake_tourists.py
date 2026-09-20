"""
seed/generate_fake_tourists.py
--------------------------------
Creates realistic fake tourists by calling your REAL running API - not by
writing straight into MongoDB. Every fake tourist goes through the exact same
pipeline a real user would: signup -> KYC record -> blockchain ID issuance ->
trip creation -> AI safety score -> a simulated GPS trail that gets
road-snapped and geofence-checked (a few are deliberately routed through your
seeded restricted zones so you have live incidents/alerts to show in the
demo) -> and a handful trigger a real SOS.

USAGE
-----
1) Start your real server first:
     uvicorn app:socket_app --reload --port 5000
   (and make sure you've already run `python -m seed.seed` at least once so
   the Nilgiri geofences exist - that's what makes the geofence-breach demo
   data possible)

2) In another terminal:
     pip install faker
     python -m seed.generate_fake_tourists --count 100

Useful flags:
    --count 100          how many fake tourists to create (default 100)
    --base-url URL       default http://localhost:5000
    --concurrency 5      how many to create in parallel (default 5; keep this
                         modest - the public OSRM demo server is free and
                         shared, don't hammer it)
    --local-test         runs against the in-process app with no real server,
                         real Mongo or real OSRM needed - useful to sanity-check
                         this script itself before your demo
"""
import argparse
import asyncio
import os
import random
import sys
import time
from datetime import date, timedelta

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import httpx
from faker import Faker

fake = Faker("en_IN")

# Real-ish Nilgiri district points of interest tourists would search for.
# (Kodaikanal is technically Dindigul district, but it appeared in your earlier
# demo recording as a searched destination, so it's included too.)
DESTINATIONS = [
    {"name": "Ooty", "lat": 11.4064, "lng": 76.6932},
    {"name": "Coonoor", "lat": 11.3530, "lng": 76.7959},
    {"name": "Kotagiri", "lat": 11.4256, "lng": 76.8664},
    {"name": "Pykara Falls", "lat": 11.4923, "lng": 76.6270},
    {"name": "Mudumalai Tiger Reserve", "lat": 11.5661, "lng": 76.5341},
    {"name": "Doddabetta Peak", "lat": 11.4034, "lng": 76.7333},
    {"name": "Botanical Garden, Ooty", "lat": 11.4131, "lng": 76.6961},
    {"name": "kodaikanal", "lat": 10.2381, "lng": 77.4892},
]

# A common road gateway into the Nilgiris (Mettupalayam), used as a plausible
# "origin" so route previews + GPS trails start somewhere realistic.
GATEWAY_ORIGIN = {"lat": 11.2996, "lng": 76.9366}

# Same centers used in seed/seed.py's geofences - pinging near these reliably
# demonstrates the auto-incident/alert pipeline for a subset of tourists.
GEOFENCE_TRIGGER_POINTS = [
    {"lat": 11.5661, "lng": 76.5341, "label": "Mudumalai core zone"},
    {"lat": 11.4300, "lng": 76.6800, "label": "Toda sacred grove"},
    {"lat": 11.4256, "lng": 76.8664, "label": "Kotagiri restricted estate"},
    {"lat": 11.4923, "lng": 76.6270, "label": "Pykara Falls high-risk slope"},
]

TRAVEL_TYPES = ["Solo", "Family", "Friends", "Business"]
LANGUAGES = ["English", "Tamil", "Hindi", "Malayalam", "Kannada", "Telugu"]
GENDERS = ["Male", "Female", "Other", "Prefer not to say"]


def jitter(value, spread=0.01):
    return value + random.uniform(-spread, spread)


def build_gps_trail(origin, destination, hit_geofence, steps: int = 6):
    """Straight-line-with-noise trail from origin to destination, optionally
    bending a midpoint through a known geofence so that tourist's pings trigger
    the auto-incident pipeline."""
    trail = []
    for i in range(steps):
        t = i / (steps - 1)
        lat = origin["lat"] + (destination["lat"] - origin["lat"]) * t
        lng = origin["lng"] + (destination["lng"] - origin["lng"]) * t

        if hit_geofence and 0.4 <= t <= 0.6:
            lat = jitter(hit_geofence["lat"], 0.003)
            lng = jitter(hit_geofence["lng"], 0.003)
        else:
            lat = jitter(lat)
            lng = jitter(lng)

        trail.append({"lat": lat, "lng": lng})
    return trail


async def create_one_tourist(client, index: int, run_tag: str, stats: dict):
    gender = random.choice(GENDERS)
    if gender == "Male":
        first = fake.first_name_male()
    elif gender == "Female":
        first = fake.first_name_female()
    else:
        first = fake.first_name()
    last = fake.last_name()
    full_name = f"{first} {last}"
    email = f"{first.lower()}.{last.lower()}{run_tag}{index}@example.com"
    mobile = f"9{random.randint(100000000, 999999999)}"
    dob = fake.date_of_birth(minimum_age=18, maximum_age=65).isoformat()
    nationality = "Indian" if random.random() < 0.9 else fake.country()

    try:
        r = await client.post(
            "/api/auth/create-account",
            json={
                "fullName": full_name,
                "email": email,
                "mobileNumber": mobile,
                "password": "Demo@12345",
                "dateOfBirth": dob,
                "gender": gender,
                "nationality": nationality,
                "preferredLanguage": random.choice(LANGUAGES),
                "idType": "Aadhaar" if nationality == "Indian" else "Passport",
            },
        )
        if r.status_code != 201:
            stats["signup_failed"] += 1
            print(f"  [{index:03d}] signup FAILED ({r.status_code}): {r.text[:120]}")
            return
        data = r.json()
        token = data["token"]
        blockchain_id = data["user"]["blockchainId"]
        headers = {"Authorization": f"Bearer {token}"}
        stats["signed_up"] += 1
    except Exception as err:
        stats["signup_failed"] += 1
        print(f"  [{index:03d}] signup ERROR: {err}")
        return

    destination = random.choice(DESTINATIONS)
    # Relative dates - a hardcoded date silently becomes a "past" trip later.
    travel_date = (date.today() + timedelta(days=random.randint(0, 30))).isoformat()

    try:
        r = await client.post(
            "/api/trips/",
            json={
                "destination": destination["name"],
                "destinationCoords": {"lat": destination["lat"], "lng": destination["lng"]},
                "originCoords": GATEWAY_ORIGIN,
                "travelDate": travel_date,
                "travelTime": f"{random.randint(6, 20):02d}:{random.choice(['00', '15', '30', '45'])}",
                "numberOfTravelers": random.randint(1, 6),
                "travelType": random.choice(TRAVEL_TYPES),
            },
            headers=headers,
        )
        if r.status_code != 201:
            stats["trip_failed"] += 1
            print(f"  [{index:03d}] {full_name}: trip creation FAILED ({r.status_code})")
            return
        trip_id = r.json()["trip"]["tripId"]
        stats["trips_created"] += 1
    except Exception as err:
        stats["trip_failed"] += 1
        print(f"  [{index:03d}] {full_name}: trip ERROR: {err}")
        return

    await client.post(f"/api/trips/{trip_id}/start", headers=headers)

    # ~25% get deliberately routed through a restricted zone, so the demo has
    # real live geofence-breach incidents to point at.
    hit_geofence = random.choice(GEOFENCE_TRIGGER_POINTS) if random.random() < 0.25 else None
    trail = build_gps_trail(GATEWAY_ORIGIN, destination, hit_geofence)

    incidents = 0
    for point in trail:
        try:
            r = await client.post(
                "/api/location/ping",
                json={
                    "lat": point["lat"],
                    "lng": point["lng"],
                    "tripId": trip_id,
                    "speedKmh": round(random.uniform(15, 60), 1),
                },
                headers=headers,
            )
            if r.status_code == 200 and r.json().get("incident"):
                incidents += 1
        except Exception:
            pass  # one dropped ping shouldn't kill this tourist's whole setup

    stats["pings_sent"] += len(trail)
    stats["incidents_triggered"] += incidents

    # ~5% also fire a real SOS, for the demo's alert/dispatch flow.
    sent_sos = False
    if random.random() < 0.05:
        last = trail[-1]
        try:
            r = await client.post(
                "/api/sos/",
                json={"lat": last["lat"], "lng": last["lng"], "tripId": trip_id, "triggerMethod": "app_button"},
                headers=headers,
            )
            sent_sos = r.status_code == 201
            if sent_sos:
                stats["sos_sent"] += 1
        except Exception:
            pass

    tags = []
    if hit_geofence:
        tags.append(f"crossed {hit_geofence['label']}")
    if sent_sos:
        tags.append("SOS sent")
    suffix = f" ({', '.join(tags)})" if tags else ""
    print(f"  [{index:03d}] {full_name} -> {destination['name']} | {blockchain_id}{suffix}")


async def create_anomalous_tourists(client, db, run_tag: str, stats: dict):
    """Creates tourists whose movement genuinely trips the AI detectors.

    The detectors need movement spread over TIME (e.g. "stationary for 90+
    minutes"), but pings sent through the API are all stamped with the current
    moment - so a normal generated tourist looks like they teleported instantly
    and nothing ever fires. These tourists are created through the real API like
    everyone else; only their ping TIMESTAMPS are then backdated directly in the
    database, because there's no legitimate API for claiming a ping happened two
    hours ago (and there shouldn't be - that would let a device forge its own
    history).

    Without this the AI Analytics screen is empty in a demo, which makes a
    working feature look broken.
    """
    from datetime import datetime, timedelta

    now = datetime.utcnow()
    made = []

    # 1) STATIONARY - trips the prolonged-inactivity detector
    stationary = [
        ("Inactivity Demo", {"lat": 11.4064, "lng": 76.6932}),
    ]
    for name, spot in stationary:
        email = f"inactive.{run_tag}@example.com"
        r = await client.post(
            "/api/auth/create-account",
            json={
                "fullName": name,
                "email": email,
                "mobileNumber": f"9{random.randint(100000000, 999999999)}",
                "password": "Demo@12345",
                "gender": "Prefer not to say",
                "nationality": "Indian",
            },
        )
        if r.status_code != 201:
            continue
        uid = r.json()["user"]["userId"]
        headers = {"Authorization": f"Bearer {r.json()['token']}"}
        stats["signed_up"] += 1

        for _ in range(6):
            await client.post(
                "/api/location/ping",
                json={"lat": spot["lat"], "lng": spot["lng"], "speedKmh": 0},
                headers=headers,
            )
            stats["pings_sent"] += 1

        # Backdate this tourist's pings so they span the last 3 hours.
        rows = await db["Live locations"].find({"userId": uid}).sort("recordedAt", 1).to_list(length=None)
        for i, row in enumerate(rows):
            await db["Live locations"].update_one(
                {"_id": row["_id"]}, {"$set": {"recordedAt": now - timedelta(minutes=180 - i * 25)}}
            )
        made.append(("prolonged_inactivity", name))

    # 2) LOOPING - trips the repeated-looping detector by revisiting two anchors
    email = f"looper.{run_tag}@example.com"
    r = await client.post(
        "/api/auth/create-account",
        json={
            "fullName": "Looping Demo",
            "email": email,
            "mobileNumber": f"9{random.randint(100000000, 999999999)}",
            "password": "Demo@12345",
            "gender": "Prefer not to say",
            "nationality": "Indian",
        },
    )
    if r.status_code == 201:
        uid = r.json()["user"]["userId"]
        headers = {"Authorization": f"Bearer {r.json()['token']}"}
        stats["signed_up"] += 1

        a = {"lat": 11.4064, "lng": 76.6932}   # Ooty
        b = {"lat": 11.3530, "lng": 76.7959}   # Coonoor
        for _ in range(4):  # four A->B->A cycles
            for spot in (a, b):
                await client.post(
                    "/api/location/ping",
                    json={"lat": spot["lat"], "lng": spot["lng"], "speedKmh": 35},
                    headers=headers,
                )
                stats["pings_sent"] += 1

        rows = await db["Live locations"].find({"userId": uid}).sort("recordedAt", 1).to_list(length=None)
        for i, row in enumerate(rows):
            await db["Live locations"].update_one(
                {"_id": row["_id"]}, {"$set": {"recordedAt": now - timedelta(minutes=300 - i * 35)}}
            )
        made.append(("repeated_looping", "Looping Demo"))

    # 3) CLUSTER - trips the proximity-cluster detector (5 tourists, same spot)
    cluster_spot = {"lat": 11.4131, "lng": 76.6961}
    for n in range(5):
        r = await client.post(
            "/api/auth/create-account",
            json={
                "fullName": f"Cluster Demo {n + 1}",
                "email": f"cluster{n}.{run_tag}@example.com",
                "mobileNumber": f"9{random.randint(100000000, 999999999)}",
                "password": "Demo@12345",
                "gender": "Prefer not to say",
                "nationality": "Indian",
            },
        )
        if r.status_code != 201:
            continue
        headers = {"Authorization": f"Bearer {r.json()['token']}"}
        stats["signed_up"] += 1
        for _ in range(3):
            await client.post(
                "/api/location/ping",
                json={
                    "lat": cluster_spot["lat"] + random.uniform(-0.001, 0.001),
                    "lng": cluster_spot["lng"] + random.uniform(-0.001, 0.001),
                    "speedKmh": 3,
                },
                headers=headers,
            )
            stats["pings_sent"] += 1
    made.append(("suspicious_group", "Cluster Demo x5"))

    for kind, who in made:
        print(f"  [anomaly] {who} -> will trigger '{kind}'")
    return made


async def run(count: int, base_url: str, concurrency: int, local_test: bool, with_anomalies: bool = True):
    run_tag = str(int(time.time()))[-5:]  # keeps emails unique across repeated runs
    stats = {
        "signed_up": 0,
        "signup_failed": 0,
        "trips_created": 0,
        "trip_failed": 0,
        "pings_sent": 0,
        "incidents_triggered": 0,
        "sos_sent": 0,
    }

    if local_test:
        os.environ.setdefault("JWT_SECRET", "test_secret")
        os.environ.setdefault("ADMIN_JWT_SECRET", "test_admin_secret")
        os.environ.setdefault("OFFICER_JWT_SECRET", "test_officer_secret")
        from mongomock_motor import AsyncMongoMockClient
        import database.db as db_module

        db_module._db = AsyncMongoMockClient()["SmartTouristDB"]
        from app import app as fastapi_app
        from httpx import ASGITransport

        client = httpx.AsyncClient(transport=ASGITransport(app=fastapi_app), base_url="http://test", timeout=30)
        print("[generate] --local-test mode (in-memory mock DB, no real server needed)")

        # The mock DB starts empty, so seed the same Nilgiri zones seed/seed.py
        # creates - otherwise no tourist can ever breach one and the geofence
        # path goes untested.
        from seed.seed import GEOFENCE_DEFS, box_around
        from utils.id_generator import next_sequential_id
        from datetime import datetime

        db = db_module.get_db()
        for g in GEOFENCE_DEFS:
            geofence_id = await next_sequential_id("geofences", "geofenceId", "GEO")
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
                    "createdAt": datetime.utcnow(),
                    "updatedAt": datetime.utcnow(),
                }
            )
        print(f"[generate] seeded {len(GEOFENCE_DEFS)} demo geofences into the mock DB\n")
    else:
        client = httpx.AsyncClient(base_url=base_url, timeout=30)
        print(f"[generate] targeting real server at {base_url}\n")

    semaphore = asyncio.Semaphore(concurrency)

    async def bound(i):
        async with semaphore:
            await create_one_tourist(client, i, run_tag, stats)

    async with client:
        await asyncio.gather(*(bound(i) for i in range(1, count + 1)))

        if with_anomalies:
            print("\n[generate] creating anomalous tourists so AI Analytics has real alerts...")
            # Needs direct DB access to backdate ping timestamps - only possible
            # in --local-test mode, or against a real Mongo the script can reach.
            try:
                import database.db as db_module

                db = db_module.get_db()
                await create_anomalous_tourists(client, db, run_tag, stats)
            except RuntimeError:
                print("  skipped: no direct database handle available in this mode.")
                print("  (run with --local-test, or run this script on the same machine as MongoDB")
                print("   with MONGO_URI set, to generate AI-detectable movement patterns)")

    print("\n[generate] summary")
    print(f"  tourists signed up:  {stats['signed_up']} (failed: {stats['signup_failed']})")
    print(f"  trips created:       {stats['trips_created']} (failed: {stats['trip_failed']})")
    print(f"  location pings sent: {stats['pings_sent']}")
    print(f"  geofence incidents:  {stats['incidents_triggered']}")
    print(f"  SOS requests sent:   {stats['sos_sent']}")
    if local_test:
        print("\n--local-test mode: nothing was written to a real database.")
    else:
        print("\nAll data went through the real API into your SmartTouristDB.")


def main():
    parser = argparse.ArgumentParser(description="Generate fake tourists through the real SafeTour API for demos.")
    parser.add_argument("--count", type=int, default=100)
    parser.add_argument("--base-url", type=str, default="http://localhost:5000")
    parser.add_argument("--concurrency", type=int, default=5)
    parser.add_argument("--local-test", action="store_true")
    parser.add_argument(
        "--no-anomalies",
        action="store_true",
        help="skip creating the extra tourists whose movement triggers the AI detectors",
    )
    args = parser.parse_args()

    asyncio.run(run(args.count, args.base_url, args.concurrency, args.local_test, not args.no_anomalies))


if __name__ == "__main__":
    main()
