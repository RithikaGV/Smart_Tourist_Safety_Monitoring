# Smart Tourist Safety & Incident Response System (SIH-25002)
## MongoDB Database Architecture & Schema Specification

This document provides the complete structural architecture for the two isolated MongoDB databases designed specifically for the **Smart Tourist Safety and Security System** based on SIH-25002 requirements:
1. **`tourist_user_db`** (Tourist Mobile Application Database)
2. **`tourist_admin_db`** (Police, Disaster Management & Tourism Authority Command Center Database)

---

## 1. High-Level Architectural Model

```
+-----------------------------------------------------------------------------------+
|                            TOURIST CLIENT LAYER (EDGE)                            |
|  - React Native / Flutter App                                                    |
|  - Edge-Intelligence Geofence Engine (Offline evaluation)                         |
|  - Bluetooth Mesh / Wi-Fi Direct Relay Daemon (Zero Network SOS)                  |
|  - Privacy-First Encrypted Ghost Mode Local Storage                              |
+-----------------------------------------+-----------------------------------------+
                                          |
                                          v
+-----------------------------------------------------------------------------------+
|                         BACKEND INTEGRATION & API GATEWAY                         |
|  - Dual Mongoose / MongoDB Native Connection Pools                                |
|  - WebSocket / Socket.io Real-Time Dispatch Engine                                |
|  - AI Pattern-of-Life Anomaly & Route Optimizer                                   |
|  - Web3 / Blockchain Incident Ledger Bridge                                      |
+---------------------+-------------------------------------+-----------------------+
                      |                                     |
                      v                                     v
+-------------------------------------+   +-----------------------------------------+
|     tourist_user_db (User Panel)    |   |     tourist_admin_db (Admin Panel)      |
+-------------------------------------+   +-----------------------------------------+
| 1. users                            |   | 1. officers                             |
| 2. trips                            |   | 2. admin_dashboard_metrics              |
| 3. trip_checklists                  |   | 3. geofence_zones (GeoJSON 2dsphere)    |
| 4. live_locations (GeoJSON 2dsphere)|   | 4. risk_heatmaps (District Grid)        |
| 5. sos_alerts                       |   | 5. sos_management (Triage & SLA)        |
| 6. efir_reports                     |   | 6. efir_management (Police Filing)      |
| 7. safety_advisories                |   | 7. blockchain_incident_ledgers          |
| 8. destination_safety_scores        |   | 8. ai_behavior_analytics                |
| 9. local_emergency_services         |   | 9. investigative_overrides (Legal Audit)|
| 10. safe_places_nearby              |   | 10. admin_activity_logs                 |
| 11. user_notifications              |   +-----------------------------------------+
+-------------------------------------+
```

---

## 2. Database 1: `tourist_user_db` Collections Reference

### 2.1 Collection: `users`
Stores user profile, authentication, biometric flags, emergency contacts, medical profiles, and KYC identity verification.
* **`_id`**: `ObjectId` - Unique Primary Key.
* **`auth`**: `Object`
  * `email`: `String` (Indexed, Unique)
  * `passwordHash`: `String` (Bcrypt/Argon2)
  * `twoFactorEnabled`: `Boolean`
  * `twoFactorMethod`: `String` (`SMS_OTP` | `EMAIL_OTP`)
  * `securityQuestion`: `Object` (`question`, `answerHash`)
  * `biometricEnabled`: `Boolean`
* **`personalInfo`**: `Object`
  * `fullName`: `String`
  * `mobileNumber`: `String` (E.164 format with country code)
  * `dob`: `String` (YYYY-MM-DD)
  * `gender`: `String` (`Male` | `Female` | `Other` | `Prefer not to say`)
  * `nationality`: `String`
  * `preferredLanguage`: `String`
  * `profilePictureUrl`: `String`
* **`kyc`**: `Object`
  * `kycId`: `String` (Unique generated KYC ID e.g., `KYC-IND-2026-00481`)
  * `idProofType`: `String` (`AADHAAR` | `PASSPORT` | `DRIVING_LICENSE`)
  * `idNumberMasked`: `String` (Masked sample format e.g., `XXXXXXXX9481`)
  * `idDocumentUrl`: `String` (Encrypted object storage URI)
  * `verificationStatus`: `String` (`PENDING` | `VERIFIED` | `REJECTED`)
  * `verifiedAt`: `Date`
  * `blockchainId`: `String` (Trip DID hash created upon verification)
