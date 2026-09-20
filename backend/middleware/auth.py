"""
middleware/auth.py
FastAPI dependencies that verify a Bearer JWT and attach the decoded payload
as `request.state`-style return value. Use as:

    @router.get("/me")
    async def me(auth = Depends(require_user)):
        user_id = auth["id"]
"""
import os
from fastapi import Header, HTTPException
from jose import jwt, JWTError

ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")


def _make_auth_dependency(secret_env_var: str, role: str):
    async def dependency(authorization: str | None = Header(default=None)):
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Missing Authorization Bearer token")

        token = authorization.split(" ", 1)[1]
        secret = os.getenv(secret_env_var)
        try:
            payload = jwt.decode(token, secret, algorithms=[ALGORITHM])
        except JWTError:
            raise HTTPException(status_code=401, detail="Invalid or expired token")

        if role and payload.get("role") != role:
            raise HTTPException(status_code=403, detail=f"Token is not valid for role '{role}'")

        return payload

    return dependency


require_user = _make_auth_dependency("JWT_SECRET", "user")
require_admin = _make_auth_dependency("ADMIN_JWT_SECRET", "admin")
require_officer = _make_auth_dependency("OFFICER_JWT_SECRET", "officer")
