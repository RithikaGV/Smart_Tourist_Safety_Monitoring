# 🛡️ Smart Tourist Safety and Incident Response System (SIH-25002)
### Dual MongoDB Database Architecture, Schemas, & Sample Datasets

[![MongoDB](https://img.shields.io/badge/MongoDB-6.0%2B-green.svg)](https://www.mongodb.com/)
[![GeoJSON](https://img.shields.io/badge/GeoJSON-2dsphere-blue.svg)](https://geojson.org/)
[![Blockchain](https://img.shields.io/badge/Ledger-Tamper--Proof-orange.svg)](https://ethereum.org/)
[![Privacy](https://img.shields.io/badge/Privacy-Ghost%20Mode-critical.svg)](#privacy-first-ghost-mode)
[![Zero-PII](https://img.shields.io/badge/Zero--PII-Masked%20Dummy%20Data-brightgreen.svg)](#privacy--zero-pii-policy)

This repository contains the complete production-grade **dual MongoDB database architecture**, collection schemas, and realistic mock datasets designed specifically for the **Smart Tourist Safety and Security System** (SIH-25002).

The system keeps tourists safe while traveling—even in remote areas with **zero cellular connectivity**—using **Edge Computing, Bluetooth/Wi-Fi Direct Mesh Networking, Geo-Fencing, and Blockchain-based Digital ID**.

---

## 📂 Repository Structure

```
smart_tourist_safety_db/
├── README.md                                  # Main project documentation & team guide
├── .gitignore                                 # Git ignore file for secrets and node artifacts
├── docs/
│   ├── ARCHITECTURE.md                        # Complete database schemas, BSON types & ER relationships
│   ├── BACKEND_COMMUNICATION.md               # API Gateway, WebSockets, Mesh sync & Blockchain flows
│   ├── MONGODB_COMPASS_GUIDE.md               # Visual step-by-step import/export tutorial
│   └── GITHUB_SETUP_GUIDE.md                  # Git commands, branching, and pushing to GitHub
├── databases/
│   ├── tourist_user_db/                       # User Panel (Tourist Mobile App Database)
│   │   ├── users.json                         # Profiles, KYC, Medical, Emergency Contacts
│   │   ├── trips.json                         # Itineraries, Travel Types, Adaptive Routes
│   │   ├── trip_checklists.json               # Travel preparation checklists
│   │   ├── live_locations.json                # GeoJSON pings, Mesh hops, Deviation status
│   │   ├── sos_alerts.json                    # One-Touch & Mesh SOS distress records
│   │   ├── efir_reports.json                  # Auto-filled Tourist E-FIR theft/incident reports
│   │   ├── safety_advisories.json             # City warnings (Landslide, Rainfall, Wildfire)
│   │   ├── destination_safety_scores.json     # AI scores (8.9/10, Crime, Women's, Night safety)
│   │   ├── local_emergency_services.json      # Geocoded Police, Hospitals, Fire, Helplines
│   │   ├── safe_places_nearby.json            # Verified hotels, 24/7 petrol pumps, ATMs, cafes
│   │   └── user_notifications.json            # In-app push alerts (Danger zones, SOS updates)
│   └── tourist_admin_db/                      # Admin Panel (Police / Authority Control Room)
│       ├── officers.json                      # Police & Disaster Coordinator credentials
│       ├── admin_dashboard_metrics.json       # Live tourist counts, unreviewed SOS/E-FIR stats
│       ├── geofence_zones.json                # Interactive hazard polygons (Landslide, Restricted)
│       ├── risk_heatmaps.json                 # District-wide Green/Yellow/Red risk grids
│       ├── sos_management.json                # Authority SOS triage, dispatch & officer assignment
│       ├── efir_management.json               # Official police station FIR filing & investigation
│       ├── blockchain_incident_ledgers.json   # Tamper-proof cryptographic event logs
│       ├── ai_behavior_analytics.json         # Pattern-of-life anomaly & suspicious loop detector
│       ├── investigative_overrides.json       # Strict judicial audit log for unmasking Ghost Mode
│       └── admin_activity_logs.json           # Audit logs of all administrative actions
└── scripts/
    ├── seed_database.js                       # One-click mongosh/Node.js automated seeder & indexer
    └── validate_schemas.js                    # Automated test suite for GeoJSON & ID cross-references
```

---

## 🏛️ System Databases Overview

### 1. User Panel Database (`tourist_user_db`)
Tailored for the tourist mobile application, localized on-device caching, and personal safety utilities:
* **`users`**: Secure onboarding with KYC verification, masked Aadhaar/Passport proof, unique Blockchain DID hash, medical info (blood group, allergies, medications, organ donor), emergency contacts, and 2FA settings.
* **`trips`**: Multi-destination itineraries (e.g., Pykara Falls, Mudumalai Reserve, Botanical Garden) with party type (Solo, Family, Group), and **Adaptive AI Routing** (e.g., rerouting Waterfall -> Museum due to heavy rain).
* **`trip_checklists`**: Packing and safety checklists (Passport, tickets, power bank, cash, offline helplines).
* **`live_locations`**: GeoJSON 2dsphere coordinates with speed, battery level, network state (`CELLULAR_ONLINE` vs `OFFLINE_MESH`), route deviation flags, and encrypted Ghost Mode payload.
* **`sos_alerts`**: Emergency triggers capturing coordinates, multi-hop mesh relays, audio/video evidence clips, and SMS delivery tracking to emergency contacts.
* **`efir_reports`**: Direct theft and incident filing auto-populated with tourist credentials, timestamps, and GPS evidence.
* **`safety_advisories`**: City-wide warnings (Ooty/Nilgiris) with affected polygon zones for landslides, floods, and wildfire restrictions.
* **`destination_safety_scores`**: Visual AI safety cards (Overall score e.g. `8.9/10`, Crime Risk: `Low`, Women's Safety: `High`, Night Safety: `Medium`, Disaster Risk: `Low`).
* **`local_emergency_services`**: Searchable 24x7 directory of Police stations, Trauma hospitals, Ambulances, Fire stations, and Tourist Help Centers.
* **`safe_places_nearby`**: Curated directory of verified hotels, safe cafés, 24/7 petrol pumps, guarded ATMs, and transport hubs.
* **`user_notifications`**: Real-time danger alerts (e.g. `⚠️ "Danger! Please turn back."`) when entering geofenced hazard zones.

---

### 2. Admin Panel Database (`tourist_admin_db`)
Built for Police Departments, District Disaster Management Authorities, and Tourism Boards:
* **`officers`**: Pre-provisioned logins for law enforcement officers, badge numbers, designations, jurisdictions, and patrol coordinates.
* **`admin_dashboard_metrics`**: High-level counters (Total tourists, active tourists, unreviewed live SOS distress alerts, pending E-FIRs, and response SLA).
* **`geofence_zones`**: Authority-drawn GeoJSON polygons for active landslides, military borders, and forest cores, synced directly to mobile edge devices.
* **`risk_heatmaps`**: Spatial density grid with real-time color coding:
  * 🟢 **Green (Safe)**: Normal density, clear conditions.
  * 🟡 **Yellow (Crowded)**: High tourist footfall, traffic bottlenecks.
  * 🔴 **Red (Danger)**: Active landslide, accident, or distress call in progress.
* **`sos_management`**: Operational triage console for distress calls with status transitions (`PENDING` ➔ `INVESTIGATING` ➔ `CLOSED`), officer assignment, and live responder dispatch tracking.
* **`efir_management`**: Police desk for reviewing citizen E-FIRs, attaching official State Police FIR numbers, IPC sections, and investigation progress.
* **`blockchain_incident_ledgers`**: Immutable cryptographic block records of critical events (Check-in, SOS triggered, Police dispatched, Case closed) preventing tampering or unauthorized deletion.
* **`ai_behavior_analytics`**: Predictive Pattern-of-Life machine learning detector flagging unusual movement loops (e.g., suspicious midnight border oscillations or prolonged unresponsive deviations).
* **`investigative_overrides`**: Strict legal audit logger ensuring privacy; allows decrypting a tourist's travel history only upon an active SOS or authorized court warrant.
* **`admin_activity_logs`**: Chronological forensic audit log of all officer actions.

---

## 🚀 Quick Start Guide

### Option 1: One-Click Automated Import (Recommended)

1. Ensure **MongoDB** is running locally (`mongodb://localhost:27017`) or have your MongoDB Atlas URI.
2. Open terminal in this folder and run:
   ```bash
   mongosh "mongodb://localhost:27017" scripts/seed_database.js
   ```
   *This automatically creates both databases, drops stale collections, seeds all 21 JSON datasets, and builds all `2dsphere` and unique indexes.*

3. Run the validation suite:
   ```bash
   node scripts/validate_schemas.js
   ```

---

### Option 2: Visual GUI Import via MongoDB Compass

1. Open **MongoDB Compass** and click **Connect**.
2. Follow the detailed step-by-step instructions in [docs/MONGODB_COMPASS_GUIDE.md](./docs/MONGODB_COMPASS_GUIDE.md).
3. Create `tourist_user_db` and import the 11 collection JSON files from `databases/tourist_user_db/`.
4. Create `tourist_admin_db` and import the 10 collection JSON files from `databases/tourist_admin_db/`.

---

## 🌐 Backend Communication & Edge Sync

For a detailed explanation of the dual connection pool pattern, real-time WebSocket fan-out, Bluetooth Low Energy (BLE) mesh routing, and edge geofencing cache, refer to:
👉 [docs/BACKEND_COMMUNICATION.md](./docs/BACKEND_COMMUNICATION.md)

---

## 📤 Pushing to Your GitHub Repository

To push this database structure to your GitHub account:

```bash
# 1. Initialize git
git init

# 2. Stage all files
git add .

# 3. Create initial commit
git commit -m "feat: complete Smart Tourist Safety MongoDB database architecture and datasets"

# 4. Set main branch and remote URL (replace with your repo URL)
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/smart-tourist-safety-database.git

# 5. Push to GitHub
git push -u origin main
```

For more detailed collaboration instructions, see [docs/GITHUB_SETUP_GUIDE.md](./docs/GITHUB_SETUP_GUIDE.md).

---

## 🔒 Privacy & Zero-PII Policy

> [!IMPORTANT]
> **Strict Mock Data Guarantee**:
> In accordance with privacy regulations and project guidelines, **no real Aadhaar numbers, Passport credentials, private mobile numbers, or actual officer credentials are used in this repository**. All numbers, names, hashes, and document URIs are synthetic dummy data set in the sample district of Nilgiris / Ooty.
