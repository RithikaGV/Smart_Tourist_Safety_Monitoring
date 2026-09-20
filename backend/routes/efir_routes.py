from fastapi import APIRouter, Depends

from models.efir import EFIRGenerateRequest
from middleware.auth import require_officer, require_admin
from controllers import efir_controller

router = APIRouter(prefix="/api/efir", tags=["efir"])


@router.post("/generate/{incident_id}", status_code=201)
async def generate(incident_id: str, payload: EFIRGenerateRequest, auth=Depends(require_officer)):
    return await efir_controller.generate_efir_for_incident(incident_id, payload.stationJurisdiction)


@router.get("/")
async def list_efirs(auth=Depends(require_admin)):
    return await efir_controller.list_efirs()


@router.get("/{efir_id}")
async def get_efir(efir_id: str, auth=Depends(require_admin)):
    return await efir_controller.get_efir(efir_id)
