# Phase 0 — AI/ML Planning & Architecture

## 1. Scope

This document covers only the `ml/` module. Frontend and Backend are owned by
other teammates. This module exposes predictions via API; it does not own
storage, auth, or UI.

**Geographic scope: Nilgiris district, Tamil Nadu, India — only.** No other
region is in scope for v1. This is a meaningful simplification:
- Weather: single district-level station/forecast lookup instead of
  multi-region handling.
- Tourist places: bounded, known set (Ooty, Coonoor, Kotagiri, Mudumalai,
  Avalanche, Emerald Lake, etc.) — feasible to hand-curate rather than
  scrape broadly.
- Restricted zones: real, identifiable areas exist — Mudumalai Tiger Reserve
  core zone, forest buffer zones, and other protected-area boundaries. These
  are **real** restricted zones, not synthetic guesses, though exact
  polygon coordinates still need to be sourced (forest dept / WII maps or
  manually traced from OSM boundary data).
- Crowd density and crime rate: still no public geo-granular dataset for
  this district specifically, so these remain **synthetic** — but can now
  be calibrated to plausible Nilgiris tourist-season patterns (e.g., higher
  crowd density at Ooty Lake/Botanical Garden in April–June season) instead
  of being fully arbitrary.

**Assumed stack** (flag now if wrong): Python, pandas/scikit-learn/XGBoost,
FastAPI for serving, SHAP for explainability. Folder structure below assumes this.

---

## 2. Module Overview

| # | Module | Type | Model | Powers |
|---|--------|------|-------|--------|
| 1 | Risk Prediction | Supervised classification | XGBoost (Random Forest backup) | Destination Safety Score, Danger Alerts |
| 2 | Safety Score | Weighted formula → regression | Weighted formula (v1), XGBoost Regressor (v2, needs labels) | "92/100" score on User Panel |
| 3 | Smart Deviation Alert | Rule-based, no ML | Haversine distance + threshold | "You are off route" alert |
| 4 | Tourist Behaviour Analysis | Unsupervised clustering | DBSCAN | Admin: Pattern/behaviour view |
| 5 | Suspicious Movement Detection | Unsupervised anomaly detection | Isolation Forest (Autoencoder later) | Admin: Suspicious Movement Alerts |
| 6 | Pattern Detection | Unsupervised / sequential | Isolation Forest (LSTM stretch goal) | Admin: Risk Heatmap, Pattern Detection |

**Build order** (per our sequencing discussion):
1. Phase 7 first in practice — Deviation Detection (zero data risk, quick demo win)
2. Then Risk Prediction + Safety Score (core intelligence, both panels depend on it)
3. Then Behaviour Analysis → Suspicious Movement → Pattern Detection
4. Evaluation, SHAP, API integration, testing, docs last

---

## 3. Per-Module Inputs / Outputs

### Module 1 — Risk Prediction
- **Inputs:** weather, rainfall, crowd density, crime rate, time, landslide alerts, flood alerts
- **Output:** `Safe` / `Dangerous` (+ confidence score)
- **Endpoint:** `POST /predict-risk`

### Module 2 — Safety Score
- **Inputs:** weather, crime, crowd, time, disaster risk, distance to hospital, distance to police
- **Output:** integer score 0–100
- **Open decision:** v2 (regressor) needs a training target. Until we have real
  or credibly-simulated ground-truth scores, **v1 (weighted formula) is the
  actual deliverable** — v2 is future work, not a parallel track.
- **Endpoint:** `POST /safety-score`

### Module 3 — Smart Deviation Alert
- **Inputs:** planned route (list of coordinates), live GPS
- **Output:** distance from route (km) + boolean alert
- **Logic:** Haversine distance between live point and nearest planned-route
  segment; alert if > threshold (default assumption: 500m, tune later)
- **Endpoint:** `POST /detect-deviation`

### Module 4 — Tourist Behaviour Analysis
- **Inputs:** sequence of visited zones per tourist, dwell time per zone
- **Output:** cluster ID + `normal` / `outlier` flag
- **Endpoint:** `POST /pattern-detection` (shared with Module 6, see note below)

### Module 5 — Suspicious Movement Detection
- **Inputs:** zone entry/exit counts, restricted-zone entries, movement frequency
- **Output:** anomaly score + boolean flag
- **Endpoint:** `POST /detect-anomaly`

### Module 6 — Pattern Detection
- **Inputs:** time-ordered zone-transition sequences per tourist (admin-wide)
- **Output:** flagged tourist IDs + pattern description
- **Endpoint:** `POST /pattern-detection`
- **Note:** Modules 4 and 6 overlap in input features (zone sequences). We'll
  share a single feature-extraction function for both rather than duplicating it.

