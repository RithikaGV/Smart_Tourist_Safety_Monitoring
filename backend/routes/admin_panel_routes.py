"""
routes/admin_panel_routes.py
-----------------------------
Every endpoint the SafeTour admin / officer control panel calls, grouped by the
screen it belongs to. All routes require an admin token except where noted.
"""
from fastapi import APIRouter, Depends, Query

from middleware.auth import require_admin, require_officer
from models.zone import ZoneCreateRequest, ZoneUpdateRequest, ZoneAlertRequest
from models.ai_alert import AIAlertActionRequest
from models.incident import IncidentCreateRequest, IncidentStatusUpdateRequest, AssignOfficerRequest
from models.efir import EFIRGenerateRequest
from models.officer import OfficerLoginRequest

from controllers import (
    admin_dashboard_controller,
    heatmap_controller,
    sos_monitoring_controller,
    efir_monitoring_controller,
    zone_controller,
    ai_analytics_controller,
    incident_controller,
    officer_controller,
)

router = APIRouter(prefix="/api/admin", tags=["admin-panel"])


# ---------------------------------------------------------------- Dashboard
@router.get("/dashboard/overview")
async def dashboard_overview(auth=Depends(require_admin)):
    """The four KPI cards: Total Tourists / Active Tourists / Live SOS / Live E-FIR."""
    return await admin_dashboard_controller.dashboard_overview()


@router.get("/dashboard/incident-stats")
async def incident_stats(
    month: int | None = Query(default=None, ge=1, le=12),
    year: int | None = Query(default=None),
    auth=Depends(require_admin),
):
    """'Incident Stats (This Month)' - counts per category with bar percentages."""
    return await admin_dashboard_controller.incident_stats(month, year)


@router.get("/dashboard/recent-sos")
async def recent_sos(limit: int = Query(default=5, le=50), auth=Depends(require_admin)):
    return await admin_dashboard_controller.recent_sos(limit)


# ------------------------------------------------------------- Risk Heatmap
@router.get("/heatmap")
async def risk_heatmap(
    timeRange: str = Query(default="now", description="now | 1h | 6h | 24h | 7d"),
    district: str | None = Query(default=None),
    auth=Depends(require_admin),
):
    """District-wide clustered risk map with Safe/Crowded/Danger colour coding."""
    return await heatmap_controller.risk_heatmap(timeRange, district)


@router.get("/heatmap/density")
async def tourist_density(
    timeRange: str = Query(default="now"),
    limit: int = Query(default=10, le=50),
    auth=Depends(require_admin),
):
    """'Tourist Density Visualization' bars - busiest spots with GREEN/YELLOW/RED bands."""
    return await heatmap_controller.tourist_density(timeRange, limit)


@router.get("/heatmap/live-positions")
async def live_positions(limit: int = Query(default=500, le=2000), auth=Depends(require_admin)):
    """Individual live tourist markers for the map."""
    return await heatmap_controller.live_tourist_positions(limit)


# ----------------------------------------------------------- SOS Monitoring
@router.get("/sos")
async def list_sos(
    time: str = Query(default="all", description="all | 1h | 24h | 7d | 30d"),
    status: str | None = Query(default=None, description="all | pending | investigating | closed"),
    location: str | None = Query(default=None),
    limit: int = Query(default=200, le=1000),
    auth=Depends(require_admin),
):
    return await sos_monitoring_controller.list_sos_monitoring(time, status, location, limit)


@router.get("/sos/{sos_id}")
async def sos_detail(sos_id: str, auth=Depends(require_admin)):
    """Detail view: tourist info, live position, recent trail, assignable officers."""
    return await sos_monitoring_controller.sos_detail(sos_id)


@router.post("/sos/{sos_id}/assign")
async def assign_sos_officer(sos_id: str, payload: AssignOfficerRequest, auth=Depends(require_admin)):
    """'Accept / Assign Officer' - also notifies the tourist that help is coming."""
    return await sos_monitoring_controller.assign_officer(sos_id, payload.officerId, auth["id"])


@router.patch("/sos/{sos_id}/status")
async def update_sos_status(sos_id: str, payload: IncidentStatusUpdateRequest, auth=Depends(require_admin)):
    """The Pending / Investigating / Closed buttons."""
    return await sos_monitoring_controller.update_sos_status(sos_id, payload.status, payload.note, auth["id"])


# ---------------------------------------------------------- E-FIR Monitoring
@router.get("/efir")
async def list_efirs(
    time: str = Query(default="all"),
    status: str | None = Query(default=None),
    limit: int = Query(default=200, le=1000),
    auth=Depends(require_admin),
):
    return await efir_monitoring_controller.list_efirs(time, status, limit)


@router.get("/efir/{efir_id}")
async def efir_detail(efir_id: str, auth=Depends(require_admin)):
    """'View & Copy FIR' - includes a ready-to-paste plain-text FIR in `copyText`."""
    return await efir_monitoring_controller.efir_detail(efir_id)


