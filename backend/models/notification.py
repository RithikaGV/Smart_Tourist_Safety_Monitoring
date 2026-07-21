from typing import Optional, Literal, Any, Dict
from pydantic import BaseModel

NotificationType = Literal[
    "geofence_alert", "weather_alert", "sos_update", "trip_reminder", "safety_score_update", "system"
]


class NotificationOut(BaseModel):
    userId: str
    title: str
    message: str
    type: NotificationType = "system"
    read: bool = False
    meta: Optional[Dict[str, Any]] = None
