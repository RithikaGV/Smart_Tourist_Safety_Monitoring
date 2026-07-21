"""
utils/safety_score_job.py
APScheduler job that periodically refreshes AI safety scores for active
trips and pushes the update to that user's socket room - the Python
equivalent of the Node version's node-cron job.
"""
import os
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from database.db import get_db
from utils.id_generator import next_sequential_id
from utils.safety_score import compute_safety_score
from utils.socket_manager import sio

scheduler = AsyncIOScheduler()


async def _refresh_active_trip_scores():
    db = get_db()
    active_trips = await db["trips"].find({"status": "active"}).to_list(length=None)

    for trip in active_trips:
        lng, lat = trip["destinationCoords"]["coordinates"]
        score = await compute_safety_score(lat, lng)

        ai_safety_id = await next_sequential_id("ai_safety", "aiSafetyId", "AI")
        await db["ai_safety"].insert_one(
            {"aiSafetyId": ai_safety_id, "tripId": trip["tripId"], "userId": trip["userId"], **score}
        )
        await sio.emit("safety:update", {"tripId": trip["tripId"], **score}, room=f"user-{trip['userId']}")

    if active_trips:
        print(f"[cron] refreshed safety scores for {len(active_trips)} active trip(s)")


def start_safety_score_job():
    interval_minutes = int(os.getenv("SAFETY_SCORE_INTERVAL_MINUTES", "30"))
    scheduler.add_job(_refresh_active_trip_scores, "interval", minutes=interval_minutes, id="safety_score_refresh")
    scheduler.start()
    print(f"[cron] safety score job scheduled every {interval_minutes} minute(s)")
