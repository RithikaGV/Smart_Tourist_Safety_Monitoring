from typing import Optional, Literal
from pydantic import BaseModel


class KYCOut(BaseModel):
    kycId: str
    userId: str
    idType: Literal["Aadhaar", "Passport", "DrivingLicense", "VoterID"] = "Aadhaar"
    verificationStatus: Literal["pending", "verified", "rejected"] = "pending"
    verifiedBy: Optional[str] = None
