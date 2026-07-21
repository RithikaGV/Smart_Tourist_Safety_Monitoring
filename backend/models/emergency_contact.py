from typing import Optional, Literal
from pydantic import BaseModel

FacilityType = Literal["police_station", "hospital", "fire_station", "pharmacy", "tourist_help_center"]


class EmergencyContactOut(BaseModel):
    category: Literal["helpline", "facility"]
    name: str
    facilityType: Optional[FacilityType] = None
    phone: str
    district: Optional[str] = "Nilgiris"
    address: Optional[str] = None
