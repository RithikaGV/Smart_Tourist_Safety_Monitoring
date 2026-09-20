from typing import Optional, Literal
from pydantic import BaseModel


class BlockchainIdOut(BaseModel):
    blockchainId: str
    userId: str
    tripId: Optional[str] = None
    payloadHash: str
    previousHash: str
    blockHash: str
    status: Literal["active", "expired", "revoked"] = "active"
