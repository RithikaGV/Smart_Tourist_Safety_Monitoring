from typing import Optional, Literal, List
from pydantic import BaseModel


class SOSCreateRequest(BaseModel):
    lat: float
    lng: float
    tripId: Optional[str] = None
    triggerMethod: Optional[Literal["app_button", "mesh_network", "auto_inactivity", "auto_geofence"]] = "app_button"
    batteryLevel: Optional[float] = None
    isOffline: Optional[bool] = False
    relayedBy: Optional[List[str]] = None
