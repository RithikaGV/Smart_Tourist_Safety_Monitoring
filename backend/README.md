# SafeTour Backend (Python / FastAPI)

Complete backend for the **Smart Tourist Safety & Security** system — serving
**both** the tourist app and the admin / officer control panel from one server
and one database (`SmartTouristDB`).

```
backend/
├── app.py                 # entrypoint - FastAPI + Socket.io + Mongo + cron
├── requirements.txt
├── routes/                # thin FastAPI routers, one file per area
├── controllers/           # business logic
├── models/                # Pydantic request/response schemas
├── middleware/            # JWT auth (user/admin/officer), error handlers
├── utils/                 # ids, OSRM road-snap, geofence math, safety score,
│                          #   E-FIR, sockets, cron, status mapping
├── database/              # Motor async MongoDB connection + indexes
├── blockchain/            # hash-chain KYC ID issuance + verification
└── seed/                  # demo data, fake-tourist generator, 3 test suites
```

## 1. Setup

```bash
cd backend
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env              # edit MONGO_URI, JWT secrets
python -m seed.seed               # Nilgiri zones, contacts, demo accounts
uvicorn app:socket_app --reload --port 5000
```

Run `app:socket_app`, **not** `app:app` — `socket_app` is the FastAPI app
wrapped with Socket.io so HTTP and real-time share one port. Docs: `/docs`.

Demo logins:

| Role | Email | Password |
|---|---|---|
| Tourist | `rithikagv2006@gmail.com` | `Password@123` |
| Admin | `admin@safetour.gov.in` | `Admin@123` |
| Officer | `officer@safetour.gov.in` | `Officer@123` |

## 2. Demo data — 100 fake tourists

```bash
pip install faker
python -m seed.generate_fake_tourists --count 100
```

Every fake tourist goes through the **real API**, not direct DB writes: signup →
KYC → blockchain ID → trip → road-snapped GPS trail → geofence checks. About 25%
are deliberately routed through restricted zones (so you get live incidents) and
~5% fire a real SOS.

It also creates a few **anomalous** tourists whose movement trips the AI
detectors — otherwise the AI Analytics screen is empty during a demo, since
normal generated pings all carry the current timestamp and the time-based
detectors have nothing to find. Those tourists are created through the API like
everyone else; only their ping *timestamps* are backdated in the DB afterwards,
because there is deliberately no API for a device to forge its own history.
Disable with `--no-anomalies`.

Flags: `--count`, `--base-url`, `--concurrency` (keep modest — the public OSRM
server is free and shared), `--local-test` (runs in-process with a mock DB, no
server/Mongo/internet needed).

## 3. Verifying it works

Three suites, all running against an in-memory mock MongoDB (no external
services):

```bash
pip install mongomock mongomock-motor
python -m seed.smoketest              # tourist API
python -m seed.smoketest_admin        # admin panel API (45 checks)
python -m seed.smoketest_integration  # generates 30 tourists, proves the admin
                                      #   panel correctly displays their data
```

All three pass. Two known, harmless notes:

- `smoketest` skips the "nearby facilities" check — mongomock doesn't implement
  MongoDB's `$near`. Real MongoDB does, via the 2dsphere index in
  `database/db.py`. Verify that one endpoint against a real Mongo.
- `datetime.utcnow()` emits a DeprecationWarning on Python 3.12. It still works;
  worth migrating to `datetime.now(datetime.UTC)` eventually.

## 4. Collections

| Collection | Used by |
|---|---|
| `users`, `kyc`, `blockchain_ids` | signup / identity |
| `trips`, `ai_safety` | trip planning + safety scores |
| `Live locations` | GPS trail (raw + road-snapped), TTL 7 days |
| `geofences` | zones — **shared** by tourist app and admin Zone Management |
| `incidents`, `sos_requests`, `efir` | incident workflow |
| `notifications` | tourist alerts |
| `admins`, `officers` | control panel accounts |
| `ai_alerts` | AI Analytics suspicious-movement alerts |

## 5. Tourist API

**Auth:** `POST /api/auth/create-account`, `POST /api/auth/login` (both public),
`GET|PATCH /api/auth/me`

**Trips:** `POST /api/trips/`, `GET /api/trips/` (`{upcoming, past}`),
`GET|PATCH|DELETE /api/trips/{tripId}`, `POST /api/trips/{tripId}/start|end`

**Location:** `POST /api/location/ping`, `GET /api/location/current/{userId}`,
`GET /api/location/history/{userId}`, `GET /api/location/route-preview`,
`GET /api/location/snap`

