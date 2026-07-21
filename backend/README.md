# SafeTour Backend (Python / FastAPI)

Python rebuild of the SafeTour backend, laid out to match your project's file
structure exactly:

```
backend/
├── app.py                 # entrypoint - FastAPI + Socket.io + Mongo + cron, all wired here
├── requirements.txt
├── routes/                # thin FastAPI routers - one file per resource
├── controllers/           # business logic (routes call these)
├── models/                # Pydantic request/response schemas
├── middleware/            # JWT auth dependencies, error handlers
├── utils/                 # id generator, OSRM road-snap, geofence check, safety score, E-FIR, sockets, cron
├── database/              # Motor (async MongoDB) connection + index setup
├── blockchain/            # hash-chain "blockchain" KYC ID issuance + verification
└── seed/                  # seed.py (demo data) + smoketest.py (end-to-end check)
```

Same feature set as before, same `SmartTouristDB` collections - just Python
(FastAPI) instead of Node. If you already have the Node version running,
you only need one or the other, not both.

## 1. Setup

```bash
cd backend
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env            # edit MONGO_URI, JWT secrets, etc.
```

`MONGO_URI` + `MONGO_DB_NAME` default to `mongodb://127.0.0.1:27017` /
`SmartTouristDB` to match your existing database.

```bash
python -m seed.seed             # Nilgiri geofences, emergency contacts, demo accounts
uvicorn app:socket_app --reload --port 5000
```

**Important:** run `uvicorn app:socket_app`, not `app:app` - `socket_app` is
the FastAPI app wrapped with Socket.io so both HTTP and real-time traffic
share one port. Interactive API docs: `http://localhost:5000/docs`.

Demo logins created by `python -m seed.seed`:
- Tourist: `rithikagv2006@gmail.com` / `Password@123`
- Admin: `admin@safetour.gov.in` / `Admin@123`
- Officer: `officer@safetour.gov.in` / `Officer@123`

### Verifying it works end-to-end
```bash
python -m seed.smoketest
```
This runs signup -> KYC/blockchain ID issuance -> trip creation -> geofence
breach -> auto-incident -> SOS -> emergency contacts -> safety score, entirely
in-process against an in-memory mock MongoDB (`mongomock-motor`), so it needs
no real database or internet connection. It passed end-to-end while building
this. The one query it can't verify (`$near` for "nearby facilities") is a
mongomock limitation, not a real one - MongoDB itself supports `$near` fine via
the 2dsphere index `database/db.py` creates; test that one against a real Mongo.

## 2. How the pieces map to your database

Identical collections to the Node version - `users`, `admins`, `officers`,
`trips`, `kyc`, `blockchain_ids`, `geofences`, `incidents`, `efir`,
`sos_requests`, `emergency_contacts`, `notifications`, `ai_safety`,
`Live locations`.

## 3. Maps + road-snapped movement

Same OSRM-based pipeline as the Node version, now in `utils/road_snap.py`
(httpx instead of axios) and `utils/geofence_check.py` (Shapely instead of
turf.js). `controllers/location_controller.py::ingest_location_ping` is the
shared pipeline hit by both the REST fallback (`POST /api/location/ping`) and
the `location:push` Socket.io event:

1. snap the raw GPS point to the nearest road (OSRM `/nearest`)
2. check it against every `geofences` polygon (Shapely `contains`)
3. save a `Live locations` document (raw + snapped coordinates)
4. auto-raise an `incidents` doc + `notifications` alert on restricted/
   tribal-sacred-site/high-risk entry
5. broadcast over Socket.io to the tourist's own room and `admin-room`

**python-socketio speaks the same wire protocol as Node's socket.io**, so the
`frontend-integration/LiveMap.jsx` and `TripRoutePreview.jsx` components from
the Node delivery work against this backend unchanged - just point
`apiBaseUrl` at wherever you run this one.

For production, self-host OSRM with a Tamil Nadu OSM extract and set
`OSRM_BASE_URL` - no code changes needed anywhere else.

## 4. Blockchain-based KYC (`blockchain/chain.py`)

Same tamper-evident hash chain as the Node version
(`blockHash = sha256(payloadHash + previousHash + timestamp)`), stored in
`blockchain_ids`. `verify_chain()` lets an admin panel prove integrity.
Swap `issue_blockchain_id()`'s internals for a real chain client later - the
API surface (`blockchainId` on the user) doesn't change.

## 5. API reference

Identical routes/behavior to the Node version - see the interactive docs at
`/docs` once running, or:

**Auth:** `POST /api/auth/create-account` (public), `POST /api/auth/login`
(public), `GET /api/auth/me`, `PATCH /api/auth/me`

**Trips:** `POST /api/trips/`, `GET /api/trips/` (`{upcoming, past}`),
`GET/PATCH/DELETE /api/trips/{tripId}`, `POST /api/trips/{tripId}/start|end`

**Location:** `POST /api/location/ping`, `GET /api/location/current/{userId}`,
`GET /api/location/history/{userId}?limit=`,
`GET /api/location/route-preview?fromLat=&fromLng=&toLat=&toLng=`,
`GET /api/location/snap?lat=&lng=`

**Geofences:** `GET /api/geofences/`, `GET /api/geofences/check?lat=&lng=`,
`POST/PATCH/DELETE /api/geofences/*` (admin)

**SOS:** `POST /api/sos/`, `GET /api/sos/mine`, `GET /api/sos/` (admin),
`PATCH /api/sos/{sosId}/acknowledge|resolve` (officer)

**Emergency contacts:** `GET /api/emergency-contacts/helplines`,
`GET /api/emergency-contacts/nearby?type=&lat=&lng=`

**Safety:** `GET /api/safety/trip/{tripId}`, `GET /api/safety/live?lat=&lng=&tripId=`

**Notifications:** `GET /api/notifications/`, `PATCH /api/notifications/{id}/read`

**E-FIR:** `POST /api/efir/generate/{incidentId}` (officer), `GET /api/efir/`,
`GET /api/efir/{efirId}` (admin)

**Admin:** `POST /api/admin/login` (public), `GET /api/admin/dashboard-summary`

**Socket.io** (`io(url, { auth: { userId, role: 'user'|'admin' } })`):
- emit `location:push` `{ userId, tripId, lat, lng, speedKmh, heading, accuracyMeters }`
- emit `admin:watch-user` `<userId>`
- listen `location:update`, `incident:new`, `sos:new`, `sos:update`, `safety:update`

## 6. Next: Admin Command Center

Send the admin UI whenever it's ready - `/api/admin/dashboard-summary`, the
`admin-room` live broadcast, `incident:new`/`sos:new` events, geofence CRUD,
and E-FIR generation/listing are already there waiting for it.
