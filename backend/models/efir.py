from typing import Optional
from pydantic import BaseModel


class EFIRGenerateRequest(BaseModel):
    stationJurisdiction: Optional[str] = "Nilgiris District"
