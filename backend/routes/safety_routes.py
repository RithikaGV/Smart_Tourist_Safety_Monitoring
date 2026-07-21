from fastapi import APIRouter, Depends, Query

from middleware.auth import require_user
from controllers import safety_controller

router = APIRouter(prefix="/api/safety", tags=["safety"])


@router.get("/trip/{trip_id}")
async def trip_safety(trip_id: str, auth=Depends(require_user)):
    return await safety_controller.get_trip_safety(trip_id)


@router.get("/live")
async def live_safety(
    lat: float = Query(...),
    lng: float = Query(...),
    tripId: str | None = Query(default=None),
    auth=Depends(require_user),
):
    return await safety_controller.get_live_safety(auth["id"], lat, lng, tripId)
