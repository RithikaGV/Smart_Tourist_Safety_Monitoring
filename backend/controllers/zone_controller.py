"""
controllers/zone_controller.py
-------------------------------
Backs the admin panel's "Zone Management" screen.

Key design point: the admin draws a zone as a CENTER + RADIUS (simpler for an
officer than clicking out a polygon), but the tourist-side geofence pipeline
(utils/geofence_check.py) does point-in-polygon against GeoJSON polygons. So on
save we approximate the circle as a many-sided polygon and store it in the SAME
`geofences` collection the tourist app already reads.

That means a zone an officer creates here is immediately live for every tourist
- no separate collection, no sync step, no duplicated logic.
"""
import math
from datetime import datetime

from fastapi import HTTPException

from database.db import get_db
from utils.id_generator import next_sequential_id
from utils.socket_manager import sio
from utils.geofence_check import find_geofences_containing
from models.zone import ZoneCreateRequest, ZoneUpdateRequest

# Admin panel zone type -> tourist-side geofence type (models/geofence.py)
ZONE_TYPE_TO_GEOFENCE_TYPE = {
    "landslide_area": "high_risk",
    "restricted_zone": "restricted",
    "wildlife_zone": "wildlife_zone",
    "tribal_sacred_site": "tribal_sacred_site",
    "high_risk": "high_risk",
    "crowded_area": "high_risk",
    "safe_zone": "safe_zone",
}

DEFAULT_ALERTS = {
    "landslide_area": "Landslide-prone area. Avoid during and after heavy rain.",
    "restricted_zone": "Restricted zone - entry requires prior permission.",
    "wildlife_zone": "Protected wildlife zone. Stay on designated routes.",
    "tribal_sacred_site": "Tribal sacred site. Please be respectful; entry may require local permission.",
    "high_risk": "High-risk area. Exercise extreme caution.",
    "crowded_area": "Heavily crowded area. Watch your belongings and stay with your group.",
    "safe_zone": "You are in a monitored safe zone.",
}


def circle_to_polygon(lat: float, lng: float, radius_meters: float, sides: int = 32):
    """Approximates a circle as a closed GeoJSON polygon ring.

    Latitude degrees are a near-constant ~111,320 m apart everywhere, but
    longitude degrees shrink as you move away from the equator (by cos(lat)),
    so the two axes need different scaling or the "circle" comes out as an
    ellipse on the map.
    """
    lat_deg_per_meter = 1 / 111_320
    lng_deg_per_meter = 1 / (111_320 * math.cos(math.radians(lat)) or 1e-9)

    ring = []
    for i in range(sides):
        theta = 2 * math.pi * i / sides
        d_lat = radius_meters * math.sin(theta) * lat_deg_per_meter
        d_lng = radius_meters * math.cos(theta) * lng_deg_per_meter
        ring.append([lng + d_lng, lat + d_lat])
    ring.append(ring[0])  # close the ring
    return [ring]


def _decorate_zone(doc: dict) -> dict:
    """Shapes a stored geofence document into what the Zone Management table wants."""
    if not doc:
        return doc
    doc["_id"] = str(doc.get("_id", ""))
    meta = doc.get("adminZone") or {}
    doc["zoneType"] = meta.get("zoneType")
    doc["latitude"] = meta.get("latitude")
    doc["longitude"] = meta.get("longitude")
    doc["radiusMeters"] = meta.get("radiusMeters")
    doc["zoneStatus"] = meta.get("zoneStatus", "active" if doc.get("active") else "archived")
    return doc


async def list_zones() -> dict:
    db = get_db()
    zones = await db["geofences"].find().sort("createdAt", -1).to_list(length=None)
    return {"success": True, "zones": [_decorate_zone(z) for z in zones]}


async def create_zone(payload: ZoneCreateRequest, admin_id: str) -> dict:
    db = get_db()
    geofence_id = await next_sequential_id("geofences", "geofenceId", "GEO")
    now = datetime.utcnow()

    geofence_type = ZONE_TYPE_TO_GEOFENCE_TYPE.get(payload.type, "restricted")
    alert_message = payload.alertMessage or DEFAULT_ALERTS.get(payload.type, "Sensitive zone - proceed with caution.")

    zone = {
        "geofenceId": geofence_id,
        "name": payload.name,
        "type": geofence_type,
        "description": f"{payload.type.replace('_', ' ').title()} zone created from the admin panel.",
        "severity": payload.severity,
        "district": payload.district,
        "alertMessage": alert_message,
        "area": {"type": "Polygon", "coordinates": circle_to_polygon(payload.latitude, payload.longitude, payload.radiusMeters)},
        # A "draft" zone is stored but NOT active, so it doesn't fire alerts at
        # tourists until an officer flips it to active.
        "active": payload.status == "active",
        "adminZone": {
            "zoneType": payload.type,
            "zoneStatus": payload.status,
            "latitude": payload.latitude,
            "longitude": payload.longitude,
            "radiusMeters": payload.radiusMeters,
            "createdByAdminId": admin_id,
        },
        "createdAt": now,
        "updatedAt": now,
    }
    await db["geofences"].insert_one(zone)

    alerted = 0
    if payload.pushInstantAlert and payload.status == "active":
        alerted = await _push_zone_alert(zone, alert_message)

    await sio.emit("zone:created", _decorate_zone(dict(zone)), room="admin-room")

    return {"success": True, "zone": _decorate_zone(zone), "touristsAlerted": alerted}