---

## 4. Synthetic vs. Real Data — Decided Now

| Dataset | Real source available? | Decision |
|---|---|---|
| Weather / rainfall | Yes (IMD Ooty station / OpenWeather API, district-level) | Real |
| Landslide / flood alerts | Partial (TN govt disaster advisories, Nilgiris-specific) | Real where available, synthetic fallback |
| Crime rate by location | No (rarely public at geo-granularity, even for one district) | **Synthetic**, but scoped to known Nilgiris towns (Ooty, Coonoor, Kotagiri, Gudalur) |
| Crowd density | No | **Synthetic**, calibrated to real tourist-season patterns for Nilgiris spots |
| Tourist places / GPS routes | Yes (OSM / Google Places — bounded to Nilgiris district) | Real |
| Restricted zones | Real zones exist (Mudumalai Tiger Reserve, forest buffer areas) but precise polygon data needs sourcing | Real zone identity; polygon boundaries traced from OSM/forest dept maps (fallback: approximate manually) |
| Tourist movement sequences | No (privacy) | **Synthetic**, generated over the real Nilgiris place graph (so transitions like Ooty→Mudumalai are geographically plausible) |
| Historical disasters | Partial (NDMA data, Nilgiris has known landslide-prone zones) | Real where available, synthetic fallback |

**Documentation commitment (Phase 15):** every synthetic dataset is disclosed
as synthetic. No result is presented as validated against real-world ground
truth unless it actually is (weather/route data only).

---

## 5. Evaluation Strategy — Decided Now (fixes Phase 11 ambiguity)

| Module | Evaluation method |
|---|---|
| Risk Prediction | Standard supervised metrics: Accuracy, Precision, Recall, F1, ROC-AUC (on synthetic labels — disclosed as such) |
| Safety Score | Formula: no "accuracy" — validate with sanity-check cases (e.g., hospital nearby + no crime → score should be high) |
| Deviation Detection | Rule correctness testing, not ML metrics |
| Behaviour Analysis (DBSCAN) | No ground truth. Qualitative: inspect clusters manually, check outliers make sense against injected synthetic anomalies |
| Suspicious Movement (Isolation Forest) | Same as above — inject known-suspicious synthetic cases, check they're flagged |
| Pattern Detection | Same as above |

SHAP (Phase 12) applies cleanly only to Modules 1 and 2 (tree-based, supervised).
It will not be used to explain DBSCAN/Isolation Forest output — those get
human-readable rule summaries instead (e.g., "flagged: 3 restricted-zone entries").

---

## 6. Folder Structure

```
ml/
├── data/
│   ├── raw/
│   └── processed/
├── notebooks/          # EDA, phase 3
├── src/
│   ├── data_pipeline/  # collection + cleaning, phase 1-2
│   ├── features/       # feature engineering, phase 4 (shared by modules 1,4,5,6)
│   ├── models/
│   │   ├── risk_prediction.py
│   │   ├── safety_score.py
│   │   ├── deviation.py
│   │   ├── behaviour_analysis.py
│   │   ├── suspicious_movement.py
│   │   └── pattern_detection.py
│   ├── explainability/ # SHAP, phase 12
│   └── api/             # FastAPI app, phase 13
├── tests/
├── artifacts/            # saved trained models
└── docs/                 # phase 15 per-module docs
```

## 7. API Contract Summary

| Endpoint | Method | Consumed by |
|---|---|---|
| `/predict-risk` | POST | User panel — Destination Safety Score, Danger Alert |
| `/safety-score` | POST | User panel — Overall Safety score |
| `/detect-deviation` | POST | User panel — Smart Deviation Alert |
| `/detect-anomaly` | POST | Admin panel — Suspicious Movement Alerts |
| `/pattern-detection` | POST | Admin panel — Risk Heatmap, Pattern Detection, Tourist Behaviour |

All endpoints return JSON only — no UI logic, no storage decisions.

---

## 8. Open Items Still Pending

