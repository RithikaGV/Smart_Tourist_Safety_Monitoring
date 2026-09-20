"""
controllers/admin_dashboard_controller.py
------------------------------------------
Backs the admin panel's "Dashboard" screen:
  - the four KPI cards (Total Tourists / Active Tourists / Live SOS / Live E-FIR)
  - the "Incident Stats (This Month)" bar chart
  - the recent SOS alert feed
"""
from datetime import datetime, timedelta

from database.db import get_db
from utils.status_map import decorate, to_ui_status

# Order matters - the dashboard chart renders the bars in this order.
INCIDENT_CATEGORIES = ["theft", "harassment", "accident", "missing", "fraud", "medical", "other"]

ACTIVE_WINDOW_MINUTES = 15  # a tourist counts as "active" if they pinged this recently


async def dashboard_overview() -> dict:
    db = get_db()
    now = datetime.utcnow()
    active_since = now - timedelta(minutes=ACTIVE_WINDOW_MINUTES)
    month_start = datetime(now.year, now.month, 1)

    total_tourists = await db["users"].count_documents({})
    active_tourist_ids = await db["Live locations"].distinct("userId", {"recordedAt": {"$gte": active_since}})

    # "Unchecked by officers" in the UI = nobody has acknowledged it yet.
    live_sos = await db["sos_requests"].count_documents({"status": "pending"})
    live_efir = await db["efir"].count_documents({"status": {"$in": ["draft", "filed"]}})

    active_trips = await db["trips"].count_documents({"status": "active"})
    open_incidents = await db["incidents"].count_documents({"status": {"$in": ["open", "acknowledged", "responding"]}})

    return {
        "success": True,
        "cards": {
            "totalTourists": total_tourists,
            "activeTourists": len(active_tourist_ids),
            "liveSOSRequests": live_sos,
            "liveEFIRRequests": live_efir,
        },
        "extra": {"activeTrips": active_trips, "openIncidents": open_incidents},
        "generatedAt": now.isoformat(),
    }


async def incident_stats(month: int | None = None, year: int | None = None) -> dict:
    """Counts incidents per category for the given month (defaults to current)."""
    db = get_db()
    now = datetime.utcnow()
    year = year or now.year
    month = month or now.month

    period_start = datetime(year, month, 1)
    period_end = datetime(year + 1, 1, 1) if month == 12 else datetime(year, month + 1, 1)

    pipeline = [
        {"$match": {"createdAt": {"$gte": period_start, "$lt": period_end}}},
        {"$group": {"_id": "$category", "count": {"$sum": 1}}},
    ]
    rows = await db["incidents"].aggregate(pipeline).to_list(length=None)
    counts = {row["_id"] or "other": row["count"] for row in rows}

    stats = [{"category": c, "label": c.title(), "count": counts.get(c, 0)} for c in INCIDENT_CATEGORIES]
    total = sum(s["count"] for s in stats)
    peak = max((s["count"] for s in stats), default=0)

    # The UI bars are drawn as a percentage of the largest category.
    for s in stats:
        s["barPercent"] = round((s["count"] / peak) * 100) if peak else 0

    return {
        "success": True,
        "period": {"month": month, "year": year},
        "total": total,
        "stats": stats,
    }


async def recent_sos(limit: int = 5) -> dict:
    """The dashboard's recent SOS feed, joined with the tourist's name."""
    db = get_db()
    sos_list = await db["sos_requests"].find().sort("createdAt", -1).limit(limit).to_list(length=limit)

    results = []
    for sos in sos_list:
        user = await db["users"].find_one({"userId": sos["userId"]}, {"fullName": 1, "mobileNumber": 1})
        coords = sos["location"]["coordinates"]
        results.append(
            {
                "sosId": sos["sosId"],
                "userId": sos["userId"],
                "touristName": (user or {}).get("fullName", sos["userId"]),
                "locationName": sos.get("locationName"),
                "coordinates": {"lat": coords[1], "lng": coords[0]},
                "status": sos["status"],
                "uiStatus": to_ui_status(sos["status"]),
                "createdAt": sos["createdAt"].isoformat() if hasattr(sos.get("createdAt"), "isoformat") else sos.get("createdAt"),
            }
        )

    return {"success": True, "recentSOS": results}