* **`emergencyContacts`**: `Array of Objects`
  * `contactId`: `String`
  * `name`: `String`
  * `relationship`: `String`
  * `phoneNumber`: `String`
  * `email`: `String`
  * `isPrimary`: `Boolean`
* **`medicalInfo`**: `Object`
  * `bloodGroup`: `String` (`A+`, `O+`, `B+`, `AB+`, `A-`, `O-`, `B-`, `AB-`)
  * `allergies`: `Array of Strings`
  * `existingMedicalConditions`: `Array of Strings`
  * `regularMedications`: `Array of Strings`
  * `organDonor`: `Boolean`
* **`permissions`**: `Object` (`locationAccess`, `cameraAccess`, `microphoneAccess`, `notifications`, `contactsAccess`, `grantedAt`)
* **`ghostModeSettings`**: `Object`
  * `ghostModeEnabled`: `Boolean`
  * `deviceEncryptedStorageOnly`: `Boolean`
  * `autoSyncOnEmergencySos`: `Boolean`
  * `allowInvestigativeOverrideWithLegalWarrant`: `Boolean`

---

### 2.2 Collection: `trips`
Tracks tourist trips, travel party types, planned waypoints, and adaptive AI route recommendations based on real-time weather and crowd conditions.
* **`_id`**: `ObjectId`
* **`userId`**: `ObjectId` (Ref: `tourist_user_db.users._id`)
* **`blockchainTripId`**: `String`
* **`tripTitle`**: `String`
* **`destinationCity`**: `String` (e.g., "Ooty")
* **`startDate`**: `Date`, **`endDate`**: `Date`
* **`travelersCount`**: `Number`
* **`travelType`**: `String` (`Solo` | `Family` | `Friends` | `Business` | `Group`)
* **`status`**: `String` (`PLANNED` | `CURRENT` | `COMPLETED` | `CANCELLED`)
* **`plannedItinerary`**: `Array of Objects` (`day`, `date`, `placeName`, `category`, `coordinates: GeoJSON Point`, `plannedTime`, `status`)
* **`adaptiveRouting`**: `Object`
  * `isAdaptiveRerouteApplied`: `Boolean`
  * `originalSegment`: `String` (e.g., "Temple -> Waterfall")
  * `recommendedSegment`: `String` (e.g., "Museum -> Temple")
  * `reason`: `String`
  * `weatherFactor`: `String`
  * `crowdFactor`: `String`
  * `roadStatus`: `String`
* **`sharedWith`**: `Array of Objects` (`contactName`, `phoneNumber`, `shareLiveLocation`, `shareItinerary`, `shareToken`)

---

### 2.3 Collection: `trip_checklists`
Customizable travel preparation checklists for each trip.
* **`_id`**: `ObjectId`
* **`tripId`**: `ObjectId` (Ref: `trips._id`)
* **`userId`**: `ObjectId` (Ref: `users._id`)
* **`checklistItems`**: `Array of Objects` (`itemKey`, `title`, `category`, `isChecked`)

---

### 2.4 Collection: `live_locations`
High-frequency ping collection storing geospatial coordinates, mesh relay hops, battery status, and route deviation checks.
* **`_id`**: `ObjectId`
* **`userId`**: `ObjectId` (Ref: `users._id`)
* **`tripId`**: `ObjectId` (Ref: `trips._id`)
* **`currentCoordinates`**: `GeoJSON Point` (`{ "type": "Point", "coordinates": [longitude, latitude] }`) -> Indexed with `2dsphere`
* **`locationAccuracyMeters`**: `Number`
* **`speedKmh`**: `Number`, **`altitudeMeters`**: `Number`, **`headingDegrees`**: `Number`
* **`networkStatus`**: `String` (`CELLULAR_ONLINE` | `OFFLINE_MESH` | `NO_NETWORK`)
* **`meshMetadata`**: `Object` (`isMeshRelayed`, `hopCount`, `relayingDeviceId`)
* **`batteryLevelPercentage`**: `Number`
* **`isGhostModeActive`**: `Boolean`
* **`ghostModeEncryptedPayload`**: `String` (Client-side encrypted blob when Ghost Mode is active)
* **`routeDeviationStatus`**: `Object`
  * `isDeviated`: `Boolean`
  * `deviationDistanceKm`: `Number`
  * `deviationAlertSentAt`: `Date`
  * `userResponseStatus`: `String` (`NORMAL` | `ACKNOWLEDGED_SAFE` | `NO_RESPONSE`)
  * `promptMessage`: `String` ("Are you okay?")

