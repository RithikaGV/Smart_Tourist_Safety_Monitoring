"""
utils/geofence_check.py
Point-in-polygon checks against the `geofences` collection using Shapely
(Python's equivalent of turf.js for this purpose).
"""
from shapely.geometry import shape, Point
from database.db import get_db


async def find_geofences_containing(lat: float, lng: float) -> list[dict]:
    db = get_db()
    geofences = await db["geofences"].find({"active": True}).to_list(length=None)

    pt = Point(lng, lat)  # GeoJSON order is [lng, lat]
    hits = []
    for gf in geofences:
        try:
            polygon = shape(gf["area"])  # area is a GeoJSON Polygon dict
            if polygon.contains(pt):
                hits.append(gf)
        except Exception as err:
            print(f"[geofenceCheck] skipping malformed geofence {gf.get('geofenceId')}: {err}")
    return hits
