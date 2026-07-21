"""
models/user.py
Pydantic schemas for the `users` collection. These are used for request
validation and response shaping - Mongo documents are plain dicts under the
hood (see controllers/auth_controller.py).
"""
from datetime import date, datetime
from typing import Optional, Literal
from pydantic import BaseModel, EmailStr, Field


class EmergencyContactRef(BaseModel):
    name: str
    relation: str
    phone: str


class UserCreateRequest(BaseModel):
    fullName: str
    email: EmailStr
    mobileNumber: str
    password: str = Field(min_length=8)
    dateOfBirth: Optional[date] = None
    gender: Optional[Literal["Male", "Female", "Other", "Prefer not to say"]] = "Prefer not to say"
    nationality: Optional[str] = "Indian"
    preferredLanguage: Optional[str] = "English"
    idType: Optional[Literal["Aadhaar", "Passport", "DrivingLicense", "VoterID"]] = "Aadhaar"
    idNumber: Optional[str] = None


class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserUpdateRequest(BaseModel):
    fullName: Optional[str] = None
    mobileNumber: Optional[str] = None
    gender: Optional[str] = None
    nationality: Optional[str] = None
    preferredLanguage: Optional[str] = None
    dateOfBirth: Optional[date] = None


class UserOut(BaseModel):
    userId: str
    fullName: str
    email: EmailStr
    mobileNumber: Optional[str] = None
    blockchainId: Optional[str] = None
    kycStatus: str = "pending"
    dateOfBirth: Optional[datetime] = None
    gender: Optional[str] = None
    nationality: Optional[str] = None
    preferredLanguage: Optional[str] = None