---

### 2.5 Collection: `sos_alerts`
Created when the tourist hits the One-Touch SOS button or an automated timeout occurs.
* **`_id`**: `ObjectId`
* **`sosId`**: `String` (e.g., `SOS-2026-NILGIRIS-0091`)
* **`userId`**: `ObjectId` (Ref: `users._id`)
* **`tripId`**: `ObjectId` (Ref: `trips._id`)
* **`blockchainIncidentHash`**: `String`
* **`triggerType`**: `String` (`ONE_TOUCH_BUTTON` | `ROUTE_DEVIATION_TIMEOUT` | `OFFLINE_MESH_RELAY`)
* **`meshRelayHops`**: `Array of Objects` (`hopNumber`, `peerDeviceId`, `timestamp`)
* **`coordinates`**: `GeoJSON Point` (`[longitude, latitude]`)
* **`locationAddress`**: `String`
* **`mediaEvidence`**: `Object` (`audioRecordingUrl`, `videoSnippetUrl`, `recordedDurationSeconds`)
* **`emergencyContactsNotified`**: `Array of Objects` (`name`, `phone`, `smsSent`, `smsStatus`, `notifiedAt`)
* **`policeNotified`**: `Boolean`
* **`currentStatus`**: `String` (`ACTIVE` | `INVESTIGATING` | `RESOLVED` | `FALSE_ALARM`)
* **`assignedOfficerId`**: `ObjectId` (Cross-reference to `tourist_admin_db.officers._id`)

---

### 2.6 Collection: `efir_reports`
Automated electronic First Information Report (E-FIR) filed directly by the tourist, auto-populated with identity and GPS evidence.
* **`_id`**: `ObjectId`
* **`efirNumber`**: `String` (e.g., `EFIR-2026-TN-NIL-0042`)
* **`userId`**: `ObjectId` (Ref: `users._id`)
* **`tripId`**: `ObjectId` (Ref: `trips._id`)
* **`incidentCategory`**: `String` (`THEFT_LOSS` | `HARASSMENT` | `ACCIDENT` | `FRAUD` | `OTHER`)
* **`incidentLocation`**: `Object` (`placeName`, `landmark`, `coordinates: GeoJSON Point`)
* **`autoPopulatedTouristData`**: `Object` (`touristFullName`, `mobileNumber`, `email`, `kycId`, `blockchainId`)
* **`evidenceFiles`**: `Array of Objects` (`fileType`, `fileUrl`, `description`)
* **`formalPoliceFirNumber`**: `String`
* **`assignedOfficerId`**: `ObjectId` (Cross-reference to `tourist_admin_db.officers._id`)
* **`status`**: `String` (`SUBMITTED` | `PENDING_REVIEW` | `INVESTIGATING` | `REGISTERED` | `CLOSED`)
* **`blockchainVerificationHash`**: `String`

---

### 2.7 Collection: `safety_advisories`
Real-time government advisories for tourist cities (e.g., road closures, heavy rain, flood warnings).
* **`_id`**: `ObjectId`
* **`advisoryCode`**: `String`
* **`targetCity`**: `String`
* **`advisoryType`**: `String` (`HEAVY_RAINFALL_AND_LANDSLIDE` | `WILDFIRE_RESTRICTION` | `ROAD_CLOSURE`)
* **`severity`**: `String` (`INFO` | `MODERATE` | `CRITICAL`)
* **`title`**: `String`, **`summary`**: `String`
* **`affectedGeoPolygon`**: `GeoJSON Polygon` (`[ [ [lng, lat], ... ] ]`)
* **`validFrom`**: `Date`, **`validUntil`**: `Date`, **`isActive`**: `Boolean`

