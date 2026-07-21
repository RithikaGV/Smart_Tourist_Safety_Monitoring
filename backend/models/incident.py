from typing import Optional, Literal
from pydantic import BaseModel

IncidentType = Literal["sos", "geofence_breach", "inactivity", "manual_report", "crash_detected"]
IncidentStatus = Literal["open", "acknowledged", "responding", "resolved", "false_alarm"]


class IncidentOut(BaseModel):
    incidentId: str
    userId: str
    tripId: Optional[str] = None
    type: IncidentType
    severity: Literal["low", "medium", "high", "critical"] = "medium"
    status: IncidentStatus = "open"
    description: Optional[str] = None
