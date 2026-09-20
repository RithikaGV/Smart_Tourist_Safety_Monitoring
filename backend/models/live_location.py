from typing import Optional
from pydantic import BaseModel


class LocationPingRequest(BaseModel):
    lat: float
    lng: float
    tripId: Optional[str] = None
    speedKmh: Optional[float] = None
    heading: Optional[float] = None
    accuracyMeters: Optional[float] = None
    batteryLevel: Optional[float] = None
    isOffline: Optional[bool] = False
