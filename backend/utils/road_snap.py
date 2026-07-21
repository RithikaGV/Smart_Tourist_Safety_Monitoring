"""
utils/road_snap.py
Talks to OSRM (https://project-osrm.org) to:
  - snap a single raw GPS point onto the nearest road (/nearest)
  - match a recent GPS trail onto the road network (/match)
  - compute a full driving route between two points for trip preview (/route)

Defaults to the free public demo server. For production, self-host OSRM with
a Tamil Nadu OSM extract and set OSRM_BASE_URL - no other code changes needed.
"""
import os
import httpx

OSRM_BASE_URL = os.getenv("OSRM_BASE_URL", "https://router.project-osrm.org")


async def snap_point_to_road(lng: float, lat: float) -> dict | None:
    url = f"{OSRM_BASE_URL}/nearest/v1/driving/{lng},{lat}"
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            resp = await client.get(url, params={"number": 1})
            data = resp.json()
        if data.get("code") != "Ok" or not data.get("waypoints"):
            return None
        wp = data["waypoints"][0]
        return {
            "coordinates": wp["location"],  # [lng, lat]
            "distanceMeters": wp["distance"],
            "roadName": wp.get("name") or None,
        }
    except Exception as err:
        print(f"[roadSnap] snap_point_to_road failed: {err}")
        return None


async def match_trace_to_roads(points: list[dict]) -> dict | None:
    """points: [{lng, lat, timestamp(ms)}...] ordered oldest -> newest, min 2 points."""
    if not points or len(points) < 2:
        return None
    try:
        coords_str = ";".join(f"{p['lng']},{p['lat']}" for p in points)
        timestamps = ";".join(str(round(p["timestamp"] / 1000)) for p in points)
        url = f"{OSRM_BASE_URL}/match/v1/driving/{coords_str}"
        async with httpx.AsyncClient(timeout=8) as client:
            resp = await client.get(
                url, params={"geometries": "geojson", "timestamps": timestamps, "overview": "full"}
            )
            data = resp.json()
        if data.get("code") != "Ok" or not data.get("matchings"):
            return None
        m = data["matchings"][0]
        return {
            "geometry": m["geometry"],
            "distanceMeters": m["distance"],
            "durationSeconds": m["duration"],
            "matchedPoints": data.get("tracepoints"),
        }
    except Exception as err:
        print(f"[roadSnap] match_trace_to_roads failed: {err}")
        return None


async def get_route(waypoints: list[dict], profile: str = "driving") -> dict | None:
    """waypoints: [{lng, lat}, ...] in order, min 2 points."""
    if not waypoints or len(waypoints) < 2:
        return None
    try:
        coords_str = ";".join(f"{p['lng']},{p['lat']}" for p in waypoints)
        url = f"{OSRM_BASE_URL}/route/v1/{profile}/{coords_str}"
        async with httpx.AsyncClient(timeout=8) as client:
            resp = await client.get(url, params={"geometries": "geojson", "overview": "full", "steps": "false"})
            data = resp.json()
        if data.get("code") != "Ok" or not data.get("routes"):
            return None
        route = data["routes"][0]
        return {
            "geometry": route["geometry"],  # GeoJSON LineString - feed straight into Leaflet
            "distanceMeters": route["distance"],
            "durationSeconds": route["duration"],
        }
    except Exception as err:
        print(f"[roadSnap] get_route failed: {err}")
        return None
