"""
blockchain/chain.py
--------------------
Simulates a lightweight append-only hash chain (each block links to the
previous block's hash) to give the "blockchain-based KYC" property without
requiring a real chain/node for the hackathon prototype:

    blockHash = sha256(payloadHash + previousHash + timestamp)

Any edit to a past block breaks every hash after it, which is the
tamper-evidence property that matters for the demo/judging. Swap the body of
`issue_blockchain_id` for a real chain client (Polygon, Hyperledger Fabric)
later - callers (controllers/auth_controller.py) don't need to change.
"""
import hashlib
import json
import secrets
import time
from datetime import datetime
from typing import Optional

from database.db import get_db


def sha256(data: dict) -> str:
    return hashlib.sha256(json.dumps(data, sort_keys=True, default=str).encode()).hexdigest()


def random_suffix(length: int = 8) -> str:
    return secrets.token_hex(length)[:length].upper()


async def issue_blockchain_id(user_id: str, kyc_payload: dict, trip_id: Optional[str] = None, valid_until=None) -> dict:
    db = get_db()
    payload_hash = sha256(kyc_payload)

    last_block = await db["blockchain_ids"].find_one(sort=[("createdAt", -1)])
    previous_hash = last_block["blockHash"] if last_block else "0"

    block_hash = sha256({"payloadHash": payload_hash, "previousHash": previous_hash, "ts": time.time()})
    blockchain_id = f"BLCK-{random_suffix(8)}"

    now = datetime.utcnow()
    record = {
        "blockchainId": blockchain_id,
        "userId": user_id,
        "tripId": trip_id,
        "payloadHash": payload_hash,
        "previousHash": previous_hash,
        "blockHash": block_hash,
        "issuedAt": now,
        "validUntil": valid_until,
        "status": "active",
        "createdAt": now,
        "updatedAt": now,
    }
    await db["blockchain_ids"].insert_one(record)
    return record


async def verify_chain() -> dict:
    """Verifies the integrity of the whole chain - used by the admin panel."""
    db = get_db()
    blocks = await db["blockchain_ids"].find().sort("createdAt", 1).to_list(length=None)

    for i in range(1, len(blocks)):
        if blocks[i]["previousHash"] != blocks[i - 1]["blockHash"]:
            return {"valid": False, "brokenAt": blocks[i]["blockchainId"]}
    return {"valid": True, "blocks": len(blocks)}
