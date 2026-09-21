/**
 * Automated Database Seeding Script for Smart Tourist Safety & Incident Response System
 * Usage with mongosh:
 *   mongosh "mongodb://localhost:27017" scripts/seed_database.js
 * Or with Node.js:
 *   node scripts/seed_database.js
 */

const fs = require('fs');
const path = require('path');

function readJsonFile(relativePath) {
  const fullPath = path.resolve(__dirname, '..', relativePath);
  const rawContent = fs.readFileSync(fullPath, 'utf8');
  return JSON.parse(rawContent);
}

// Convert Extended JSON ($oid, $date) to native MongoDB types
function transformExtendedJson(item) {
  if (Array.isArray(item)) {
    return item.map(transformExtendedJson);
  } else if (item !== null && typeof item === 'object') {
    if (item.$oid) {
      return typeof ObjectId !== 'undefined' ? new ObjectId(item.$oid) : item.$oid;
    }
    if (item.$date) {
      return new Date(item.$date);
    }
    const transformed = {};
    for (const key of Object.keys(item)) {
      transformed[key] = transformExtendedJson(item[key]);
    }
    return transformed;
  }
  return item;
}

async function runSeed() {
  console.log('================================================================');
  console.log('  Smart Tourist Safety System - MongoDB Seeder');
  console.log('================================================================\n');

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

  // Check if running in mongosh environment
  const isMongosh = typeof db !== 'undefined';

  if (!isMongosh) {
    console.log('[INFO] Running in Node.js environment. To directly seed MongoDB, use:');
    console.log('       mongosh "mongodb://localhost:27017" scripts/seed_database.js\n');
    console.log('Validating files for tourist_user_db:');
    userCollections.forEach(col => {
      const data = readJsonFile(`databases/tourist_user_db/${col}.json`);
      console.log(`  ✓ ${col}.json (${data.length} docs ready)`);
    });

    console.log('\nValidating files for tourist_admin_db:');
    adminCollections.forEach(col => {
      const data = readJsonFile(`databases/tourist_admin_db/${col}.json`);
      console.log(`  ✓ ${col}.json (${data.length} docs ready)`);
    });

    console.log('\n[SUCCESS] All 21 JSON collection files are valid and ready for import!');
    return;
  }

  // --- MONGOSH EXECUTION ---
  console.log('>>> Seeding tourist_user_db...');
  const userDb = db.getSiblingDB('tourist_user_db');

  for (const col of userCollections) {
    const filePath = `databases/tourist_user_db/${col}.json`;
    const rawData = readJsonFile(filePath);
    const docs = transformExtendedJson(rawData);
    userDb.getCollection(col).drop();
    userDb.getCollection(col).insertMany(docs);
    console.log(`  [OK] tourist_user_db.${col} seeded (${docs.length} documents)`);
  }

  // Create Indexes on tourist_user_db
  console.log('>>> Creating geospatial and unique indexes on tourist_user_db...');
  userDb.users.createIndex({ 'auth.email': 1 }, { unique: true });
  userDb.users.createIndex({ 'kyc.kycId': 1 }, { unique: true });
  userDb.users.createIndex({ 'kyc.blockchainId': 1 }, { unique: true });
  userDb.live_locations.createIndex({ currentCoordinates: '2dsphere' });
  userDb.sos_alerts.createIndex({ coordinates: '2dsphere' });
  userDb.local_emergency_services.createIndex({ location: '2dsphere' });
  userDb.safe_places_nearby.createIndex({ location: '2dsphere' });
  userDb.safety_advisories.createIndex({ affectedGeoPolygon: '2dsphere' });
  console.log('  [OK] User DB indexes created successfully.');

  console.log('\n>>> Seeding tourist_admin_db...');
  const adminDb = db.getSiblingDB('tourist_admin_db');

  for (const col of adminCollections) {
    const filePath = `databases/tourist_admin_db/${col}.json`;
    const rawData = readJsonFile(filePath);
    const docs = transformExtendedJson(rawData);
    adminDb.getCollection(col).drop();
    adminDb.getCollection(col).insertMany(docs);
    console.log(`  [OK] tourist_admin_db.${col} seeded (${docs.length} documents)`);
  }

  // Create Indexes on tourist_admin_db
  console.log('>>> Creating geospatial and unique indexes on tourist_admin_db...');
  adminDb.officers.createIndex({ officerId: 1 }, { unique: true });
  adminDb.geofence_zones.createIndex({ boundaryPolygon: '2dsphere' });
  adminDb.geofence_zones.createIndex({ zoneCode: 1 }, { unique: true });
  adminDb.risk_heatmaps.createIndex({ centerCoordinates: '2dsphere' });
  adminDb.sos_management.createIndex({ sosId: 1 }, { unique: true });
  adminDb.efir_management.createIndex({ efirNumber: 1 }, { unique: true });
  adminDb.blockchain_incident_ledgers.createIndex({ transactionHash: 1 }, { unique: true });
  console.log('  [OK] Admin DB indexes created successfully.');

  console.log('\n================================================================');
  console.log('  DATABASE SEEDING COMPLETED SUCCESSFULLY!');
  console.log('================================================================');
}

runSeed();
