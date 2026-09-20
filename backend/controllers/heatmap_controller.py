"""
controllers/heatmap_controller.py
----------------------------------
Backs the admin panel's "Risk Heatmap" screen: a district-wide live map with
tourist density and colour-coded risk levels (Safe / Crowded / Danger), plus
the "Tourist Density Visualization" bars underneath it.

How the risk colour is decided for each spot:
  - DANGER  (red)    - the spot sits inside a high-severity geofence, or has an
                       open SOS/critical incident attached to it
  - CROWDED (yellow) - tourist count at that spot is at/over the crowding
                       threshold, but nothing dangerous is happening
  - SAFE    (green)  - everything else

This is intentionally a transparent rule-based calculation rather than a black
box, so during a demo you can explain exactly why any given dot is the colour
it is.
"""
from datetime import datetime, timedelta

from database.db import get_db
from utils.geofence_check import find_geofences_containing

ACTIVE_WINDOW_MINUTES = 30
CLUSTER_PRECISION = 2  # decimal degrees for grouping (~1.1 km buckets)
CROWD_THRESHOLD = 8  # tourists at one spot before it counts as "crowded"
CROWD_CAPACITY = 40  # what a density bar treats as 100%

TIME_RANGES = {
    "now": 30,
    "1h": 60,
    "6h": 360,
    "24h": 1440,
    "7d": 10080,
}


def _cluster_key(lat: float, lng: float):
    return (round(lat, CLUSTER_PRECISION), round(lng, CLUSTER_PRECISION))


async def risk_heatmap(time_range: str = "now", district: str | None = None) -> dict:
    db = get_db()
    minutes = TIME_RANGES.get(time_range, 30)
    since = datetime.utcnow() - timedelta(minutes=minutes)

    # Take each tourist's most recent ping inside the window - one dot per
    # tourist, not one per ping, otherwise someone standing still would look
    # like a crowd.
    pipeline = [
        {"$match": {"recordedAt": {"$gte": since}}},
        {"$sort": {"recordedAt": -1}},
        {
            "$group": {
                "_id": "$userId",
                "location": {"$first": "$snappedLocation"},
                "rawLocation": {"$first": "$rawLocation"},
                "recordedAt": {"$first": "$recordedAt"},
                "insideGeofenceIds": {"$first": "$insideGeofenceIds"},
            }
        },
    ]
    latest = await db["Live locations"].aggregate(pipeline).to_list(length=None)

    clusters: dict = {}
    for row in latest:
        coords = (row.get("location") or {}).get("coordinates") or (row.get("rawLocation") or {}).get("coordinates")
        if not coords:
            continue
        lng, lat = coords[0], coords[1]
        key = _cluster_key(lat, lng)

        bucket = clusters.setdefault(
            key,
            {"lat": key[0], "lng": key[1], "touristCount": 0, "userIds": [], "geofenceIds": set()},
        )
        bucket["touristCount"] += 1
        bucket["userIds"].append(row["_id"])
        for gid in row.get("insideGeofenceIds") or []:
            bucket["geofenceIds"].add(gid)

    # Pull in anything dangerous happening right now so it can override colour.
    open_sos = await db["sos_requests"].find({"status": {"$in": ["pending", "acknowledged", "dispatched"]}}).to_list(length=None)
    open_incidents = await db["incidents"].find(
        {"status": {"$in": ["open", "acknowledged", "responding"]}, "severity": {"$in": ["high", "critical"]}}
    ).to_list(length=None)

    danger_points = []
    for doc in list(open_sos) + list(open_incidents):
        c = doc["location"]["coordinates"]
        danger_points.append(_cluster_key(c[1], c[0]))
    danger_keys = set(danger_points)

    geofence_lookup = {g["geofenceId"]: g for g in await db["geofences"].find({"active": True}).to_list(length=None)}

    spots = []
    for key, bucket in clusters.items():
        severities = [geofence_lookup.get(gid, {}).get("severity") for gid in bucket["geofenceIds"]]
        in_dangerous_zone = any(s in ("high", "critical") for s in severities if s)
        has_live_emergency = key in danger_keys

        if in_dangerous_zone or has_live_emergency:
            risk = "danger"
        elif bucket["touristCount"] >= CROWD_THRESHOLD:
            risk = "crowded"
        else:
            risk = "safe"

        zone_names = [geofence_lookup[gid]["name"] for gid in bucket["geofenceIds"] if gid in geofence_lookup]

        spots.append(
            {
                "lat": bucket["lat"],
                "lng": bucket["lng"],
                "touristCount": bucket["touristCount"],
                "risk": risk,
                "densityPercent": min(100, round((bucket["touristCount"] / CROWD_CAPACITY) * 100)),
                "zones": zone_names,
                "label": zone_names[0] if zone_names else f"{bucket['lat']:.2f}, {bucket['lng']:.2f}",
                "hasLiveEmergency": has_live_emergency,
            }
        )

    spots.sort(key=lambda s: s["touristCount"], reverse=True)

    legend = {
        "safe": sum(1 for s in spots if s["risk"] == "safe"),
        "crowded": sum(1 for s in spots if s["risk"] == "crowded"),
        "danger": sum(1 for s in spots if s["risk"] == "danger"),
    }

    return {
        "success": True,
        "timeRange": time_range,
        "district": district or "All Districts",
        "totalTouristsTracked": sum(s["touristCount"] for s in spots),
        "legend": legend,
        "spots": spots,
    }


async def tourist_density(time_range: str = "now", limit: int = 10) -> dict:
    """The 'Tourist Density Visualization' bars - busiest spots, with a
    green/yellow/red band and a percentage of assumed capacity."""
    heatmap = await risk_heatmap(time_range=time_range)

    bands = {"safe": "GREEN", "crowded": "YELLOW", "danger": "RED"}
    rows = [
        {
            "label": spot["label"],
            "touristCount": spot["touristCount"],
            "densityPercent": spot["densityPercent"],
            "band": bands.get(spot["risk"], "GREEN"),
            "lat": spot["lat"],
            "lng": spot["lng"],
        }
        for spot in heatmap["spots"][:limit]
    ]

    return {"success": True, "timeRange": time_range, "density": rows}


async def live_tourist_positions(limit: int = 500) -> dict:
    """Individual live markers for the heatmap map itself (not clustered)."""
    db = get_db()
    since = datetime.utcnow() - timedelta(minutes=ACTIVE_WINDOW_MINUTES)

    pipeline = [
        {"$match": {"recordedAt": {"$gte": since}}},
        {"$sort": {"recordedAt": -1}},
        {
            "$group": {
                "_id": "$userId",
                "location": {"$first": "$snappedLocation"},
                "rawLocation": {"$first": "$rawLocation"},
                "recordedAt": {"$first": "$recordedAt"},
                "tripId": {"$first": "$tripId"},
            }
        },
        {"$limit": limit},
    ]
    rows = await db["Live locations"].aggregate(pipeline).to_list(length=limit)

    positions = []
    for row in rows:
        coords = (row.get("location") or {}).get("coordinates") or (row.get("rawLocation") or {}).get("coordinates")
        if not coords:
            continue
        user = await db["users"].find_one({"userId": row["_id"]}, {"fullName": 1})
        positions.append(
            {
                "userId": row["_id"],
                "touristName": (user or {}).get("fullName", row["_id"]),
                "lat": coords[1],
                "lng": coords[0],
                "tripId": row.get("tripId"),
                "recordedAt": row["recordedAt"].isoformat() if hasattr(row.get("recordedAt"), "isoformat") else row.get("recordedAt"),
            }
        )

    return {"success": True, "count": len(positions), "positions": positions}
