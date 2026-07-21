from fastapi import APIRouter, Depends, Query

from models.live_location import LocationPingRequest
from middleware.auth import require_user
from controllers import location_controller

router = APIRouter(prefix="/api/location", tags=["location"])


@router.post("/ping")
async def ping(payload: LocationPingRequest, auth=Depends(require_user)):
    """REST fallback for devices not using the socket connection - same pipeline either way."""
    result = await location_controller.ingest_location_ping(
        user_id=auth["id"],
        trip_id=payload.tripId,
        lat=payload.lat,
        lng=payload.lng,
        speed_kmh=payload.speedKmh,
        heading=payload.heading,
        accuracy_meters=payload.accuracyMeters,
        battery_level=payload.batteryLevel,
        is_offline=payload.isOffline,
    )
    return {"success": True, **result}


@router.get("/current/{user_id}")
async def current(user_id: str, auth=Depends(require_user)):
    return await location_controller.get_current_location(user_id)


@router.get("/history/{user_id}")
async def history(user_id: str, limit: int = Query(default=100), auth=Depends(require_user)):
    return await location_controller.get_location_history(user_id, limit)


@router.get("/route-preview")
async def route_preview(
    fromLat: float = Query(...),
    fromLng: float = Query(...),
    toLat: float = Query(...),
    toLng: float = Query(...),
    auth=Depends(require_user),
):
    """Draws a road-following polyline preview before the trip is even created."""
    return await location_controller.route_preview(fromLat, fromLng, toLat, toLng)


@router.get("/snap")
async def snap(lat: float = Query(...), lng: float = Query(...), auth=Depends(require_user)):
    return await location_controller.snap_debug(lat, lng)
