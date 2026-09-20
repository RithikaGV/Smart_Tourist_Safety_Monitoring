"""
controllers/ai_analytics_controller.py
---------------------------------------
Backs the admin panel's "AI Analytics" screen (Suspicious Movement Alerts).

These detectors run over the real `Live locations` trail data rather than
returning canned rows, so during a demo the alerts genuinely correspond to what
the tracked tourists did. Each detector returns a 0-100 score; the score drives
both the severity badge and the ordering.

The detectors are deliberately explainable heuristics, not a trained model -
each one states plainly why it fired. Swap any detector's body for a real model
later; the alert shape the UI consumes stays the same.
"""
import math
from datetime import datetime, timedelta

from fastapi import HTTPException

from database.db import get_db
from utils.id_generator import next_sequential_id
from utils.socket_manager import sio
from models.ai_alert import AIAlertActionRequest

# Tuning knobs - all in one place so they're easy to explain/adjust in a demo.
LOOP_RADIUS_KM = 1.0          # revisiting within this counts as returning to a spot
LOOP_MIN_VISITS = 3           # this many separate visits = looping behaviour
INACTIVITY_MINUTES = 90       # no movement beyond STATIONARY_KM for this long
STATIONARY_KM = 0.15
NIGHT_HOURS = range(22, 24)   # plus 0-5, handled in the check
DEVIATION_KM = 12.0           # distance from planned destination before flagging
GROUP_RADIUS_KM = 0.3         # tourists this close together count as a group
GROUP_MIN_SIZE = 4

SEVERITY_FROM_SCORE = lambda s: "high" if s >= 80 else "medium" if s >= 60 else "low"  # noqa: E731


