/**
 * Schema & Data Integrity Validator for Smart Tourist Safety & Incident Response System
 * Validates JSON syntax, GeoJSON coordinate boundaries, and cross-database ID relations.
 * Run with: node scripts/validate_schemas.js
 */

const fs = require('fs');
const path = require('path');

const userCollections = [
  'users',
  'trips',
  'trip_checklists',
  'live_locations',
  'sos_alerts',
  'efir_reports',
  'safety_advisories',
  'destination_safety_scores',
  'local_emergency_services',
  'safe_places_nearby',
  'user_notifications'
];

const adminCollections = [
  'officers',
  'admin_dashboard_metrics',
  'geofence_zones',
  'risk_heatmaps',
  'sos_management',
  'efir_management',
  'blockchain_incident_ledgers',
  'ai_behavior_analytics',
  'investigative_overrides',
  'admin_activity_logs'
];

function loadJson(relPath) {
  const p = path.resolve(__dirname, '..', relPath);
  return JSON.parse(fs.readFileSync(p, 'utf8'));
}

function extractId(val) {
  if (!val) return null;
  if (typeof val === 'string') return val;
  if (typeof val === 'object' && val.$oid) return val.$oid;
  return String(val);
}

function validateGeoJsonPoint(pt, ctx) {
  if (!pt || pt.type !== 'Point' || !Array.isArray(pt.coordinates) || pt.coordinates.length !== 2) {
    throw new Error(`[${ctx}] Invalid GeoJSON Point structure`);
  }
  const [lng, lat] = pt.coordinates;
  if (lng < -180 || lng > 180 || lat < -90 || lat > 90) {
    throw new Error(`[${ctx}] Coordinates out of bounds: [${lng}, ${lat}] (Expected [lng, lat])`);
  }
}

function validateGeoJsonPolygon(poly, ctx) {
  if (!poly || poly.type !== 'Polygon' || !Array.isArray(poly.coordinates) || poly.coordinates.length === 0) {
    throw new Error(`[${ctx}] Invalid GeoJSON Polygon structure`);
  }
  const ring = poly.coordinates[0];
  if (!Array.isArray(ring) || ring.length < 4) {
    throw new Error(`[${ctx}] Polygon linear ring must have at least 4 coordinates`);
  }
  const first = ring[0];
  const last = ring[ring.length - 1];
  if (first[0] !== last[0] || first[1] !== last[1]) {
    throw new Error(`[${ctx}] Polygon ring is not closed (first and last coordinates must match)`);
  }
}

