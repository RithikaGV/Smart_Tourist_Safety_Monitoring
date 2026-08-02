import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import Sidebar from '../components/Sidebar'
import TopNav from '../components/TopNav'
import './Dashboard.css'
import { MapContainer, TileLayer, Marker, Popup, Circle } from 'react-leaflet'
import { useTrips } from '../TripsContext'

function Dashboard() {
  const [showGeofenceAlert, setShowGeofenceAlert] = useState(false)
  const [showOverdueAlert, setShowOverdueAlert] = useState(false)
  const [userLocation, setUserLocation] = useState([11.6075, 76.6635]) // Default: Ooty (Pyakara Falls area)
  const dangerZones = [
    { center: [11.5900, 76.6800], radius: 500, name: "Forest Area" },
    { center: [11.6200, 76.6400], radius: 300, name: "Landslide Zone" }
  ]
  const { trips, classifyTrips } = useTrips()
  const { current } = classifyTrips(trips)
  const currentTrip = current[0] // Get first current trip if exists

  useEffect(() => {
    const timer = setTimeout(() => {
      setShowGeofenceAlert(true)
    }, 5000)
    return () => clearTimeout(timer)
  }, [])

  useEffect(() => {
    if (currentTrip) {
      const tripDateTime = new Date(`${currentTrip.date}T${currentTrip.time}`)
      const now = new Date()
      const threeHours = 3 * 60 * 60 * 1000 // 3 hours in milliseconds
      const overdueTimer = setTimeout(() => {
        if (now - tripDateTime > threeHours) {
          setShowOverdueAlert(true)
        }
      }, 3000)
      return () => clearTimeout(overdueTimer)
    }
  }, [currentTrip])

  const closeAlert = () => {
    setShowGeofenceAlert(false)
  }

  const closeOverdueAlert = () => {
    setShowOverdueAlert(false)
  }

  return (
    <div className="dashboard-layout">
      <Sidebar />
      <div className="dashboard-main">
        <TopNav />
        <div className="dashboard-content">
          {showGeofenceAlert && (
            <div className="geofence-notification">
              <div className="notification-content">
                <span className="notification-icon">⚠️</span>
                <span className="notification-text">
                  Entering a geofenced dangerous area! Please stay alert.
                </span>
                <button className="notification-close" onClick={closeAlert}>×</button>
              </div>
            </div>
          )}

          {showOverdueAlert && (
            <div className="geofence-notification overdue-alert">
              <div className="notification-content">
                <span className="notification-icon">⚠️</span>
                <span className="notification-text">
                  You have not reached your destination for over 3 hours! Check in or send an SOS if you need help.
                </span>
                <button className="notification-close" onClick={closeOverdueAlert}>×</button>
              </div>
            </div>
          )}

          <div className="dashboard-header">
            <h1>Welcome Back!</h1>
            <p>Your safety is our priority</p>
          </div>

          <div className="sos-section">
            <button className="sos-emergency-btn">
              🚨 Emergency SOS
            </button>
          </div>

          {currentTrip ? (
            <Link to={`/trip-details/${currentTrip.id}`} className="current-trip-section card">
              <h2>Current Trip</h2>
              <div className="trip-details">
                <p><strong>{currentTrip.destination}</strong> • {currentTrip.date} at {currentTrip.time}</p>
              </div>
            </Link>
          ) : (
            <div className="current-trip-section card no-trip">
              <h2>Current Trip</h2>
              <div className="trip-details">
                <p style={{ color: '#64748b', fontSize: '18px' }}>NO CURRENT ONGOING TRIPS</p>
              </div>
            </div>
          )}

          <div className="dashboard-grid">
            <div className="map-section card">
              <h3>Your Location & Geofenced Areas</h3>
              <p>View your current location and nearby danger zones</p>
              <div className="leaflet-map-container">
                <MapContainer center={userLocation} zoom={14} style={{ height: '100%', width: '100%', borderRadius: '12px' }}>
                  <TileLayer
                    attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                    url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                  />
                  <Marker position={userLocation}>
                    <Popup>
                      <div>
                        <strong>Your Location</strong>
                      </div>
                    </Popup>
                  </Marker>
                  {dangerZones.map((zone, idx) => (
                    <Circle
                      key={idx}
                      center={zone.center}
                      radius={zone.radius}
                      fillColor="#ef4444"
                      fillOpacity={0.4}
                      color="#ef4444"
                      weight={2}
                    >
                      <Popup>
                        <strong>⚠️ {zone.name}</strong><br/>
                        Danger Zone - Do not enter!
                      </Popup>
                    </Circle>
                  ))}
                </MapContainer>
              </div>
            </div>

            <div className="advisories-section card">
              <h3>Live Travel Advisories</h3>
              <p>Important updates for your trip</p>
              <div className="advisory-list">
                <div className="advisory-item">
                  <span>🌧️</span> Heavy Rainfall
                </div>
                <div className="advisory-item">
                  <span>⚠️</span> Road Closures
                </div>
                <div className="advisory-item">
                  <span>🔥</span> Wildfire warning
                </div>
              </div>
            </div>

            <div className="emergency-services-section card">
              <h3>Nearby Emergency Services</h3>
              <p>Tap to see locations</p>
              <div className="services-list">
                <Link to="/nearby/police-stations" className="service-item">🚓 Police Stations</Link>
                <Link to="/nearby/hospitals" className="service-item">🏥 Hospitals</Link>
                <Link to="/nearby/fire-stations" className="service-item">🚒 Fire Stations</Link>
                <Link to="/nearby/pharmacies" className="service-item">💊 Pharmacies</Link>
                <Link to="/nearby/tourist-help-centers" className="service-item">🆘 Tourist Help Centers</Link>
              </div>
            </div>

            <div className="emergency-numbers-section card">
              <h3>Local Emergency Contacts</h3>
              <div className="numbers-list">
                <div className="number-item">Police: 100</div>
                <div className="number-item">Ambulance: 108</div>
                <div className="number-item">Fire Department: 101</div>
                <div className="number-item">Women's Helpline: 1091</div>
                <div className="number-item">Disaster Management: 1078</div>
              </div>
            </div>

            <div className="safe-places-section card">
              <h3>Safe Places Nearby</h3>
              <p>Recommended trusted locations</p>
              <div className="safe-places-list">
                <Link to="/nearby/verified-hotels" className="place-item">Verified hotels</Link>
                <Link to="/nearby/safe-cafes" className="place-item">Safe cafes</Link>
                <Link to="/nearby/petrol-stations" className="place-item">24/7 petrol stations</Link>
                <Link to="/nearby/atms" className="place-item">ATMs</Link>
                <Link to="/nearby/transport-hubs" className="place-item">Public transport hubs</Link>
                <Link to="/nearby/tourist-info-centers" className="place-item">Government tourist information centers</Link>
              </div>
            </div>

            <div className="share-trip-section card">
              <h3>Share Your Trip</h3>
              <p>Keep your loved ones informed</p>
              <div className="share-buttons">
                <button className="btn btn-primary">Share Itinerary</button>
                <button className="btn btn-outline">Share Live Location</button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Dashboard