- [ ] Confirm 500m deviation threshold (or get real value from product/backend team)
- [ ] Confirm FastAPI as the serving framework (or Flask, if that's what backend expects)
- [ ] Decide synthetic data generator: build one shared generator script or per-dataset scripts

## 9. Phase 1 Kickoff — Curated Nilgiris Place Data (real, sourced)

### 9.1 Tourist places by cluster (hand-curated, not scraped)

| Cluster | Key spots |
|---|---|
| **Ooty town** | Ooty Lake, Government Botanical Garden, Doddabetta Peak, Rose Garden, Wax World Museum, Tea Museum |
| **Pykara side** | Pykara Falls, Pykara Lake/boating, Pykara Dam |
| **Avalanche / Emerald** | Avalanche Lake, Emerald Lake — **note: this area is defense-watershed controlled, entry is permit-restricted**, not open like standard tourist spots |
| **Coonoor** | Sim's Park, Dolphin's Nose, Lamb's Rock, Catherine Falls (Coonoor side), Kateri Falls |
| **Kotagiri** | Kodanad Viewpoint, Catherine Falls (Kotagiri side), Longwood Shola, Rangaswamy Peak, Elk Falls |
| **Mudumalai / Masinagudi belt** | Theppakadu (reserve reception centre + elephant camp), Mudumalai safari zones, Masinagudi town |
| **Kunda / high-altitude** | Upper Bhavani Lake, Mukurthi National Park (Mukurthi Peak) |
| **Gudalur** | Gateway town to Mudumalai, forest belt |

Each spot needs: name, lat/long, cluster, "type" (lake/peak/waterfall/forest/wildlife/urban),
and a `restricted` boolean — most fields collectible from OSM; coordinates
straightforward to pull via Nominatim/Overpass API.

### 9.2 Restricted / permit-controlled zones (real, not synthetic)

| Zone | Status | Notes |
|---|---|---|
| **Mudumalai Tiger Reserve — Core / Critical Tiger Habitat** | Restricted | 321 km², no general public entry — safari only via permitted routes/vehicles |
| **Mudumalai Tiger Reserve — Buffer zone** | Semi-restricted | 367.59 km² surrounding core; some public road transit allowed, off-road entry restricted |
| **Mukurthi National Park** | Restricted, permit required | Advance permit from Nilgiris Forest Division (Ooty); mandatory Forest Dept guide for core zone entry — no walk-in access |
| **Avalanche / Upper Bhavani watershed** | Restricted (defense-controlled) | Permit-gated, unlike typical tourist spots |

**Boundary data:** exact polygons for these need to come from WII (Wildlife
Institute of India) geospatial portal or traced from OSM boundary relations —
not something we invent. This is a real follow-up task, not a synthetic
placeholder.

### 9.3 Place-graph (basis for synthetic movement generation)

Real geography gives us real adjacency/travel-time structure instead of
arbitrary transitions. Rough structure:

```
Ooty town ── Pykara side (17 km)
Ooty town ── Coonoor (19 km)
Ooty town ── Kotagiri (28-32 km)
Ooty town ── Avalanche/Emerald (restricted, permit gate)
Ooty town ── Mukurthi (restricted, permit gate)
Ooty town ── Mudumalai/Masinagudi (36 km via Kalhatty, or 67 km via Gudalur)
Coonoor ── Kotagiri (21 km)
Gudalur ── Mudumalai (gateway town, short distance)
Mudumalai core ── Kerala/Karnataka borders (tri-junction — cross-state edge, out of scope but relevant for "unusual" edge-of-district movement flags)
```

This graph is what makes synthetic tourist movement *plausible* rather than
random: e.g., "Ooty → Avalanche without permit record → Ooty" is a
meaningfully different (flaggable) sequence from "Ooty → Coonoor → Kotagiri."
The restricted-zone-without-permit pattern is actually one of the more
realistic synthetic signals we can build for Module 5 (Suspicious Movement).

### 9.5 Restricted zone boundaries — real sources identified

Two real, usable sources exist for actual polygon boundaries (not just points):

1. **OSM Overpass API** — no signup, has boundary relations for named
   protected areas. Rougher (multipolygon assembly needs care), but free
   and immediate.
2. **Protected Planet / WDPA** (UN Environment + IUCN) — the authoritative
   global database, has clean polygons for Mudumalai Tiger Reserve and
   Mukurthi National Park specifically. Needs a free API token
   (https://api.protectedplanet.net/request, usually same-day approval).

`fetch_restricted_zones.py` (in this outputs folder) tries WDPA first if a
token is set, falls back to OSM otherwise, and writes `restricted_zones.geojson`.

**Known gap:** Avalanche watershed and Upper Bhavani are defense/watershed-
controlled areas, not IUCN-designated protected areas — they likely won't
appear in WDPA at all, and may not be cleanly tagged in OSM either. These
two will probably need manual boundary tracing (e.g., drawing a polygon in
geojson.io based on descriptions/maps) rather than API lookup. Flagging this
now so it doesn't block the rest of Phase 1.
- [ ] Pull precise lat/long for every place in 9.1 via OSM Nominatim
- [ ] Source or trace boundary polygons for the 4 restricted zones in 9.2 (WII geoportal / OSM relations)
- [ ] Build `nilgiris_places.csv` and `restricted_zones.geojson` as the first two real datasets
- [ ] Use this graph structure as the seed for the synthetic tourist-movement generator (Phase 1, remaining synthetic datasets)
