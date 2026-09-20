"""
controllers/efir_monitoring_controller.py
------------------------------------------
Backs the admin panel's "E-FIR Monitoring" screen: the table of filed FIRs with
official-style reference numbers (FIR-KR-2026-00451), the incident category tag,
the tourist's details, and the "View & Copy FIR" action that produces a plain-text
FIR an officer can paste into the state police system.
"""
from datetime import datetime, timedelta

from fastapi import HTTPException

from database.db import get_db
from utils.status_map import to_ui_status

# Station code used in the FIR reference. In a real deployment this would come
# from the officer's posting; keyed by station name here.
STATION_CODES = {
    "Ooty Town Police Station": "OT",
    "Coonoor Police Station": "CN",
    "Kotagiri Police Station": "KG",
    "Gudalur Police Station": "GD",
}
DEFAULT_STATION_CODE = "NG"  # Nilgiris

CATEGORY_LABELS = {
    "theft": "Theft of Property",
    "harassment": "Harassment",
    "accident": "Road Accident",
    "missing": "Missing Person",
    "fraud": "Fraud / Scam",
    "medical": "Medical Emergency",
    "other": "Other",
}

TIME_FILTERS = {"all": None, "24h": 1440, "7d": 10080, "30d": 43200}


def _fir_reference(efir: dict, station_code: str) -> str:
    filed = efir.get("filedAt") or efir.get("createdAt")
    year = filed.year if hasattr(filed, "year") else datetime.utcnow().year
    digits = "".join(ch for ch in efir["efirId"] if ch.isdigit()) or "0"
    serial = str(int(digits) if digits.isdigit() else 0).zfill(5)
    return f"FIR-{station_code}-{year}-{serial}"


async def _shape_efir(efir: dict, db) -> dict:
    user = await db["users"].find_one(
        {"userId": efir["userId"]}, {"fullName": 1, "mobileNumber": 1, "nationality": 1}
    )
    incident = await db["incidents"].find_one(
        {"incidentId": efir["incidentId"]}, {"category": 1, "severity": 1, "description": 1, "locationName": 1}
    )
    category = (incident or {}).get("category", "other")
    station = efir.get("stationJurisdiction") or ""
    station_code = STATION_CODES.get(station, DEFAULT_STATION_CODE)
    coords = efir["location"]["coordinates"]

    return {
        "efirId": efir["efirId"],
        "firReference": _fir_reference(efir, station_code),
        "incidentId": efir["incidentId"],
        "category": category,
        "categoryLabel": CATEGORY_LABELS.get(category, "Other"),
        "tourist": {
            "name": (user or {}).get("fullName", efir["userId"]),
            "phone": (user or {}).get("mobileNumber"),
            "nationality": (user or {}).get("nationality"),
        },
        "userId": efir["userId"],
        "blockchainId": efir.get("blockchainId"),
        "location": {
            "lat": coords[1],
            "lng": coords[0],
            "name": (incident or {}).get("locationName") or efir.get("stationJurisdiction"),
        },
        "time": efir["filedAt"].isoformat() if hasattr(efir.get("filedAt"), "isoformat") else efir.get("filedAt"),
        "status": efir["status"],
        "uiStatus": to_ui_status({"draft": "open", "filed": "acknowledged", "under_investigation": "responding", "closed": "resolved"}.get(efir["status"], "open")),
        "stationJurisdiction": station,
    }


async def list_efirs(time_filter: str = "all", ui_status: str | None = None, limit: int = 200) -> dict:
    db = get_db()
    query: dict = {}

    minutes = TIME_FILTERS.get(time_filter)
    if minutes:
        query["filedAt"] = {"$gte": datetime.utcnow() - timedelta(minutes=minutes)}

    if ui_status and ui_status.lower() != "all":
        mapping = {
            "pending": ["draft"],
            "investigating": ["filed", "under_investigation"],
            "closed": ["closed"],
        }
        if ui_status.lower() in mapping:
            query["status"] = {"$in": mapping[ui_status.lower()]}

    rows = await db["efir"].find(query).sort("filedAt", -1).limit(limit).to_list(length=limit)
    shaped = [await _shape_efir(e, db) for e in rows]
    return {"success": True, "count": len(shaped), "efirs": shaped}


async def efir_detail(efir_id: str) -> dict:
    """Full FIR including a plain-text rendering for the 'View & Copy FIR' button."""
    db = get_db()
    efir = await db["efir"].find_one({"efirId": efir_id})
    if not efir:
        raise HTTPException(status_code=404, detail="E-FIR not found")

    shaped = await _shape_efir(efir, db)
    shaped["narrative"] = efir.get("narrative")
    shaped["lastKnownLocations"] = [
        {
            "lat": loc["coordinates"][1],
            "lng": loc["coordinates"][0],
            "timestamp": loc["timestamp"].isoformat() if hasattr(loc.get("timestamp"), "isoformat") else loc.get("timestamp"),
        }
        for loc in efir.get("lastKnownLocations", [])
    ]

    shaped["copyText"] = _render_fir_text(shaped, efir)
    return {"success": True, "efir": shaped}


def _render_fir_text(shaped: dict, efir: dict) -> str:
    """Plain-text FIR an officer can copy straight into the police system."""
    trail_lines = "\n".join(
        f"    - {loc['lat']:.5f}, {loc['lng']:.5f} at {loc['timestamp']}" for loc in shaped.get("lastKnownLocations", [])[:10]
    ) or "    - No location trail recorded."

    return f"""FIRST INFORMATION REPORT (ELECTRONIC)
=====================================
FIR Reference : {shaped['firReference']}
E-FIR ID      : {shaped['efirId']}
Incident ID   : {shaped['incidentId']}
Station       : {shaped['stationJurisdiction'] or 'Nilgiris District'}
Filed At      : {shaped['time']}
Status        : {shaped['status']}

COMPLAINANT / SUBJECT
---------------------
Name          : {shaped['tourist']['name']}
Phone         : {shaped['tourist']['phone'] or 'Not recorded'}
Nationality   : {shaped['tourist']['nationality'] or 'Not recorded'}
Digital ID    : {shaped['blockchainId'] or 'Not issued'}

NATURE OF INCIDENT
------------------
Category      : {shaped['categoryLabel']}
Location      : {shaped['location']['name'] or 'See coordinates'}
Coordinates   : {shaped['location']['lat']:.5f}, {shaped['location']['lng']:.5f}

PARTICULARS
-----------
{efir.get('narrative', 'No narrative recorded.')}

LAST KNOWN MOVEMENTS
--------------------
{trail_lines}

Generated automatically by the SafeTour Smart Tourist Safety System.
This is a system-generated draft and must be verified by the attending officer.
"""


async def update_efir_status(efir_id: str, ui_status: str, officer_id: str) -> dict:
    db = get_db()
    mapping = {"pending": "draft", "investigating": "under_investigation", "closed": "closed"}
    internal = mapping.get(ui_status.lower())
    if not internal:
        raise HTTPException(status_code=400, detail="status must be one of: pending, investigating, closed")

    efir = await db["efir"].find_one_and_update(
        {"efirId": efir_id},
        {"$set": {"status": internal, "updatedAt": datetime.utcnow(), "lastUpdatedBy": officer_id}},
        return_document=True,
    )
    if not efir:
        raise HTTPException(status_code=404, detail="E-FIR not found")

    return {"success": True, "efir": await _shape_efir(efir, db)}
