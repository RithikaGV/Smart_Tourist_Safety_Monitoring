from typing import Optional
from pydantic import BaseModel, EmailStr


class OfficerLoginRequest(BaseModel):
    email: EmailStr
    password: str


class OfficerOut(BaseModel):
    officerId: str
    name: str
    badgeNumber: Optional[str] = None
    email: EmailStr
    station: Optional[str] = None
    jurisdiction: Optional[str] = "Nilgiris"
    onDuty: bool = True
