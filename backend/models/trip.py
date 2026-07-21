from typing import Optional, Literal
from pydantic import BaseModel


class LatLng(BaseModel):
    lat: float
    lng: float


class TripCreateRequest(BaseModel):
    destination: str
    destinationCoords: LatLng
    originCoords: Optional[LatLng] = None  # used to build a route preview
    travelDate: str  # ISO date string, e.g. "2026-07-18"
    travelTime: Optional[str] = None  # "13:40"
    numberOfTravelers: Optional[int] = 1
    travelType: Optional[Literal["Solo", "Family", "Friends", "Business"]] = "Family"


class TripUpdateRequest(BaseModel):
    destination: Optional[str] = None
    travelDate: Optional[str] = None
    travelTime: Optional[str] = None
    numberOfTravelers: Optional[int] = None
    travelType: Optional[str] = None
    shareTripEnabled: Optional[bool] = None
