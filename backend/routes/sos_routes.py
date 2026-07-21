from fastapi import APIRouter, Depends, Query

from models.sos_request import SOSCreateRequest
from middleware.auth import require_user, require_admin, require_officer
from controllers import sos_controller

router = APIRouter(prefix="/api/sos", tags=["sos"])


@router.post("/", status_code=201)
async def create_sos(payload: SOSCreateRequest, auth=Depends(require_user)):
    return await sos_controller.create_sos(auth["id"], payload)


@router.get("/mine")
async def mine(auth=Depends(require_user)):
    return await sos_controller.my_sos(auth["id"])


@router.get("/")
async def list_sos(status: str | None = Query(default=None), auth=Depends(require_admin)):
    return await sos_controller.list_sos(status)


@router.patch("/{sos_id}/acknowledge")
async def acknowledge(sos_id: str, auth=Depends(require_officer)):
    return await sos_controller.acknowledge_sos(sos_id, auth["id"])


@router.patch("/{sos_id}/resolve")
async def resolve(sos_id: str, auth=Depends(require_officer)):
    return await sos_controller.resolve_sos(sos_id)