async def update_zone(geofence_id: str, payload: ZoneUpdateRequest) -> dict:
    db = get_db()
    existing = await db["geofences"].find_one({"geofenceId": geofence_id})
    if not existing:
        raise HTTPException(status_code=404, detail="Zone not found")

    data = payload.model_dump(exclude_unset=True)
    updates: dict = {"updatedAt": datetime.utcnow()}
    admin_meta = dict(existing.get("adminZone") or {})

    if "name" in data and data["name"]:
        updates["name"] = data["name"]
    if "severity" in data and data["severity"]:
        updates["severity"] = data["severity"]
    if "alertMessage" in data and data["alertMessage"]:
        updates["alertMessage"] = data["alertMessage"]
    if "type" in data and data["type"]:
        updates["type"] = ZONE_TYPE_TO_GEOFENCE_TYPE.get(data["type"], "restricted")
        admin_meta["zoneType"] = data["type"]
    if "status" in data and data["status"]:
        updates["active"] = data["status"] == "active"
        admin_meta["zoneStatus"] = data["status"]

    # If any geometry field changed, rebuild the polygon from the new circle.
    lat = data.get("latitude", admin_meta.get("latitude"))
    lng = data.get("longitude", admin_meta.get("longitude"))
    radius = data.get("radiusMeters", admin_meta.get("radiusMeters"))
    if any(k in data for k in ("latitude", "longitude", "radiusMeters")) and lat is not None and lng is not None and radius:
        updates["area"] = {"type": "Polygon", "coordinates": circle_to_polygon(lat, lng, radius)}
        admin_meta.update({"latitude": lat, "longitude": lng, "radiusMeters": radius})

    updates["adminZone"] = admin_meta

    zone = await db["geofences"].find_one_and_update(
        {"geofenceId": geofence_id}, {"$set": updates}, return_document=True
    )
    await sio.emit("zone:updated", _decorate_zone(dict(zone)), room="admin-room")
    return {"success": True, "zone": _decorate_zone(zone)}


async def delete_zone(geofence_id: str) -> dict:
    db = get_db()
    result = await db["geofences"].delete_one({"geofenceId": geofence_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Zone not found")
    await sio.emit("zone:deleted", {"geofenceId": geofence_id}, room="admin-room")
    return {"success": True, "message": "Zone removed"}


async def _push_zone_alert(zone: dict, message: str) -> int:
    """Notifies every tourist whose last known position falls inside this zone.

    We look at each active tourist's most recent `Live locations` ping rather
    than scanning the whole history - that's the only position that matters for
    "who is in danger right now".
    """
    db = get_db()
    now = datetime.utcnow()

    recent_user_ids = await db["Live locations"].distinct("userId")
    alerted = 0

    for user_id in recent_user_ids:
        last = await db["Live locations"].find_one({"userId": user_id}, sort=[("recordedAt", -1)])
        if not last:
            continue

        coords = (last.get("snappedLocation") or {}).get("coordinates") or last["rawLocation"]["coordinates"]
        lng, lat = coords[0], coords[1]

        hits = await find_geofences_containing(lat, lng)
        if not any(h["geofenceId"] == zone["geofenceId"] for h in hits):
            continue

        await db["notifications"].insert_one(
            {
                "userId": user_id,
                "title": f"Zone Alert: {zone['name']}",
                "message": message,
                "type": "geofence_alert",
                "read": False,
                "meta": {"geofenceId": zone["geofenceId"], "pushedByAdmin": True},
                "createdAt": now,
                "updatedAt": now,
            }
        )
        await sio.emit(
            "zone:alert",
            {"geofenceId": zone["geofenceId"], "name": zone["name"], "message": message, "severity": zone.get("severity")},
            room=f"user-{user_id}",
        )
        alerted += 1

    return alerted


async def push_alert_for_zone(geofence_id: str, message: str | None) -> dict:
    db = get_db()
    zone = await db["geofences"].find_one({"geofenceId": geofence_id})
    if not zone:
        raise HTTPException(status_code=404, detail="Zone not found")

    text = message or zone.get("alertMessage") or f"Safety alert for {zone['name']}."
    alerted = await _push_zone_alert(zone, text)
    return {"success": True, "touristsAlerted": alerted, "message": text}
