from typing import Literal
from pydantic import BaseModel

RiskBand = Literal["Low", "Medium", "High"]


class AISafetyOut(BaseModel):
    aiSafetyId: str
    tripId: str
    userId: str
    overallSafetyScore: float
    crimeRisk: RiskBand
    womenSafety: RiskBand
    weatherRisk: RiskBand
    nightSafety: RiskBand
