# Phase 7 — Smart Deviation Detection: Status

## What it is
`src/models/deviation/deviation_detection.py` — pure geometry (Haversine
distance + a threshold), no ML, no training data needed. Matches what we
agreed back in Phase 0: this is the one module that's genuinely more
reliable as a rule than as a trained model.

## Tested and working
Self-test uses real verified Nilgiris coordinates (Ooty Town → Botanical
Garden → Doddabetta Peak as a planned route):
- On-route point: 0.029 km from route → OK
- Just-over-threshold point: 0.586 km → ALERT (correctly triggers just
  past the 500m line)
- Far-off point (near Avalanche): 13.78 km → ALERT

## Known limitation (disclosed, not hidden)
The route between waypoints is approximated as a **straight line**, then
densely sampled every 50m. Real Nilgiris ghat roads curve substantially,
so right after a sharp bend this can slightly overstate how far someone
has deviated. Fine for a prototype. A production version would snap the
route to actual road geometry using a routing engine (e.g. OSRM) instead
of straight-line interpolation — flagged here as a real upgrade path, not
forgotten.

## Still open
The 500m threshold is still a default, not a confirmed value — this was
flagged as an open item back in Phase 0 and still needs sign-off from
whoever owns the actual UX/safety requirements (could reasonably be
tighter in a dense urban cluster like Ooty town, looser on a remote
forest trail — a single global threshold is a simplification worth
revisiting later).

## API shape (ready for Phase 13)
```python
check_deviation(planned_route, current_location, threshold_km=0.5)
# returns: {distance_from_route_km, is_deviated, threshold_km, nearest_route_point}
```
This is already in the exact shape a FastAPI endpoint would wrap directly
— no additional adaptation needed when Phase 13 happens.
