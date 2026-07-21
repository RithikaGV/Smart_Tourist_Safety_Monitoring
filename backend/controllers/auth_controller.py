"""
controllers/auth_controller.py
Business logic for signup/login/profile. Routes stay thin and just call these.
"""
import os
import bcrypt
from datetime import datetime, timedelta
from jose import jwt
from fastapi import HTTPException

from database.db import get_db
from utils.id_generator import next_sequential_id
from blockchain.chain import issue_blockchain_id
from models.user import UserCreateRequest, UserLoginRequest, UserUpdateRequest

# Using bcrypt directly (rather than passlib's CryptContext wrapper) - passlib's
# bcrypt backend has a known incompatibility with bcrypt>=4.1 (raises on the
# library's own internal self-test). Talking to bcrypt directly avoids it.


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))


def sign_user_token(user: dict) -> str:
    expires_minutes = int(os.getenv("JWT_EXPIRES_MINUTES", "10080"))
    payload = {
        "id": user["userId"],
        "role": "user",
        "email": user["email"],
        "exp": datetime.utcnow() + timedelta(minutes=expires_minutes),
    }
    return jwt.encode(payload, os.getenv("JWT_SECRET"), algorithm=os.getenv("JWT_ALGORITHM", "HS256"))


def _public_user(user: dict) -> dict:
    return {
        "userId": user["userId"],
        "fullName": user["fullName"],
        "email": user["email"],
        "blockchainId": user.get("blockchainId"),
        "kycStatus": user.get("kycStatus", "pending"),
    }


async def create_account(payload: UserCreateRequest) -> dict:
    db = get_db()

    existing = await db["users"].find_one({"email": payload.email.lower()})
    if existing:
        raise HTTPException(status_code=409, detail="An account with this email already exists")

    user_id = await next_sequential_id("users", "userId", "USER")
    now = datetime.utcnow()

    user = {
        "userId": user_id,
        "fullName": payload.fullName,
        "email": payload.email.lower(),
        "mobileNumber": payload.mobileNumber,
        "passwordHash": hash_password(payload.password),
        "dateOfBirth": datetime.combine(payload.dateOfBirth, datetime.min.time()) if payload.dateOfBirth else None,
        "gender": payload.gender,
        "nationality": payload.nationality,
        "preferredLanguage": payload.preferredLanguage,
        "blockchainId": None,
        "kycStatus": "pending",
        "emergencyContacts": [],
        "isActive": True,
        "lastLoginAt": now,
        "createdAt": now,
        "updatedAt": now,
    }
    await db["users"].insert_one(user)

    # KYC record (raw ID number is never stored - only referenced via the blockchain payload hash)
    kyc_id = await next_sequential_id("kyc", "kycId", "KYC")
    await db["kyc"].insert_one(
        {
            "kycId": kyc_id,
            "userId": user_id,
            "idType": payload.idType,
            "verificationStatus": "pending",
            "createdAt": now,
            "updatedAt": now,
        }
    )

    block_record = await issue_blockchain_id(
        user_id=user_id,
        kyc_payload={
            "userId": user_id,
            "email": payload.email.lower(),
            "idType": payload.idType,
            "idNumber": payload.idNumber,
            "ts": now.isoformat(),
        },
    )

    await db["users"].update_one({"userId": user_id}, {"$set": {"blockchainId": block_record["blockchainId"]}})
    user["blockchainId"] = block_record["blockchainId"]

    token = sign_user_token(user)
    return {
        "success": True,
        "message": "You have successfully logged in. Your KYC/Blockchain ID has been created.",
        "token": token,
        "user": _public_user(user),
    }


async def login(payload: UserLoginRequest) -> dict:
    db = get_db()
    user = await db["users"].find_one({"email": payload.email.lower()})
    if not user or not verify_password(payload.password, user["passwordHash"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    await db["users"].update_one({"userId": user["userId"]}, {"$set": {"lastLoginAt": datetime.utcnow()}})

    token = sign_user_token(user)
    return {"success": True, "token": token, "user": _public_user(user)}


async def get_me(user_id: str) -> dict:
    db = get_db()
    user = await db["users"].find_one({"userId": user_id}, {"passwordHash": 0})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user["_id"] = str(user["_id"])
    return {"success": True, "user": user}


async def update_me(user_id: str, payload: UserUpdateRequest) -> dict:
    db = get_db()
    updates = {k: v for k, v in payload.model_dump(exclude_unset=True).items() if v is not None}
    updates["updatedAt"] = datetime.utcnow()

    await db["users"].update_one({"userId": user_id}, {"$set": updates})
    user = await db["users"].find_one({"userId": user_id}, {"passwordHash": 0})
    user["_id"] = str(user["_id"])
    return {"success": True, "user": user}