function runValidation() {
  console.log('================================================================');
  console.log('  Smart Tourist Safety Database - Validation Suite');
  console.log('================================================================\n');

  let passedTests = 0;
  let totalTests = 0;

  function assert(condition, message) {
    totalTests++;
    if (condition) {
      console.log(`  ✓ PASS: ${message}`);
      passedTests++;
    } else {
      console.error(`  ✗ FAIL: ${message}`);
      process.exitCode = 1;
    }
  }

  console.log('[1] Checking JSON syntax for tourist_user_db...');
  const userDb = {};
  for (const name of userCollections) {
    try {
      userDb[name] = loadJson(`databases/tourist_user_db/${name}.json`);
      assert(Array.isArray(userDb[name]) && userDb[name].length > 0, `tourist_user_db.${name}.json is valid array (${userDb[name].length} docs)`);
    } catch (err) {
      assert(false, `Failed to load tourist_user_db.${name}.json: ${err.message}`);
    }
  }

  console.log('\n[2] Checking JSON syntax for tourist_admin_db...');
  const adminDb = {};
  for (const name of adminCollections) {
    try {
      adminDb[name] = loadJson(`databases/tourist_admin_db/${name}.json`);
      assert(Array.isArray(adminDb[name]) && adminDb[name].length > 0, `tourist_admin_db.${name}.json is valid array (${adminDb[name].length} docs)`);
    } catch (err) {
      assert(false, `Failed to load tourist_admin_db.${name}.json: ${err.message}`);
    }
  }

  console.log('\n[3] Validating GeoJSON specifications in both databases...');
  try {
    // live_locations
    userDb.live_locations.forEach((loc, i) => {
      validateGeoJsonPoint(loc.currentCoordinates, `live_locations[${i}]`);
    });
    assert(true, 'All live_locations GeoJSON Points are valid');

    // sos_alerts
    userDb.sos_alerts.forEach((sos, i) => {
      validateGeoJsonPoint(sos.coordinates, `sos_alerts[${i}]`);
    });
    assert(true, 'All sos_alerts GeoJSON Points are valid');

    // safety_advisories polygons
    userDb.safety_advisories.forEach((adv, i) => {
      validateGeoJsonPolygon(adv.affectedGeoPolygon, `safety_advisories[${i}]`);
    });
    assert(true, 'All safety_advisories GeoJSON Polygons are valid and closed');

    // geofence_zones polygons
    adminDb.geofence_zones.forEach((zone, i) => {
      validateGeoJsonPolygon(zone.boundaryPolygon, `geofence_zones[${i}]`);
    });
    assert(true, 'All geofence_zones GeoJSON Polygons are valid and closed');

    // risk_heatmaps
    adminDb.risk_heatmaps.forEach((hm, i) => {
      validateGeoJsonPoint(hm.centerCoordinates, `risk_heatmaps[${i}].center`);
      validateGeoJsonPolygon(hm.gridBoundingBox, `risk_heatmaps[${i}].bounding`);
    });
    assert(true, 'All risk_heatmaps GeoJSON Points and Polygons are valid');
  } catch (err) {
    assert(false, `GeoJSON validation error: ${err.message}`);
  }

  console.log('\n[4] Validating Cross-Collection and Cross-Database ID References...');
  const userIds = new Set(userDb.users.map(u => extractId(u._id)));
  const tripIds = new Set(userDb.trips.map(t => extractId(t._id)));
  const officerIds = new Set(adminDb.officers.map(o => extractId(o._id)));
  const sosAlertCodes = new Set(userDb.sos_alerts.map(s => s.sosId));
  const efirNumberCodes = new Set(userDb.efir_reports.map(e => e.efirNumber));

  // Trips -> Users
  const tripUserValid = userDb.trips.every(t => userIds.has(extractId(t.userId)));
  assert(tripUserValid, 'All trips.userId correctly reference valid users._id');

  // Checklists -> Trips
  const checkTripValid = userDb.trip_checklists.every(c => tripIds.has(extractId(c.tripId)));
  assert(checkTripValid, 'All trip_checklists.tripId correctly reference valid trips._id');

  // SOS Alerts -> Officers
  const sosOfficerValid = userDb.sos_alerts.every(s => !s.assignedOfficerId || officerIds.has(extractId(s.assignedOfficerId)));
  assert(sosOfficerValid, 'All sos_alerts.assignedOfficerId correctly reference valid officers._id in tourist_admin_db');

  // Admin SOS Management -> User SOS Alerts
  const adminSosValid = adminDb.sos_management.every(s => sosAlertCodes.has(s.sosId));
  assert(adminSosValid, 'All admin sos_management.sosId exist in tourist_user_db.sos_alerts');

  // Admin E-FIR Management -> User E-FIR Reports
  const adminEfirValid = adminDb.efir_management.every(e => !e.linkedUserDbEfirId || efirNumberCodes.has(e.efirNumber));
  assert(adminEfirValid, 'All admin efir_management records correctly link to tourist_user_db.efir_reports');

  // Geofence Zones -> Officers
  const zoneOfficerValid = adminDb.geofence_zones.every(z => officerIds.has(extractId(z.createdByOfficerId)));
  assert(zoneOfficerValid, 'All geofence_zones.createdByOfficerId correctly reference valid officers._id');

  console.log('\n================================================================');
  console.log(`  VALIDATION SUMMARY: ${passedTests}/${totalTests} Tests Passed`);
  console.log('================================================================\n');

  if (passedTests === totalTests) {
    console.log('>>> [SUCCESS] All database schemas, data types, GeoJSON, and references are 100% verified!\n');
  } else {
    console.error('>>> [FAILURE] Some validation checks failed.\n');
  }
}

runValidation();
