# nilgiris_places.csv — Data Dictionary & Status

**v2: expanded from 27 → 60 places**, adding villages, sub-clusters, ghat-road
waypoints, and administrative towns, not just headline tourist attractions.
This matters for the movement/behaviour modules specifically: real tourist
GPS traces pass through villages and road waypoints, not just marquee spots,
so a graph built only from famous places would make every real trace look
like an "outlier" simply from missing nodes. Denser graph = fewer false
positives in Modules 4–6.

Breakdown: Ooty 19, Coonoor 12, Kotagiri 8, Mudumalai 6, Gudalur 6, Pykara 5,
Avalanche 2, Kunda 2 — 6 places flagged `restricted=True`.

## Columns
| Column | Description |
|---|---|
| `place_id` | Unique ID, used as a node reference for the place-graph and later synthetic movement generation |
| `name` | Place name |
| `cluster` | Which geographic group this belongs to (Ooty, Pykara, Avalanche, Coonoor, Kotagiri, Mudumalai, Kunda, Gudalur) |
| `type` | urban / lake / peak / waterfall / garden / museum / viewpoint / forest / wildlife / dam |
| `latitude`, `longitude` | Coordinates in decimal degrees |
| `restricted` | True if entry requires a permit or is otherwise access-controlled (safari-only, defense watershed, Forest Dept guide mandatory) |
| `notes` | Source context / access conditions |

## ⚠️ Coordinate accuracy — important, read before using in code

Only two coordinates in this file are precision-verified from a cited source:
- **P001 Ooty Town Centre** and **P003 Government Botanical Garden** —
  confirmed via Wikipedia (11.41°N 76.70°E and 11.418752°N 76.711038°E respectively).

**11 of 60 coordinates are now verified** (up from 2), sourced from Wikipedia
infoboxes and latlong.net. A new `coord_source` column marks each row as
`verified_wikipedia_or_latlong.net` or `estimated_unverified` so this is
traceable in code, not just in this doc.

**Verified (11):** Ooty Town Centre, Ooty Lake, Government Botanical Garden,
Doddabetta Peak, Avalanche Lake, Theppakadu, Mudumalai National Park (general),
Masinagudi, Mukurthi National Park, Coonoor Town Centre, Kotagiri Town Centre —
this covers the district's main towns, the highest-traffic tourist landmark,
and 3 of the 6 restricted zones.

**Still estimated (49):** mostly villages, minor waterfalls/viewpoints, and
the remaining restricted zones (Emerald Lake, Mudumalai Core Safari Zone as
a distinct sub-boundary from the park's general coordinates, Upper Bhavani
Lake, Moyar River Crossing). These still need the Nominatim pass described
below before feeding Phase 4 — **the sandbox environment used for this
project can't reach the Nominatim API directly (network allowlist doesn't
include it)**, so that step needs to run from your own machine or dev
environment, not from here.

## Required follow-up before this feeds Phase 4 (feature engineering)

1. Run every `name` through OSM Nominatim (`https://nominatim.openstreetmap.org/search?q=<name>,+Nilgiris,+Tamil+Nadu,+India&format=json`) to get verified coordinates.
2. Manually spot-check the restricted-zone entries (P011, P012, P023, P025, P026) — these matter most for Module 5 (Suspicious Movement), so their accuracy has outsized impact.
3. Cross-check against Google Places API if available (more reliable disambiguation than Nominatim for tourist-spot names with generic terms like "Falls" or "Viewpoint").
4. Once corrected, this becomes the canonical `data/raw/nilgiris_places.csv` referenced by every downstream module.

## Restricted zones — still needs real boundary data

This CSV only has point coordinates (single lat/long per restricted area),
which is not sufficient for real "is this GPS point inside the restricted
zone" logic — that needs a polygon, not a point + radius guess. Actual
polygon boundaries for Mudumalai core/buffer and Mukurthi still need to be
sourced from the WII geospatial portal (https://mee-tr.wii.gov.in) or traced
from OSM boundary relations. Treat the `restricted=True` rows here as
placeholders marking *that* a zone is restricted, not yet *where exactly*
its boundary is.
