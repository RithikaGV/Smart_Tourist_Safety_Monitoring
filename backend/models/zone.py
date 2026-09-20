from typing import Optional, Literal
from pydantic import BaseModel, Field

# Zone types as labelled in the admin panel's "Mark as (type)" dropdown.
# These map onto the tourist-side geofence types - see ZONE_TYPE_TO_GEOFENCE_TYPE
# in controllers/zone_controller.py.
ZoneType = Literal[
    "landslide_area",
    "restricted_zone",
    "wildlife_zone",
    "tribal_sacred_site",
    "high_risk",
    "crowded_area",
    "safe_zone",
]

ZoneStatus = Literal["active", "draft", "archived"]


class ZoneCreateRequest(BaseModel):
    """The admin panel draws zones as a center point + radius in metres, which is
    simpler for an officer than drawing a polygon. We convert that circle into a
    GeoJSON polygon on save so the existing tourist-side geofence pipeline
    (shapely point-in-polygon) works against it unchanged."""
    name: str
    type: ZoneType
    status: ZoneStatus = "active"
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    radiusMeters: float = Field(gt=0, le=100000)
    severity: Literal["low", "medium", "high", "critical"] = "medium"
    alertMessage: Optional[str] = None
    district: Optional[str] = "Nilgiris"
    pushInstantAlert: bool = True  # "Add Zone & Push Instant Alert" button


class ZoneUpdateRequest(BaseModel):
    name: Optional[str] = None
    type: Optional[ZoneType] = None
    status: Optional[ZoneStatus] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    radiusMeters: Optional[float] = None
    severity: Optional[str] = None
    alertMessage: Optional[str] = None


class ZoneAlertRequest(BaseModel):
    """The 'Alert' button on each zone row - pushes a notification to every
    tourist currently inside (or near) that zone."""
    message: Optional[str] = None