def haversine_km(lat1, lng1, lat2, lng2) -> float:
    """Great-circle distance between two lat/lng points, in kilometres."""
    r = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = math.radians(lat2 - lat1)
    dl = math.radians(lng2 - lng1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


def _coords_of(row: dict):
    c = (row.get("snappedLocation") or {}).get("coordinates") or (row.get("rawLocation") or {}).get("coordinates")
    return (c[1], c[0]) if c else (None, None)


async def _trails(db, since: datetime, min_points: int = 3) -> dict:
    """Recent location trail per tourist, oldest -> newest."""
    rows = await db["Live locations"].find({"recordedAt": {"$gte": since}}).sort("recordedAt", 1).to_list(length=None)
    trails: dict = {}
    for row in rows:
        trails.setdefault(row["userId"], []).append(row)
    return {uid: pts for uid, pts in trails.items() if len(pts) >= min_points}


async def _tourist_name(db, user_id: str) -> str:
    user = await db["users"].find_one({"userId": user_id}, {"fullName": 1})
    return (user or {}).get("fullName", user_id)


async def detect_repeated_looping(db, trails) -> list:
    """Same tourist circling back to the same place repeatedly - the pattern
    behind the panel's 'Ooty -> Coonoor -> Bandipur (3 loops in 6h)' example."""
    alerts = []
    for user_id, points in trails.items():
        anchors: list = []  # [[lat, lng, visit_count]]
        last_anchor_idx = None

        for row in points:
            lat, lng = _coords_of(row)
            if lat is None:
                continue
            matched = None
            for idx, (alat, alng, _) in enumerate(anchors):
                if haversine_km(lat, lng, alat, alng) <= LOOP_RADIUS_KM:
                    matched = idx
                    break
            if matched is None:
                anchors.append([lat, lng, 1])
                last_anchor_idx = len(anchors) - 1
            else:
                # Only count it as a new visit if they left and came back.
                if last_anchor_idx != matched:
                    anchors[matched][2] += 1
                last_anchor_idx = matched

        loops = max((a[2] for a in anchors), default=0)
        if loops >= LOOP_MIN_VISITS:
            hours = round((points[-1]["recordedAt"] - points[0]["recordedAt"]).total_seconds() / 3600, 1)
            score = min(95, 55 + loops * 10)
            alerts.append(
                {
                    "kind": "repeated_looping",
                    "userId": user_id,
                    "title": f"Repeated looping - {await _tourist_name(db, user_id)}",
                    "detail": f"Returned to the same location {loops} times in {hours}h.",
                    "score": score,
                    "modelName": "Movement Pattern Heuristic v1",
                    "evidence": {"loops": loops, "windowHours": hours},
                }
            )
    return alerts


async def detect_prolonged_inactivity(db, trails) -> list:
    """A tracked tourist who stops moving for a long stretch - possible injury,
    phone abandoned, or someone in trouble."""
    alerts = []
    now = datetime.utcnow()
    for user_id, points in trails.items():
        last = points[-1]
        lat, lng = _coords_of(last)
        if lat is None:
            continue

        stationary_since = last["recordedAt"]
        for row in reversed(points):
            rlat, rlng = _coords_of(row)
            if rlat is None:
                continue
            if haversine_km(lat, lng, rlat, rlng) <= STATIONARY_KM:
                stationary_since = row["recordedAt"]
            else:
                break

        minutes = (now - stationary_since).total_seconds() / 60
        if minutes >= INACTIVITY_MINUTES:
            hour = last["recordedAt"].hour
            at_night = hour in NIGHT_HOURS or hour < 6
            score = min(92, 50 + int(minutes / 30) * 8 + (12 if at_night else 0))
            alerts.append(
                {
                    "kind": "prolonged_inactivity",
                    "userId": user_id,
                    "title": f"No movement for {int(minutes)} min - {await _tourist_name(db, user_id)}",
                    "detail": f"Stationary at {lat:.4f}, {lng:.4f}" + (" during night hours." if at_night else "."),
                    "score": score,
                    "modelName": "Inactivity Detector v1",
                    "evidence": {"stationaryMinutes": int(minutes), "atNight": at_night},
                }
            )
    return alerts


async def detect_route_deviation(db, trails) -> list:
    """Tourist is far from the destination of their own active trip."""
    alerts = []
    for user_id, points in trails.items():
        trip = await db["trips"].find_one({"userId": user_id, "status": "active"})
        if not trip:
            continue

        dest = trip["destinationCoords"]["coordinates"]
        lat, lng = _coords_of(points[-1])
        if lat is None:
            continue

        distance = haversine_km(lat, lng, dest[1], dest[0])
        if distance >= DEVIATION_KM:
            score = min(90, 45 + int(distance))
            alerts.append(
                {
                    "kind": "route_deviation",
                    "userId": user_id,
                    "title": f"Off planned route - {await _tourist_name(db, user_id)}",
                    "detail": f"{distance:.1f} km away from declared destination ({trip['destination']}).",
                    "score": score,
                    "modelName": "Route Deviation Heuristic v1",
                    "evidence": {"deviationKm": round(distance, 1), "destination": trip["destination"], "tripId": trip["tripId"]},
                }
            )
    return alerts


async def detect_suspicious_grouping(db, trails) -> list:
    """Several tourists tightly clustered and moving together - the panel's
    'Group of 4 males circling a single tourist' style alert. Flags the cluster
    for an officer to eyeball; it is not an accusation on its own."""
    latest: list = []
    for user_id, points in trails.items():
        lat, lng = _coords_of(points[-1])
        if lat is not None:
            latest.append((user_id, lat, lng))

    used = set()
    alerts = []
    for i, (uid, lat, lng) in enumerate(latest):
        if uid in used:
            continue
        cluster = [uid]
        for j, (ouid, olat, olng) in enumerate(latest):
            if i == j or ouid in used:
                continue
            if haversine_km(lat, lng, olat, olng) <= GROUP_RADIUS_KM:
                cluster.append(ouid)

        if len(cluster) >= GROUP_MIN_SIZE:
            used.update(cluster)
            score = min(85, 50 + len(cluster) * 5)
            alerts.append(
                {
                    "kind": "suspicious_group",
                    "userId": cluster[0],
                    "title": f"Tight cluster of {len(cluster)} tourists",
                    "detail": f"{len(cluster)} tracked tourists within {int(GROUP_RADIUS_KM * 1000)} m of each other at {lat:.4f}, {lng:.4f}.",
                    "score": score,
                    "modelName": "Proximity Cluster Detector v1",
                    "evidence": {"groupSize": len(cluster), "members": cluster},
                }
            )
    return alerts


async def run_analysis(window_hours: int = 6, persist: bool = True) -> dict:
    """Runs every detector over the recent window and returns scored alerts."""
    db = get_db()
    since = datetime.utcnow() - timedelta(hours=window_hours)
    trails = await _trails(db, since)

    found = []
    found += await detect_repeated_looping(db, trails)
    found += await detect_prolonged_inactivity(db, trails)
    found += await detect_route_deviation(db, trails)
    found += await detect_suspicious_grouping(db, trails)

    now = datetime.utcnow()
    saved = []
    for alert in found:
        alert["severity"] = SEVERITY_FROM_SCORE(alert["score"])
        alert["status"] = "open"
        alert["firstSeen"] = now
        alert["windowHours"] = window_hours

        if persist:
            # Don't duplicate an alert that's already open for the same tourist/kind.
            existing = await db["ai_alerts"].find_one(
                {"userId": alert["userId"], "kind": alert["kind"], "status": "open"}
            )
            if existing:
                await db["ai_alerts"].update_one(
                    {"_id": existing["_id"]},
                    {"$set": {"score": alert["score"], "severity": alert["severity"], "detail": alert["detail"], "updatedAt": now}},
                )
                existing.update(alert)
                existing["_id"] = str(existing["_id"])
                existing["alertId"] = existing.get("alertId")
                saved.append(existing)
                continue

            alert_id = await next_sequential_id("ai_alerts", "alertId", "AIA")
            alert["alertId"] = alert_id
            alert["createdAt"] = now
            alert["updatedAt"] = now
            await db["ai_alerts"].insert_one(dict(alert))
            await sio.emit("ai:alert", {k: v for k, v in alert.items() if k != "_id"}, room="admin-room")

        alert.pop("_id", None)
        saved.append(alert)

    saved.sort(key=lambda a: a["score"], reverse=True)
    return {
        "success": True,
        "windowHours": window_hours,
        "touristsAnalysed": len(trails),
        "alertCount": len(saved),
        "highSeverityCount": sum(1 for a in saved if a["severity"] == "high"),
        "alerts": saved,
    }


async def list_alerts(status: str | None = "open", limit: int = 100) -> dict:
    db = get_db()
    query = {} if not status or status == "all" else {"status": status}
    rows = await db["ai_alerts"].find(query).sort("score", -1).limit(limit).to_list(length=limit)

    for r in rows:
        r["_id"] = str(r["_id"])
        for key in ("firstSeen", "createdAt", "updatedAt"):
            if hasattr(r.get(key), "isoformat"):
                r[key] = r[key].isoformat()

    return {
        "success": True,
        "count": len(rows),
        "highSeverityCount": sum(1 for r in rows if r.get("severity") == "high"),
        "alerts": rows,
    }


async def act_on_alert(alert_id: str, payload: AIAlertActionRequest, admin_id: str) -> dict:
    """Handles the Dispatch / Mark Benign / Escalate buttons on each alert card."""
    db = get_db()
    alert = await db["ai_alerts"].find_one({"alertId": alert_id})
    if not alert:
        raise HTTPException(status_code=404, detail="AI alert not found")

    now = datetime.utcnow()
    updates = {"updatedAt": now, "actionedBy": admin_id, "actionNote": payload.note}
    result_extra: dict = {}

    if payload.action == "benign":
        updates["status"] = "benign"

    elif payload.action == "dispatch":
        if not payload.officerId:
            raise HTTPException(status_code=400, detail="officerId is required when dispatching")
        officer = await db["officers"].find_one({"officerId": payload.officerId})
        if not officer:
            raise HTTPException(status_code=404, detail="Officer not found")

        updates["status"] = "dispatched"
        updates["assignedOfficerId"] = payload.officerId

        # Dispatching creates a real incident so it flows into the normal
        # SOS/incident workflow instead of living only inside the AI screen.
        last = await db["Live locations"].find_one({"userId": alert["userId"]}, sort=[("recordedAt", -1)])
        coords = ((last or {}).get("snappedLocation") or {}).get("coordinates") or (last or {}).get("rawLocation", {}).get("coordinates") or [0, 0]

        incident_id = await next_sequential_id("incidents", "incidentId", "INC")
        await db["incidents"].insert_one(
            {
                "incidentId": incident_id,
                "userId": alert["userId"],
                "tripId": None,
                "type": "manual_report",
                "category": "other",
                "severity": "high" if alert.get("severity") == "high" else "medium",
                "status": "responding",
                "location": {"type": "Point", "coordinates": coords},
                "description": f"Dispatched from AI alert {alert_id}: {alert.get('title')} - {alert.get('detail')}",
                "assignedOfficerId": payload.officerId,
                "respondedAt": now,
                "resolvedAt": None,
                "efirId": None,
                "createdAt": now,
                "updatedAt": now,
            }
        )
        updates["incidentId"] = incident_id
        result_extra["incidentId"] = incident_id

    elif payload.action == "escalate":
        updates["status"] = "escalated"
        updates["score"] = min(100, alert.get("score", 50) + 15)
        updates["severity"] = "high"

    updated = await db["ai_alerts"].find_one_and_update({"alertId": alert_id}, {"$set": updates}, return_document=True)
    updated["_id"] = str(updated["_id"])
    for key in ("firstSeen", "createdAt", "updatedAt"):
        if hasattr(updated.get(key), "isoformat"):
            updated[key] = updated[key].isoformat()

    await sio.emit("ai:alert-update", updated, room="admin-room")
    return {"success": True, "alert": updated, **result_extra}
