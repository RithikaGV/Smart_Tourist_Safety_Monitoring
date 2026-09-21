# Backend Communication Architecture & Data Synchronization Guide
## Smart Tourist Safety & Incident Response System (SIH-25002)

This document explains how the **User Panel (Tourist Mobile App)** and **Admin Panel (Police/Authority Dashboard)** communicate with the backend, and how data flows between the two isolated databases (`tourist_user_db` and `tourist_admin_db`).

---

## 1. Architectural Topology

```
+-----------------------------------------------------------------------------------------+
|                                    TOURIST CLIENTS                                      |
|   - Tourist Mobile App (Online via 4G/5G)                                               |
|   - Tourist Mobile App in Dead-Zone (Offline via Bluetooth/Wi-Fi Direct Mesh)           |
+--------------------------------------------+--------------------------------------------+
                                             |
                                             v
+-----------------------------------------------------------------------------------------+
|                                API GATEWAY & INGESTION LAYER                             |
|  - Reverse Proxy (NGINX / Kong)                                                         |
|  - JWT Authentication & RBAC Filter (Distinguishes Tourists from Police Officers)       |
+---------------------+---------------------------------------------+---------------------+
                      |                                             |
                      v                                             v
+-------------------------------------------+ +-------------------------------------------+
|          TOURIST BACKEND SERVICE          | |           ADMIN BACKEND SERVICE           |
|  (Node.js / Express or Python FastAPI)    | |  (Node.js / Express or Python FastAPI)    |
|                                           | |                                           |
|  Connection Pool:                         | |  Connection Pool:                         |
|  mongodb://.../tourist_user_db            | |  mongodb://.../tourist_admin_db           |
+---------------------+---------------------+ +---------------------+---------------------+
                      |                                             |
                      +----------------------+----------------------+
                                             |
                                             v
+-----------------------------------------------------------------------------------------+
|                                 EVENT BUS & REAL-TIME BROKER                            |
|  - Redis Pub/Sub / Kafka / RabbitMQ (Internal event transport)                          |
|  - Socket.io / WebSocket Cluster (Bi-directional real-time push)                        |
+--------------------------------------------+--------------------------------------------+
                                             |
                      +----------------------+----------------------+
                      |                                             |
                      v                                             v
+-------------------------------------------+ +-------------------------------------------+
|            EDGE SYNC WORKER               | |         BLOCKCHAIN ORACLE WORKER          |
|  Pushes updated Geofence polygons         | |  Mints immutable hashes for check-ins,    |
|  and advisories to mobile local SQLite    | |  SOS distress triggers, and police audits |
+-------------------------------------------+ +-------------------------------------------+
```

---

## 2. Core Communication Flows

### Flow A: Real-Time One-Touch SOS Dispatch (Online & Offline Mesh)
1. **Triggering the SOS**:
   - The tourist taps the emergency SOS button on the mobile app.
   - If **Online**: The app makes an immediate `POST /api/v1/tourist/sos` HTTP request and simultaneously emits a `socket.emit("tourist_sos_distress", payload)` WebSocket event.
   - If **Offline (No Network)**: The phone initiates a **Bluetooth Low Energy (BLE) and Wi-Fi Direct mesh broadcast**. The payload hops across neighboring peer phones until a device with active cellular/internet connection is reached, which proxies the request to `/api/v1/mesh/relay-sos`.
2. **Backend Event Fan-Out**:
   - The Tourist Backend Service receives the SOS payload and writes the primary incident document into `tourist_user_db.sos_alerts`.
   - The service publishes an event `EVENT_SOS_TRIGGERED` onto the Redis event bus.
   - The Admin Backend Service intercepts `EVENT_SOS_TRIGGERED`, extracts the tourist snapshot, creates an active triage record in `tourist_admin_db.sos_management`, and increments `admin_dashboard_metrics.liveSosRequestsUnchecked`.
   - The WebSocket server broadcasts an instant push alert to all on-duty police officers in that taluk/district with sound sirens and GPS pin coordinates.
3. **Blockchain Anchor**:
   - The Blockchain Oracle worker hashes the SOS transaction and writes a block to the immutable ledger in `tourist_admin_db.blockchain_incident_ledgers`.

---

