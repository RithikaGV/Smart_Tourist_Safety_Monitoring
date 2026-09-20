from fastapi import APIRouter, Depends

from models.trip import TripCreateRequest, TripUpdateRequest
from middleware.auth import require_user
from controllers import trip_controller

router = APIRouter(prefix="/api/trips", tags=["trips"])


@router.post("/", status_code=201)
async def create_trip(payload: TripCreateRequest, auth=Depends(require_user)):
    return await trip_controller.create_trip(auth["id"], payload)


@router.get("/")
async def list_trips(auth=Depends(require_user)):
    return await trip_controller.list_my_trips(auth["id"])


@router.get("/{trip_id}")
async def get_trip(trip_id: str, auth=Depends(require_user)):
    return await trip_controller.get_trip(auth["id"], trip_id)


@router.patch("/{trip_id}")
async def update_trip(trip_id: str, payload: TripUpdateRequest, auth=Depends(require_user)):
    return await trip_controller.update_trip(auth["id"], trip_id, payload)


@router.delete("/{trip_id}")
async def delete_trip(trip_id: str, auth=Depends(require_user)):
    return await trip_controller.delete_trip(auth["id"], trip_id)


@router.post("/{trip_id}/start")
async def start_trip(trip_id: str, auth=Depends(require_user)):
    return await trip_controller.start_trip(auth["id"], trip_id)


@router.post("/{trip_id}/end")
async def end_trip(trip_id: str, auth=Depends(require_user)):
    return await trip_controller.end_trip(auth["id"], trip_id)
