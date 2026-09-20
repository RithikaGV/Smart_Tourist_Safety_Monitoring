from typing import Optional, Literal
from pydantic import BaseModel, EmailStr


class AdminLoginRequest(BaseModel):
    email: EmailStr
    password: str


class AdminOut(BaseModel):
    adminId: str
    name: str
    email: EmailStr
    role: Literal["super_admin", "district_admin", "analyst"] = "district_admin"
    district: Optional[str] = "Nilgiris"
