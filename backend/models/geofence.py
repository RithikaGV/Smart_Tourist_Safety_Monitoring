from typing import Optional, Literal, List
from pydantic import BaseModel

GeofenceType = Literal["restricted", "tribal_sacred_site", "high_risk", "safe_zone", "wildlife_zone"]
Severity = Literal["low", "medium", "high", "critical"]


class GeofenceCreateRequest(BaseModel):
    name: str
    type: GeofenceType
    description: Optional[str] = None
    severity: Severity = "medium"
    district: Optional[str] = "Nilgiris"
    alertMessage: Optional[str] = "You are entering a restricted/sensitive zone."
    # GeoJSON Polygon coordinates: [ [ [lng,lat], ... , [lng,lat] ] ] (ring must close)
    coordinates: List[List[List[float]]]


class GeofenceUpdateRequest(BaseModel):
    name: Optional[str] = None
    type: Optional[GeofenceType] = None
    description: Optional[str] = None
    severity: Optional[Severity] = None
    active: Optional[bool] = None
    alertMessage: Optional[str] = None
