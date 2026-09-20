from typing import Optional, Literal
from pydantic import BaseModel

# How the incident was raised (internal origin)
IncidentType = Literal["sos", "geofence_breach", "inactivity", "manual_report", "crash_detected"]

# What kind of incident it is - these are the categories the admin panel's
# "Incident Stats (This Month)" chart groups by.
IncidentCategory = Literal["theft", "harassment", "accident", "missing", "fraud", "medical", "other"]

# Internal lifecycle. The admin panel collapses these into three buckets
# (Pending / Investigating / Closed) - see utils/status_map.py.
IncidentStatus = Literal["open", "acknowledged", "responding", "resolved", "false_alarm"]

Priority = Literal["low", "medium", "high"]


class IncidentOut(BaseModel):
    incidentId: str
    userId: str
    tripId: Optional[str] = None
    type: IncidentType
    category: IncidentCategory = "other"
    severity: Literal["low", "medium", "high", "critical"] = "medium"
    status: IncidentStatus = "open"
    description: Optional[str] = None
    assignedOfficerId: Optional[str] = None
    locationName: Optional[str] = None


class IncidentCreateRequest(BaseModel):
    """Admin/officer manually filing an incident from the panel."""
    userId: str
    category: IncidentCategory
    lat: float
    lng: float
    locationName: Optional[str] = None
    description: Optional[str] = None
    severity: Literal["low", "medium", "high", "critical"] = "medium"
    tripId: Optional[str] = None


class IncidentStatusUpdateRequest(BaseModel):
    """Maps the admin panel's three status buttons onto the internal lifecycle."""
    status: Literal["pending", "investigating", "closed"]
    note: Optional[str] = None


class AssignOfficerRequest(BaseModel):
    officerId: str