### Flow B: Dynamic Geofencing & Edge Intelligence Synchronization
1. **Officer Draws Danger Zone**:
   - A landslide or flash flood occurs at Pykara Ghat Road.
   - The district authority uses the Admin Panel's Zone Management tool to draw a polygon on the map.
   - The Admin Panel sends `POST /api/v1/admin/geofence-zones` with GeoJSON Polygon data.
   - The document is stored in `tourist_admin_db.geofence_zones`.
2. **Pushing Down to Edge Tourist Devices**:
   - An event `EVENT_GEOFENCE_UPDATED` is dispatched.
   - Firebase Cloud Messaging (FCM) / Apple APNs sends a silent background push to all active tourist apps in that district.
   - The tourist mobile app receives the payload and updates its **local on-device SQLite/Realm spatial cache**.
3. **Zero-Internet Edge Detection**:
   - The tourist walks toward the landslide zone without cellular coverage.
   - The mobile device's background GPS service evaluates the user's location against the locally cached polygons.
   - **Immediately, without needing internet**, the phone sounds a loud alarm: `⚠️ "Danger! Please turn back."`

---

### Flow C: Automated E-FIR Generation & Officer Triage
1. **Tourist Submission**:
   - Tourist reports theft or loss through the mobile app.
   - The mobile app queries `tourist_user_db.users` to automatically populate the tourist's full name, phone, verified KYC ID, and Blockchain DID.
   - Current GPS coordinates and timestamp are attached automatically.
   - Tourist adds photos of broken vehicle locks and clicks "Submit E-FIR".
   - Stored in `tourist_user_db.efir_reports` with status `SUBMITTED`.
2. **Admin/Police Review**:
   - Real-time notification appears on the police station dashboard: `Live E-FIR requests (unchecked)`.
   - The record is mirrored to `tourist_admin_db.efir_management` with status `PENDING`.
   - The Station House Officer (SHO) reviews the evidence, assigns an investigating officer (`officers._id`), registers the formal State Police FIR number (`FIR-2026/OOTY-RURAL/00318`), and transitions status to `INVESTIGATING`.
3. **Status Push to Tourist**:
   - The status change triggers an in-app notification in `tourist_user_db.user_notifications`, notifying the tourist: *"Your E-FIR #EFIR-2026-TN-NIL-0042 has been accepted and Inspector R. Vijayan has been assigned."*

---

### Flow D: Privacy-First Ghost Mode & Investigative Override
1. **Normal Tourist Movement (Ghost Mode Active)**:
   - When Ghost Mode is enabled, the tourist app does **not** send plaintext GPS coordinates to the server.
   - Movement history is encrypted client-side using an ephemeral key and stored strictly on the tourist's phone.
   - Only periodic encrypted heartbeat hashes or anonymized density pings are received.
2. **Investigative Override Trigger**:
   - Under normal circumstances, police **cannot** view tourist history.
   - If an SOS is pressed or a court warrant is issued for a missing person:
     - Officer submits an override application in `tourist_admin_db.investigative_overrides`.
     - System verifies either: (a) An active SOS distress state exists, or (b) Valid judicial warrant reference is logged.
     - The emergency decryption key is released or the client device automatically transmits the decrypted trail.
     - Every access attempt is immutably logged with timestamp, officer badge ID, terminal IP, and reason for complete judicial auditing.

---

## 3. Recommended Backend Implementation (Dual-Connection Pattern)

If implementing a unified Node.js / Express backend, use the **Dual Database Connection Pool** pattern:

```javascript
// config/database.js
const mongoose = require('mongoose');

const userDbConnection = mongoose.createConnection(process.env.USER_DB_URI, {
  maxPoolSize: 50,
  minPoolSize: 10
});

const adminDbConnection = mongoose.createConnection(process.env.ADMIN_DB_URI, {
  maxPoolSize: 20,
  minPoolSize: 5
});

userDbConnection.on('connected', () => console.log('Connected to tourist_user_db'));
adminDbConnection.on('connected', () => console.log('Connected to tourist_admin_db'));

module.exports = { userDbConnection, adminDbConnection };
```

### Models Initialization
```javascript
// models/User.js
const { userDbConnection } = require('../config/database');
const userSchema = new mongoose.Schema({ /* ... schema ... */ });
module.exports = userDbConnection.model('User', userSchema, 'users');

// models/Officer.js
const { adminDbConnection } = require('../config/database');
const officerSchema = new mongoose.Schema({ /* ... schema ... */ });
module.exports = adminDbConnection.model('Officer', officerSchema, 'officers');
```
