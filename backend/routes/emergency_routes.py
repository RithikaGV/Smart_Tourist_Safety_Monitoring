from fastapi import APIRouter, Depends, Query

from middleware.auth import require_user
from controllers import emergency_controller

router = APIRouter(prefix="/api/emergency-contacts", tags=["emergency-contacts"])


@router.get("/helplines")
async def helplines(auth=Depends(require_user)):
    return await emergency_controller.list_helplines()


@router.get("/nearby")
async def nearby(
    type: str = Query(...),
    lat: float = Query(...),
    lng: float = Query(...),
    radiusKm: float = Query(default=15),
    auth=Depends(require_user),
):
    return await emergency_controller.nearby_facilities(type, lat, lng, radiusKm)
