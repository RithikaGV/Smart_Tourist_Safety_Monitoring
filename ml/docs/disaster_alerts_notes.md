# Disaster Alerts (Landslide / Flood) — Data Sourcing Notes

## Reality check

Unlike weather, there is **no clean public API** for landslide/flood alerts
at Nilgiris district granularity. What exists instead:

- **NDMA Alerts Hub** (https://ndma.gov.in/alert-hub/Alert) — dashboard
  only, aggregates IMD weather bulletins, CWC flood bulletins, DGRE
  avalanche bulletins. No documented REST API for programmatic access.
- **Sachet app** (sachet.ndma.gov.in) — the actual citizen-facing alert
  system (12 languages, Android/iOS), but it's an app/push-notification
  system, not an open data API.
- **NDMA Landslide Hazard Zonation (LHZ) maps** — exist as static maps
  (via NRSC/BMTPC), useful as a one-time reference layer, not a live feed.

This matches what we flagged back in Phase 0: these datasets are
**"Real where available, synthetic fallback."** In practice, for Nilgiris,
"real where available" mostly means static/historical, not live.

## What we'll actually do

1. **Static risk layer, not live feed.** Use the LHZ maps and known
   landslide-prone zones (Nilgiris has documented landslide history along
   the Ooty-Coonoor and Ooty-Gudalur ghat roads) to hand-label a
   `landslide_risk_zone` flag per place in `nilgiris_places.csv` — same
   pattern as the `restricted` column. This is honest: a static risk
   score based on historical patterns, not a real-time alert.
2. **Synthetic alert events layered on top of real weather.** Once
   `weather_historical.csv` exists (from `fetch_weather_data.py`), we can
   generate synthetic "landslide alert" / "flood alert" events
   *conditionally* — e.g., trigger a synthetic alert when historical
   rainfall exceeds a known danger threshold at a known landslide-prone
   location. This is more defensible than pure random synthetic data,
   because the trigger condition is grounded in real rainfall data and
   real geography, even though the "alert" itself is simulated.
3. **Document this clearly in Phase 15.** The eventual model documentation
   should state plainly: landslide/flood "alerts" in this dataset are
   synthetically generated from a rule (historical rainfall threshold ×
   known-risk location), not sourced from a live government feed. This is
   a reasonable, disclosed simplification for a prototype — just not one
   to present as "real-time government alert data."

## Open task

- [ ] Identify 3-5 documented landslide-prone stretches in Nilgiris (ghat
      roads are the obvious candidates) and hand-label them in the places
      dataset
- [ ] Decide the rainfall threshold for the synthetic alert rule (needs a
      reasonable citation — e.g., IMD's heavy/very heavy rainfall
      classification, which is a real public standard, not invented)
