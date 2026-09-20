from fastapi import APIRouter, Depends

from models.user import UserCreateRequest, UserLoginRequest, UserUpdateRequest
from middleware.auth import require_user
from controllers import auth_controller

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/create-account", status_code=201)
async def create_account(payload: UserCreateRequest):
    """Mirrors the 'Create Account' screen: issues a KYC record + blockchain ID immediately."""
    return await auth_controller.create_account(payload)


@router.post("/login")
async def login(payload: UserLoginRequest):
    return await auth_controller.login(payload)


@router.get("/me")
async def me(auth=Depends(require_user)):
    return await auth_controller.get_me(auth["id"])


@router.patch("/me")
async def update_me(payload: UserUpdateRequest, auth=Depends(require_user)):
    return await auth_controller.update_me(auth["id"], payload)
