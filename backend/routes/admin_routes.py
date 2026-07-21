from fastapi import APIRouter, Depends

from models.admin import AdminLoginRequest
from middleware.auth import require_admin
from controllers import admin_controller

router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.post("/login")
async def login(payload: AdminLoginRequest):
    return await admin_controller.admin_login(payload)


@router.get("/dashboard-summary")
async def dashboard_summary(auth=Depends(require_admin)):
    """Starter aggregate endpoint for the Command Center panel - active tourists, open incidents, pending SOS."""
    return await admin_controller.dashboard_summary()
