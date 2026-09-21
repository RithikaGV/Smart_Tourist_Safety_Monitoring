const { MongoClient, ObjectId } = require('mongodb');
const fs = require('fs');
const path = require('path');

const uri = 'mongodb://127.0.0.1:27017';

function readJsonFile(relativePath) {
  const fullPath = path.resolve(__dirname, '..', relativePath);
  const rawContent = fs.readFileSync(fullPath, 'utf8');
  return JSON.parse(rawContent);
}

function transformDoc(item) {
  if (Array.isArray(item)) {
    return item.map(transformDoc);
  } else if (item !== null && typeof item === 'object') {
    if (item.$oid) {
      return new ObjectId(item.$oid);
    }
    if (item.$date) {
      return new Date(item.$date);
    }
    const transformed = {};
    for (const key of Object.keys(item)) {
      transformed[key] = transformDoc(item[key]);
    }
    return transformed;
  }
  return item;
}

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

async function seed() {
  console.log('Connecting to local MongoDB service at ' + uri + ' ...');
  const client = new MongoClient(uri);

  try {
    await client.connect();
    console.log('✓ Successfully connected to MongoDB Server!\n');

    // 1. Seed tourist_user_db
    console.log('>>> Loading Database: tourist_user_db (11 Collections)...');
    const userDb = client.db('tourist_user_db');
    for (const colName of userCollections) {
      const data = readJsonFile(`databases/tourist_user_db/${colName}.json`);
      const docs = data.map(transformDoc);
      const col = userDb.collection(colName);
      await col.deleteMany({});
      await col.insertMany(docs);
      console.log(`  ✓ tourist_user_db.${colName} (${docs.length} documents loaded)`);
    }

    // Create Indexes
    await userDb.collection('users').createIndex({ 'auth.email': 1 }, { unique: true });
    await userDb.collection('live_locations').createIndex({ currentCoordinates: '2dsphere' });
    await userDb.collection('sos_alerts').createIndex({ coordinates: '2dsphere' });
    await userDb.collection('local_emergency_services').createIndex({ location: '2dsphere' });
    await userDb.collection('safe_places_nearby').createIndex({ location: '2dsphere' });
    await userDb.collection('safety_advisories').createIndex({ affectedGeoPolygon: '2dsphere' });
    console.log('  ✓ 2dsphere and unique indexes created for tourist_user_db.\n');

    // 2. Seed tourist_admin_db
    console.log('>>> Loading Database: tourist_admin_db (10 Collections)...');
    const adminDb = client.db('tourist_admin_db');
    for (const colName of adminCollections) {
      const data = readJsonFile(`databases/tourist_admin_db/${colName}.json`);
      const docs = data.map(transformDoc);
      const col = adminDb.collection(colName);
      await col.deleteMany({});
      await col.insertMany(docs);
      console.log(`  ✓ tourist_admin_db.${colName} (${docs.length} documents loaded)`);
    }

    // Create Indexes
    await adminDb.collection('officers').createIndex({ officerId: 1 }, { unique: true });
    await adminDb.collection('geofence_zones').createIndex({ boundaryPolygon: '2dsphere' });
    await adminDb.collection('risk_heatmaps').createIndex({ centerCoordinates: '2dsphere' });
    await adminDb.collection('sos_management').createIndex({ sosId: 1 }, { unique: true });
    await adminDb.collection('efir_management').createIndex({ efirNumber: 1 }, { unique: true });
    console.log('  ✓ 2dsphere and unique indexes created for tourist_admin_db.\n');

    console.log('================================================================');
    console.log('  SUCCESS! Both databases are now live in your MongoDB server:');
    console.log('   - tourist_user_db (11 collections)');
    console.log('   - tourist_admin_db (10 collections)');
    console.log('================================================================');
  } catch (err) {
    console.error('Error importing to MongoDB:', err);
  } finally {
    await client.close();
  }
}

seed();