---

### 2.8 Collection: `destination_safety_scores`
Destination rating cards visible in the Tourist App.
* **`_id`**: `ObjectId`
* **`destinationCity`**: `String`, **`placeName`**: `String`
* **`safetyRating`**: `Object`
  * `overallScore`: `Number` (e.g., `8.9` out of 10.0)
  * `scoreBadgeColor`: `String` (`GREEN` | `YELLOW` | `RED`)
  * `crimeRisk`: `String` (`LOW` | `MEDIUM` | `HIGH`)
  * `womensSafety`: `String` (`VERY_HIGH` | `HIGH` | `MEDIUM` | `LOW`)
  * `nightSafety`: `String` (`HIGH` | `MEDIUM` | `LOW`)
  * `naturalDisasterRisk`: `String` (`VERY_LOW` | `LOW` | `MEDIUM` | `HIGH`)
  * `crowdLevel`: `String`
  * `weatherAlerts`: `Array of Strings`
* **`aiSafetyInsights`**: `String`
* **`emergencyAccessSummary`**: `String`

---

### 2.9 Collection: `local_emergency_services`
Geocoded directory of Police stations, Hospitals, Fire stations, Pharmacies, and Help Centers.
* **`_id`**: `ObjectId`
* **`category`**: `String` (`POLICE_STATION` | `HOSPITAL` | `FIRE_STATION` | `PHARMACY` | `TOURIST_HELP_CENTER` | `WOMEN_AND_CHILD_HELPLINE`)
* **`name`**: `String`, **`phoneNumber`**: `String`, **`emergencyHotline`**: `String`
* **`location`**: `GeoJSON Point` (`[lng, lat]`)
* **`address`**: `String`, **`is24x7`**: `Boolean`, **`supportedLanguages`**: `Array of Strings`

---

### 2.10 Collection: `safe_places_nearby`
Verified safe zones recommended to tourists (Verified hotels, safe cafés, 24/7 petrol pumps, guarded ATMs, public transport hubs).
* **`_id`**: `ObjectId`
* **`category`**: `String` (`VERIFIED_HOTEL` | `SAFE_CAFE` | `PETROL_STATION_24X7` | `ATM` | `PUBLIC_TRANSPORT_HUB`)
* **`name`**: `String`, **`location`**: `GeoJSON Point`, **`safetyRating`**: `Number`, **`features`**: `Array of Strings`

---

### 2.11 Collection: `user_notifications`
In-app alerts pushed to the tourist mobile app (Geofence breach warnings, route deviation checks, SOS dispatch progress).
* **`_id`**: `ObjectId`
* **`userId`**: `ObjectId` (Ref: `users._id`)
* **`notificationType`**: `String` (`GEOFENCE_BREACH_WARNING` | `ROUTE_DEVIATION_ALERT` | `SOS_DISPATCH_UPDATE`)
* **`title`**: `String`, **`message`**: `String`, **`severity`**: `String`, **`isRead`**: `Boolean`
* **`actionButton`**: `Object` (`label`, `routePath`)

---

## 3. Database 2: `tourist_admin_db` Collections Reference

### 3.1 Collection: `officers`
Admin and law enforcement credentials, designations, and jurisdiction boundaries.
* **`_id`**: `ObjectId`
* **`officerId`**: `String` (Unique ID e.g., `TN-POL-NIL-4819`)
* **`fullName`**: `String`, **`department`**: `String`, **`designation`**: `String`
* **`badgeNumber`**: `String`, **`email`**: `String`, **`passwordHash`**: `String`, **`phone`**: `String`
* **`assignedJurisdiction`**: `Object` (`district`, `taluk`, `stationAddress`)
* **`currentDutyStatus`**: `String` (`ON_DUTY` | `OFF_DUTY` | `ON_CALL`)
* **`lastKnownCoordinates`**: `GeoJSON Point`
* **`rolePermissions`**: `Array of Strings`

