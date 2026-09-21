# MongoDB Compass Import & Export Step-by-Step Guide
## Smart Tourist Safety & Incident Response System

This guide shows how you and your teammates can easily import and export the **User Panel** and **Admin Panel** databases using **MongoDB Compass** (GUI).

---

## 1. Prerequisites
1. Install [MongoDB Community Server](https://www.mongodb.com/try/download/community) or have a [MongoDB Atlas](https://www.mongodb.com/cloud/atlas) free cloud cluster.
2. Install [MongoDB Compass](https://www.mongodb.com/try/download/compass).
3. Connect MongoDB Compass to your database:
   - For Local MongoDB: `mongodb://localhost:27017`
   - For MongoDB Atlas: `mongodb+srv://<username>:<password>@cluster0.xxxxx.mongodb.net/`

---

## 2. Importing the Databases into MongoDB Compass

### Phase A: Import User Panel Database (`tourist_user_db`)

1. Open **MongoDB Compass** and click **Connect**.
2. In the left sidebar, click the **`+` (Create Database)** button next to "Databases".
3. Enter:
   - **Database Name**: `tourist_user_db`
   - **Collection Name**: `users`
   - Click **Create Database**.
4. In `tourist_user_db`, click on the `users` collection.
5. In the top toolbar, click **Add Data** -> Select **Import JSON or CSV file**.
6. Browse to your project folder:
   `databases/tourist_user_db/users.json`
7. Ensure **JSON** format is selected, then click **Import**.
8. Repeat steps 4–7 for the remaining 10 collections in `tourist_user_db`:
   * Click **Create Collection** -> Name: `trips` -> Import `trips.json`
   * Click **Create Collection** -> Name: `trip_checklists` -> Import `trip_checklists.json`
   * Click **Create Collection** -> Name: `live_locations` -> Import `live_locations.json`
   * Click **Create Collection** -> Name: `sos_alerts` -> Import `sos_alerts.json`
   * Click **Create Collection** -> Name: `efir_reports` -> Import `efir_reports.json`
   * Click **Create Collection** -> Name: `safety_advisories` -> Import `safety_advisories.json`
   * Click **Create Collection** -> Name: `destination_safety_scores` -> Import `destination_safety_scores.json`
   * Click **Create Collection** -> Name: `local_emergency_services` -> Import `local_emergency_services.json`
   * Click **Create Collection** -> Name: `safe_places_nearby` -> Import `safe_places_nearby.json`
   * Click **Create Collection** -> Name: `user_notifications` -> Import `user_notifications.json`

---

### Phase B: Import Admin Panel Database (`tourist_admin_db`)

1. Click the **`+` (Create Database)** button in MongoDB Compass sidebar.
2. Enter:
   - **Database Name**: `tourist_admin_db`
   - **Collection Name**: `officers`
   - Click **Create Database**.
3. In `tourist_admin_db`, click on the `officers` collection.
4. Click **Add Data** -> Select **Import JSON or CSV file**.
5. Browse to `databases/tourist_admin_db/officers.json` and click **Import**.
6. Create and import the remaining 9 collections in `tourist_admin_db`:
   * Collection: `admin_dashboard_metrics` -> Import `admin_dashboard_metrics.json`
   * Collection: `geofence_zones` -> Import `geofence_zones.json`
   * Collection: `risk_heatmaps` -> Import `risk_heatmaps.json`
   * Collection: `sos_management` -> Import `sos_management.json`
   * Collection: `efir_management` -> Import `efir_management.json`
   * Collection: `blockchain_incident_ledgers` -> Import `blockchain_incident_ledgers.json`
   * Collection: `ai_behavior_analytics` -> Import `ai_behavior_analytics.json`
   * Collection: `investigative_overrides` -> Import `investigative_overrides.json`
   * Collection: `admin_activity_logs` -> Import `admin_activity_logs.json`

---

## 3. Creating Geospatial (`2dsphere`) Indexes in Compass

For real-time proximity alerts and geofence boundary checks to work, create 2dsphere indexes in Compass:

1. **In `tourist_user_db` -> `live_locations`**:
   - Go to the **Indexes** tab.
   - Click **Create Index**.
   - Index Field: `currentCoordinates`, Type: `2dsphere`.
   - Click **Create Index**.

2. **In `tourist_admin_db` -> `geofence_zones`**:
   - Go to the **Indexes** tab.
   - Click **Create Index**.
   - Index Field: `boundaryPolygon`, Type: `2dsphere`.
   - Click **Create Index**.

3. **In `tourist_user_db` -> `local_emergency_services`**:
   - Index Field: `location`, Type: `2dsphere`.

---

## 4. How to Export Data from MongoDB Compass

If you or your team make changes or add new documents and want to export them to JSON:

1. In Compass, open the collection you want to export (e.g., `sos_management`).
2. Click **Collection** in the top menu bar -> Select **Export Collection**.
3. Choose:
   - **Export full collection** (or choose "Filter export" for specific queries).
   - Select fields to export (leave all checked).
   - Click **Select Output**.
4. Choose **JSON** format and select your project's destination folder:
   e.g., `databases/tourist_admin_db/sos_management.json`.
5. Click **Export**.

---

## 5. Quick Test Queries in MongoDB Compass

Test these queries in the **Filter** box in Compass:

### Find nearby emergency services within 5km of Ooty center:
```json
{
  "location": {
    "$near": {
      "$geometry": {
        "type": "Point",
        "coordinates": [76.7025, 11.4112]
      },
      "$maxDistance": 5000
    }
  }
}
```

### Find all unreviewed SOS distress signals:
```json
{
  "status": "PENDING"
}
```

### Find high-risk danger zones:
```json
{
  "riskLevel": "RED_DANGER"
}
```