@router.patch("/efir/{efir_id}/status")
async def update_efir_status(efir_id: str, payload: IncidentStatusUpdateRequest, auth=Depends(require_admin)):
    return await efir_monitoring_controller.update_efir_status(efir_id, payload.status, auth["id"])


# --------------------------------------------------------- Zone Management
@router.get("/zones")
async def list_zones(auth=Depends(require_admin)):
    return await zone_controller.list_zones()


@router.post("/zones", status_code=201)
async def create_zone(payload: ZoneCreateRequest, auth=Depends(require_admin)):
    """'Add Zone & Push Instant Alert' - creates the zone and, if requested,
    immediately notifies every tourist currently inside it."""
    return await zone_controller.create_zone(payload, auth["id"])


@router.patch("/zones/{geofence_id}")
async def update_zone(geofence_id: str, payload: ZoneUpdateRequest, auth=Depends(require_admin)):
    return await zone_controller.update_zone(geofence_id, payload)


@router.delete("/zones/{geofence_id}")
async def delete_zone(geofence_id: str, auth=Depends(require_admin)):
    return await zone_controller.delete_zone(geofence_id)


@router.post("/zones/{geofence_id}/alert")
async def alert_zone(geofence_id: str, payload: ZoneAlertRequest, auth=Depends(require_admin)):
    """The per-row 'Alert' button - re-pushes a warning to everyone in the zone."""
    return await zone_controller.push_alert_for_zone(geofence_id, payload.message)


# ------------------------------------------------------------- AI Analytics
@router.get("/ai/alerts")
async def list_ai_alerts(
    status: str = Query(default="open", description="open | dispatched | benign | escalated | all"),
    limit: int = Query(default=100, le=500),
    auth=Depends(require_admin),
):
    return await ai_analytics_controller.list_alerts(status, limit)


@router.post("/ai/analyze")
async def run_ai_analysis(
    windowHours: int = Query(default=6, ge=1, le=168),
    auth=Depends(require_admin),
):
    """Runs the anomaly detectors over recent movement data and saves new alerts."""
    return await ai_analytics_controller.run_analysis(windowHours)


@router.post("/ai/alerts/{alert_id}/action")
async def act_on_ai_alert(alert_id: str, payload: AIAlertActionRequest, auth=Depends(require_admin)):
    """The Dispatch / Mark Benign / Escalate buttons on each alert card."""
    return await ai_analytics_controller.act_on_alert(alert_id, payload, auth["id"])


# ---------------------------------------------------------------- Incidents
@router.get("/incidents")
async def list_incidents(
    time: str = Query(default="all"),
    status: str | None = Query(default=None),
    category: str | None = Query(default=None),
    limit: int = Query(default=200, le=1000),
    auth=Depends(require_admin),
):
    return await incident_controller.list_incidents(time, status, category, limit)


@router.post("/incidents", status_code=201)
async def create_incident(payload: IncidentCreateRequest, auth=Depends(require_admin)):
    return await incident_controller.create_incident(payload, auth["id"])


@router.get("/incidents/{incident_id}")
async def incident_detail(incident_id: str, auth=Depends(require_admin)):
    return await incident_controller.incident_detail(incident_id)


@router.post("/incidents/{incident_id}/assign")
async def assign_incident_officer(incident_id: str, payload: AssignOfficerRequest, auth=Depends(require_admin)):
    return await incident_controller.assign_officer_to_incident(incident_id, payload.officerId)


@router.patch("/incidents/{incident_id}/status")
async def update_incident_status(incident_id: str, payload: IncidentStatusUpdateRequest, auth=Depends(require_admin)):
    return await incident_controller.update_incident_status(incident_id, payload.status, payload.note, auth["id"])


@router.post("/incidents/{incident_id}/efir", status_code=201)
async def file_efir(incident_id: str, payload: EFIRGenerateRequest, auth=Depends(require_admin)):
    return await incident_controller.generate_efir_for_incident(incident_id, payload.stationJurisdiction)


# ----------------------------------------------------------------- Officers
@router.get("/officers")
async def list_officers(onDutyOnly: bool = Query(default=False), auth=Depends(require_admin)):
    """Feeds every 'Assign to officer' dropdown in the panel."""
    return await officer_controller.list_officers(onDutyOnly)


@router.patch("/officers/{officer_id}/duty")
async def set_duty(officer_id: str, onDuty: bool = Query(...), auth=Depends(require_admin)):
    return await officer_controller.set_duty_status(officer_id, onDuty)


# Officer-authenticated (not admin) - officers updating their own position
officer_router = APIRouter(prefix="/api/officer", tags=["officer"])


@officer_router.post("/login")
async def officer_login(payload: OfficerLoginRequest):
    return await officer_controller.officer_login(payload)


@officer_router.patch("/location")
async def update_my_location(lat: float = Query(...), lng: float = Query(...), auth=Depends(require_officer)):
    return await officer_controller.update_officer_location(auth["id"], lat, lng)