---

### 3.2 Collection: `admin_dashboard_metrics`
Real-time summary counters displayed on the Admin Home Dashboard.
* **`_id`**: `ObjectId`
* **`district`**: `String`
* **`metricsSnapshot`**: `Object`
  * `totalTouristsCount`: `Number`
  * `activeTourists`: `Number`
  * `liveSosRequestsUnchecked`: `Number`
  * `liveEfirRequestsUnchecked`: `Number`
  * `activeDangerZonesCount`: `Number`
  * `officersOnDutyCount`: `Number`
* **`incidentStats`**: `Object` (`todaySosCount`, `todayEfirCount`, `resolvedToday`, `pendingInvestigation`, `averageResponseTimeMinutes`, `meshRelayedIncidentsCount`)
* **`zoneHealth`**: `Object` (`safeGreenCount`, `crowdedYellowCount`, `dangerRedCount`)

---

### 3.3 Collection: `geofence_zones`
Interactive danger and restriction polygons drawn on the map by authorities (landslides, military zones, flood corridors).
* **`_id`**: `ObjectId`
* **`zoneCode`**: `String` (Unique zone code e.g., `ZONE-NILGIRIS-RED-001`)
* **`zoneName`**: `String`
* **`zoneType`**: `String` (`LANDSLIDE_AREA` | `RESTRICTED_FOREST_ZONE` | `HIGH_CROWD_DENSITY_ZONE` | `MILITARY_BORDER`)
* **`riskLevel`**: `String` (`RED_DANGER` | `YELLOW_CROWDED` | `GREEN_SAFE`)
* **`boundaryPolygon`**: `GeoJSON Polygon` (`[ [ [lng, lat], ... ] ]`) -> Indexed with `2dsphere`
* **`alertNotification`**: `Object` (`displayHeadline`, `subText`, `severity`)
* **`edgeSync`**: `Object` (`syncVersion`, `cachedOnEdgeDevicesCount`, `instantPushTriggered`, `pushedAt`)
* **`createdByOfficerId`**: `ObjectId` (Ref: `officers._id`)
* **`isActive`**: `Boolean`

---

### 3.4 Collection: `risk_heatmaps`
District-wide spatial risk density grid.
* **`_id`**: `ObjectId`
* **`gridId`**: `String`
* **`district`**: `String`, **`locationName`**: `String`
* **`colorCode`**: `String` (`GREEN` | `YELLOW` | `RED`)
* **`statusLabel`**: `String` (`SAFE` | `CROWDED` | `DANGER`)
* **`touristDensityCount`**: `Number`
* **`centerCoordinates`**: `GeoJSON Point`
* **`gridBoundingBox`**: `GeoJSON Polygon`
* **`policePersonnelDeployed`**: `Number`

---

### 3.5 Collection: `sos_management`
Authority incident response workbench for managing distress calls.
* **`_id`**: `ObjectId`
* **`sosId`**: `String` (Matches `tourist_user_db.sos_alerts.sosId`)
* **`linkedUserDbSosId`**: `ObjectId` (Cross-reference to `tourist_user_db.sos_alerts._id`)
* **`touristId`**: `ObjectId` (Cross-reference to `tourist_user_db.users._id`)
* **`touristDetailsSnapshot`**: `Object` (`fullName`, `mobileNumber`, `nationality`, `kycId`, `blockchainId`, `bloodGroup`, `primaryEmergencyContact`)
* **`requestDateTime`**: `Date`
* **`locationTracking`**: `Object` (`initialCoordinates`, `currentCoordinates`, `landmark`, `lastPingTimestamp`)
* **`triggerChannel`**: `String` (`CELLULAR_ONLINE` | `BLUETOOTH_MESH_RELAY`)
* **`status`**: `String` (`PENDING` | `INVESTIGATING` | `CLOSED`)
* **`assignedOfficer`**: `Object` (`officerObjectId: Ref officers._id`, `officerId`, `name`, `assignedAt`)
* **`mediaEvidenceReceived`**: `Object` (`hasAudio`, `audioUrl`, `hasVideo`, `videoUrl`)
* **`investigationNotes`**: `Array of Objects` (`note`, `recordedBy`, `timestamp`)
* **`blockchainIncidentHash`**: `String`

