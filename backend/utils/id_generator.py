"""
utils/id_generator.py
Generates human-readable sequential IDs like "USER001", "TRIP014", "AI009" to
match the convention already visible in the SmartTouristDB collections.
"""
import re
from database.db import get_db


async def next_sequential_id(collection_name: str, id_field: str, prefix: str, pad_length: int = 3) -> str:
    db = get_db()
    last = await db[collection_name].find_one(
        {id_field: {"$regex": f"^{prefix}\\d+$"}}, sort=[(id_field, -1)]
    )

    next_num = 1
    if last and last.get(id_field):
        match = re.search(r"(\d+)$", last[id_field])
        if match:
            next_num = int(match.group(1)) + 1

    return f"{prefix}{str(next_num).zfill(pad_length)}"
