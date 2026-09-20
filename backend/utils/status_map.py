"""
utils/status_map.py
--------------------
The tourist-facing backend tracks a fine-grained incident/SOS lifecycle
(open -> acknowledged -> responding -> resolved / false_alarm), but the admin
panel UI only shows three buckets: Pending, Investigating, Closed.

Rather than dumbing down the internal model (officers genuinely need the
difference between "acknowledged" and "a unit is en route"), we keep both and
translate at the API boundary. Every admin endpoint returns a `uiStatus` field
alongside the real `status`, so the panel can render its three badges while the
database keeps the full detail.
"""

# internal -> what the admin panel displays
TO_UI = {
    "open": "pending",
    "pending": "pending",
    "acknowledged": "investigating",
    "responding": "investigating",
    "dispatched": "investigating",
    "resolved": "closed",
    "false_alarm": "closed",
    "cancelled": "closed",
}

# what the admin panel sends -> what we store internally
FROM_UI_INCIDENT = {
    "pending": "open",
    "investigating": "responding",
    "closed": "resolved",
}

FROM_UI_SOS = {
    "pending": "pending",
    "investigating": "dispatched",
    "closed": "resolved",
}

# Severity -> the panel's Priority badge (High / Medium / Low)
SEVERITY_TO_PRIORITY = {
    "critical": "high",
    "high": "high",
    "medium": "medium",
    "low": "low",
}


def to_ui_status(internal_status: str) -> str:
    return TO_UI.get(internal_status, "pending")


def to_priority(severity: str) -> str:
    return SEVERITY_TO_PRIORITY.get(severity, "medium")


def decorate(doc: dict) -> dict:
    """Adds uiStatus/priority to a document so the admin panel can render it directly."""
    if not doc:
        return doc
    if "status" in doc:
        doc["uiStatus"] = to_ui_status(doc["status"])
    if "severity" in doc:
        doc["priority"] = to_priority(doc["severity"])
    return doc
