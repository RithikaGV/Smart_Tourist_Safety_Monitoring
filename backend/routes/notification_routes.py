from fastapi import APIRouter, Depends

from middleware.auth import require_user
from controllers import notification_controller

router = APIRouter(prefix="/api/notifications", tags=["notifications"])


@router.get("/")
async def list_notifications(auth=Depends(require_user)):
    return await notification_controller.list_notifications(auth["id"])


@router.patch("/{notification_id}/read")
async def mark_read(notification_id: str, auth=Depends(require_user)):
    return await notification_controller.mark_read(auth["id"], notification_id)