---

### 3.6 Collection: `efir_management`
Official police E-FIR review, station filing, and investigation tracking.
* **`_id`**: `ObjectId`
* **`efirNumber`**: `String` (Matches `tourist_user_db.efir_reports.efirNumber`)
* **`touristId`**: `ObjectId` (Ref: `tourist_user_db.users._id`)
* **`touristDetailsSnapshot`**: `Object` (`fullName`, `mobileNumber`, `email`, `kycId`, `idProofType`, `blockchainId`)
* **`efirDocumentCopy`**: `Object` (`generatedPdfUrl`, `digitalSignatureHash`)
* **`status`**: `String` (`PENDING` | `INVESTIGATING` | `CLOSED`)
* **`assignedOfficer`**: `Object` (`officerObjectId: Ref officers._id`, `officerId`, `name`, `assignedAt`)
* **`officialPoliceFirRegistration`**: `Object` (`isOfficiallyRegistered`, `statePoliceFirNo`, `ipcSections`, `policeStation`)
* **`officerRemarks`**: `String`

---

### 3.7 Collection: `blockchain_incident_ledgers`
Permanent cryptographic audit ledger storing hashes of critical tourist events.
* **`_id`**: `ObjectId`
* **`blockNumber`**: `Number`
* **`transactionHash`**: `String` (SHA256 / Hex Tx hash)
* **`previousBlockHash`**: `String`
* **`eventType`**: `String` (`TOURIST_KYC_VERIFIED` | `SOS_ALERT_TRIGGERED` | `POLICE_RESPONDED_DISPATCHED` | `INCIDENT_CLOSED`)
* **`touristBlockchainId`**: `String`
* **`referenceEntity`**: `Object` (`collectionName`, `entityId`, `businessKey`)
* **`immutablePayloadHash`**: `String`
* **`eventDetails`**: `Object` (`summary`, `actor`, `coordinates`, `timestamp`)
* **`gasUsed`**: `Number`, **`blockTimestamp`**: `Date`

---

### 3.8 Collection: `ai_behavior_analytics`
Machine learning anomaly detection records analyzing pattern-of-life deviations.
* **`_id`**: `ObjectId`
* **`alertId`**: `String`
* **`touristBlockchainId`**: `String`
* **`detectionCategory`**: `String` (`SUSPICIOUS_OSCILLATION_MOVEMENT` | `SUDDEN_DEVIATION_UNRESPONSIVE` | `BORDER_BUFFER_LOITERING`)
* **`riskScore`**: `Number` (0 to 100)
* **`confidenceLevel`**: `Number` (0.0 to 1.0)
* **`analysisSummary`**: `String`
* **`movementPatternTrail`**: `Array of Objects` (`step`, `locationName`, `coordinates: GeoJSON Point`, `dwellTimeMinutes`, `recordedAt`)
* **`comparativeBaseline`**: `Object` (`typicalTouristRoute`, `deviationEntropyIndex`, `isOffHours`)
* **`alertStatus`**: `String` (`NEW_ALERT` | `UNDER_OFFICER_REVIEW` | `CLEARED_NORMAL` | `ESCALATED_TO_SOS`)
* **`reviewedByOfficerId`**: `ObjectId` (Ref: `officers._id`)
* **`riskPredictionScoreDistribution`**: `Object`

---

### 3.9 Collection: `investigative_overrides`
Strict legal audit log for accessing encrypted Ghost Mode data.
* **`_id`**: `ObjectId`
* **`overrideRequestId`**: `String`
* **`requestingOfficer`**: `Object` (`officerObjectId: Ref officers._id`, `officerId`, `name`, `department`)
* **`targetTouristBlockchainId`**: `String`
* **`legalJustificationType`**: `String` (`ACTIVE_SOS_DISTRESS` | `SERIOUS_CRIME_INVESTIGATION` | `COURT_WARRANT`)
* **`legalAuthorizationDetails`**: `Object` (`statutoryProvision`, `warrantOrCaseNumber`, `approvingMagistrateOrSuperintendent`)
* **`reasonForOverride`**: `String`
* **`unmaskedDataScope`**: `Array of Strings`
* **`unmaskedTouristData`**: `Object`
* **`auditRecord`**: `Object` (`ipAddress`, `stationTerminalId`, `auditIntegritySignature`)
* **`status`**: `String` (`AUTHORIZED_AND_EXECUTED` | `PENDING_JUDICIAL_APPROVAL` | `REJECTED`)
* **`accessedAt`**: `Date`

