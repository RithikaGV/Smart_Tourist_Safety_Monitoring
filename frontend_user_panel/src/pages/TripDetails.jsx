import { useParams, Link } from 'react-router-dom'
import Sidebar from '../components/Sidebar'
import TopNav from '../components/TopNav'
import './TripDetails.css'
import { useTrips } from '../TripsContext'
import { MapContainer, TileLayer, Marker, Popup, Circle } from 'react-leaflet'

function TripDetails() {
  const { id } = useParams()
  const { trips } = useTrips()
  const trip = trips.find(t => t.id === parseInt(id))

  if (!trip) {
    return (
      <div className="dashboard-layout">
        <Sidebar />
        <div className="dashboard-main">
          <TopNav />
          <div className="dashboard-content">
            <Link to="/my-trips" className="back-link">← Back to My Trips</Link>
            <h1>Trip not found!</h1>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="dashboard-layout">
      <Sidebar />
      <div className="dashboard-main">
        <TopNav />
        <div className="dashboard-content">
          <Link to="/my-trips" className="back-link">← Back to My Trips</Link>
          <h1>Trip Details: {trip.destination}</h1>
          <p className="trip-meta">Date: {trip.date} • Time: {trip.time} • {trip.travelers} traveler(s) • {trip.type}</p>

          <div className="trip-details-grid">
            <div className="safety-score-section card">
              <h2>Destination Safety Score</h2>
              <p>Show an easy-to-understand safety rating.</p>
              <div className="safety-score">
                <div className="score-circle">
                  <span className="score-number">8.9</span>
                  <span className="score-label">/10</span>
                </div>
                <div className="score-details">
                  <div className="score-item">
                    <span className="item-icon">🟢</span>
                    <span>Overall Safety: 8.9/10</span>
                  </div>
                  <div className="score-item">
                    <span className="item-icon">🟢</span>
                    <span>Crime Risk: Low</span>
                  </div>
                  <div className="score-item">
                    <span className="item-icon">🟡</span>
                    <span>Road Safety: Medium</span>
                  </div>
                  <div className="score-item">
                    <span className="item-icon">🟢</span>
                    <span>Natural Disaster Risk: Low</span>
                  </div>
                  <div className="score-item">
                    <span className="item-icon">🟡</span>
                    <span>Weather Alerts</span>
                  </div>
                </div>
              </div>
            </div>

            <div className="travel-checklist-section card">
              <h2>Travel Checklist</h2>
              <p>Customizable checklist:</p>
              <ul className="checklist">
                <li><input type="checkbox" /> Passport</li>
                <li><input type="checkbox" /> Tickets</li>
                <li><input type="checkbox" /> Hotel confirmation</li>
                <li><input type="checkbox" /> Medicines</li>
                <li><input type="checkbox" /> Power bank</li>
                <li><input type="checkbox" /> Cash</li>
                <li><input type="checkbox" /> ID proof</li>
                <li><input type="checkbox" /> Emergency contacts</li>
              </ul>
            </div>

            <div className="trip-map-section card">
              <h3>Trip Map</h3>
              <div className="nearby-leaflet-container">
                <MapContainer
                  center={[trip.lat, trip.lng]}
                  zoom={14}
                  style={{ height: '100%', width: '100%', borderRadius: '12px' }}
                >
                  <TileLayer
                    attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                    url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                  />
                  <Marker position={[trip.lat, trip.lng]}>
                    <Popup>
                      <strong>{trip.destination}</strong>
                    </Popup>
                  </Marker>
                  <Circle
                    center={[trip.lat, trip.lng]}
                    radius={500}
                    fillColor="#22c55e"
                    fillOpacity={0.2}
                    color="#22c55e"
                    weight={2}
                  />
                </MapContainer>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default TripDetails
