from fastapi import APIRouter, Depends, Query

from models.geofence import GeofenceCreateRequest, GeofenceUpdateRequest
from middleware.auth import require_user, require_admin
from controllers import geofence_controller

router = APIRouter(prefix="/api/geofences", tags=["geofences"])


@router.get("/")
async def list_geofences(auth=Depends(require_user)):
    return await geofence_controller.list_geofences()


@router.get("/check")
async def check(lat: float = Query(...), lng: float = Query(...), auth=Depends(require_user)):
    return await geofence_controller.check_point(lat, lng)


@router.post("/", status_code=201)
async def create_geofence(payload: GeofenceCreateRequest, auth=Depends(require_admin)):
    return await geofence_controller.create_geofence(payload)


@router.patch("/{geofence_id}")
async def update_geofence(geofence_id: str, payload: GeofenceUpdateRequest, auth=Depends(require_admin)):
    return await geofence_controller.update_geofence(geofence_id, payload)


@router.delete("/{geofence_id}")
async def delete_geofence(geofence_id: str, auth=Depends(require_admin)):
    return await geofence_controller.delete_geofence(geofence_id)
