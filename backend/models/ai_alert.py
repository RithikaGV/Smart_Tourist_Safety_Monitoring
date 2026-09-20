from typing import Optional, Literal
from pydantic import BaseModel, Field

AIAlertSeverity = Literal["low", "medium", "high"]
AIAlertStatus = Literal["open", "dispatched", "benign", "escalated"]

# The kinds of anomaly the AI Analytics screen surfaces
AIAlertKind = Literal[
    "unregistered_vehicle",
    "suspicious_group",
    "route_deviation",
    "prolonged_inactivity",
    "repeated_looping",
    "distress_pattern",
]


class AIAlertOut(BaseModel):
    alertId: str
    kind: AIAlertKind
    severity: AIAlertSeverity
    score: int = Field(ge=0, le=100)
    title: str
    detail: Optional[str] = None
    modelName: Optional[str] = None
    status: AIAlertStatus = "open"


class AIAlertActionRequest(BaseModel):
    """The three buttons on each AI alert card: Dispatch / Mark Benign / Escalate."""
    action: Literal["dispatch", "benign", "escalate"]
    officerId: Optional[str] = None  # required when action == "dispatch"
    note: Optional[str] = None