---

### 3.10 Collection: `admin_activity_logs`
Chronological activity logs tracking every administrative action.
* **`_id`**: `ObjectId`
* **`logId`**: `String`
* **`officer`**: `Object` (`officerObjectId`, `officerId`, `fullName`, `department`)
* **`actionCategory`**: `String` (`SOS_TRIAGE_ASSIGNMENT` | `GEOFENCE_ZONE_ACTIVATION` | `EFIR_STATUS_UPDATE`)
* **`actionDescription`**: `String`
* **`targetResource`**: `Object` (`collectionName`, `documentId`, `businessKey`)
* **`requestOrigin`**: `Object` (`ipAddress`, `userAgent`, `locationTerminal`)
* **`status`**: `String` (`SUCCESS` | `FAILED`)
* **`timestamp`**: `Date`

---

## 4. Cross-Database ID References & Index Strategy

### Cross-Database Relationships
| User DB Collection | User DB Field | Target Admin DB Collection | Target Admin DB Field | Purpose |
|---|---|---|---|---|
| `users` | `_id` | `sos_management` | `touristId` | Direct reference to tourist profile in SOS triage |
| `users` | `_id` | `efir_management` | `touristId` | Direct reference to tourist profile in E-FIR investigation |
| `users` | `kyc.blockchainId` | `blockchain_incident_ledgers`| `touristBlockchainId` | Immutable audit trail linkage |
| `sos_alerts` | `sosId` | `sos_management` | `sosId` | Synchronized SOS incident tracking across apps |
| `sos_alerts` | `assignedOfficerId`| `officers` | `_id` | Field officer handling the rescue mission |
| `efir_reports` | `efirNumber` | `efir_management` | `efirNumber` | Synchronized E-FIR filing reference |

### Essential MongoDB Geospatial & Performance Indexes
Execute these in MongoDB Compass or via `scripts/seed_database.js`:

```javascript
// tourist_user_db
db.users.createIndex({ "auth.email": 1 }, { unique: true });
db.users.createIndex({ "kyc.kycId": 1 }, { unique: true });
db.users.createIndex({ "kyc.blockchainId": 1 }, { unique: true });
db.live_locations.createIndex({ "currentCoordinates": "2dsphere" });
db.live_locations.createIndex({ "userId": 1, "recordedAt": -1 });
db.sos_alerts.createIndex({ "coordinates": "2dsphere" });
db.sos_alerts.createIndex({ "sosId": 1 }, { unique: true });
db.local_emergency_services.createIndex({ "location": "2dsphere" });
db.safe_places_nearby.createIndex({ "location": "2dsphere" });
db.safety_advisories.createIndex({ "affectedGeoPolygon": "2dsphere" });

// tourist_admin_db
db.officers.createIndex({ "officerId": 1 }, { unique: true });
db.officers.createIndex({ "email": 1 }, { unique: true });
db.geofence_zones.createIndex({ "boundaryPolygon": "2dsphere" });
db.geofence_zones.createIndex({ "zoneCode": 1 }, { unique: true });
db.risk_heatmaps.createIndex({ "centerCoordinates": "2dsphere" });
db.sos_management.createIndex({ "sosId": 1 }, { unique: true });
db.sos_management.createIndex({ "status": 1, "requestDateTime": -1 });
db.efir_management.createIndex({ "efirNumber": 1 }, { unique: true });
db.blockchain_incident_ledgers.createIndex({ "transactionHash": 1 }, { unique: true });
db.blockchain_incident_ledgers.createIndex({ "touristBlockchainId": 1, "blockTimestamp": -1 });
db.investigative_overrides.createIndex({ "overrideRequestId": 1 }, { unique: true });
```