**Other:** `GET /api/geofences/`, `POST /api/sos/`, `GET /api/sos/mine`,
`GET /api/emergency-contacts/helplines|nearby`, `GET /api/safety/trip/{tripId}`,
`GET /api/safety/live`, `GET /api/notifications/`

## 6. Admin panel API

All under `/api/admin`, all requiring an admin token.

**Dashboard** — `GET /dashboard/overview` (the four KPI cards),
`GET /dashboard/incident-stats` (the monthly category chart, with bar
percentages precomputed), `GET /dashboard/recent-sos`

**Risk Heatmap** — `GET /heatmap` (clustered spots with Safe/Crowded/Danger),
`GET /heatmap/density` (the density bars), `GET /heatmap/live-positions`

**SOS Monitoring** — `GET /sos` (filters: `time`, `status`, `location`),
`GET /sos/{sosId}` (detail + movement trail + assignable officers),
`POST /sos/{sosId}/assign`, `PATCH /sos/{sosId}/status`

**E-FIR Monitoring** — `GET /efir`, `GET /efir/{efirId}` (includes `copyText`,
a paste-ready plain-text FIR), `PATCH /efir/{efirId}/status`

**Zone Management** — `GET /zones`, `POST /zones` ("Add Zone & Push Instant
Alert"), `PATCH|DELETE /zones/{geofenceId}`, `POST /zones/{geofenceId}/alert`

**AI Analytics** — `GET /ai/alerts`, `POST /ai/analyze`,
`POST /ai/alerts/{alertId}/action` (Dispatch / Mark Benign / Escalate)

**Incidents** — `GET|POST /incidents`, `GET /incidents/{id}`,
`POST /incidents/{id}/assign`, `PATCH /incidents/{id}/status`,
`POST /incidents/{id}/efir`

**Officers** — `GET /officers`, `PATCH /officers/{id}/duty`,
plus `POST /api/officer/login` and `PATCH /api/officer/location`

## 7. Design decisions worth knowing

**Zones are circles in the UI, polygons in the database.** An officer draws a
zone as centre + radius (far easier than clicking out a polygon), but the
tourist-side geofence check does point-in-polygon on GeoJSON. So on save the
circle is converted to a 32-sided polygon — correcting for longitude degrees
compressing as latitude increases, or the "circle" renders as an ellipse — and
stored in the **same `geofences` collection the tourist app already reads**. A
zone an officer creates is live for every tourist immediately: no sync step, no
duplicated logic. Zones saved as *draft* are stored but inactive, so they don't
alert anyone until promoted.

**Two status vocabularies, deliberately.** The panel shows three states
(Pending / Investigating / Closed), but officers need finer detail internally —
"acknowledged" versus "a unit is en route" is a real operational difference.
Rather than flattening the model, `utils/status_map.py` translates at the API
boundary and every admin response carries both `status` and `uiStatus`.

**Role separation is cryptographic, not a string check.** Tourist, admin and
officer tokens are signed with *different secrets*. A tourist token presented to
an admin route fails signature verification (401) before any role comparison
happens — so a forged `role: "admin"` claim is useless without the admin secret.

**The AI detectors are explainable heuristics, not a black box.** Four of them
(repeated looping, prolonged inactivity, route deviation, proximity clustering)
run over real `Live locations` data and each states plainly why it fired, with a
0–100 score. All thresholds sit in named constants at the top of
`controllers/ai_analytics_controller.py` so you can explain or tune any of them
on stage. Swap any detector's body for a trained model later — the alert shape
the UI consumes stays the same.

**"Blockchain" is a hash chain, and that's the honest framing.** Each KYC record
stores `sha256(payloadHash + previousHash + timestamp)`, so editing any past
record breaks every hash after it. That's genuine tamper-evidence without
pretending there's a distributed network of nodes. `verify_chain()` proves
integrity on demand.

## 8. Real-time (Socket.io)

Connect with `io(url, { auth: { userId, role: 'user' | 'admin' } })`.
python-socketio speaks the same wire protocol as Node's socket.io, so a
JavaScript frontend needs no changes.

- **Tourist emits:** `location:push`
- **Admin emits:** `admin:watch-user`
- **Listen for:** `location:update`, `incident:new`, `incident:update`,
  `sos:new`, `sos:update`, `safety:update`, `zone:created`, `zone:updated`,
  `zone:deleted`, `zone:alert`, `ai:alert`, `ai:alert-update`, `efir:new`

Admins are auto-joined to `admin-room` (sees everything); tourists join
`user-{userId}` (sees only themselves).
