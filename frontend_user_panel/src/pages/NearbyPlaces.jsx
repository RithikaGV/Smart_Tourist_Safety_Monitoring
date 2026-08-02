import { useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import Sidebar from '../components/Sidebar'
import TopNav from '../components/TopNav'
import './NearbyPlaces.css'
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet'

function NearbyPlaces() {
  const { type } = useParams()
  const [selectedPlace, setSelectedPlace] = useState(null)
  const userLocation = [11.6075, 76.6635] // Default: Ooty

  // Sample place data
  const placesData = {
    "police-stations": [
      { id: 1, name: "Ooty Police Station", address: "Commercial Rd, Ooty, Tamil Nadu 643001", lat: 11.6020, lng: 76.6560, phone: "+91 423 244 0200" },
      { id: 2, name: "Charring Cross Police Station", address: "Charring Cross, Ooty, Tamil Nadu 643001", lat: 11.6050, lng: 76.6630, phone: "+91 423 244 1200" },
    ],
    "hospitals": [
      { id: 1, name: "KGH Hospital Ooty", address: "Commercial Rd, Ooty, Tamil Nadu 643001", lat: 11.6030, lng: 76.6580, phone: "+91 423 244 2500" },
      { id: 2, name: "St. Joseph's Hospital", address: "Forest Gate, Ooty, Tamil Nadu 643001", lat: 11.6080, lng: 76.6680, phone: "+91 423 244 3500" },
    ],
    "fire-stations": [
      { id: 1, name: "Ooty Fire Station", address: "Upper Bazaar, Ooty, Tamil Nadu 643001", lat: 11.6100, lng: 76.6600, phone: "101" },
    ],
    "pharmacies": [
      { id: 1, name: "Apollo Pharmacy", address: "Commercial Rd, Ooty, Tamil Nadu 643001", lat: 11.6040, lng: 76.6600, phone: "+91 423 244 4500" },
      { id: 2, name: "MedPlus Ooty", address: "Charring Cross, Ooty, Tamil Nadu 643001", lat: 11.6060, lng: 76.6640, phone: "+91 423 244 5500" },
    ],
    "tourist-help-centers": [
      { id: 1, name: "Tamil Nadu Tourism Office", address: "Charring Cross, Ooty, Tamil Nadu 643001", lat: 11.6055, lng: 76.6620, phone: "+91 423 244 6500" },
    ],
    "verified-hotels": [
      { id: 1, name: "Hotel Savoy - IHCL SeleQtions", address: "Garden Rd, Ooty, Tamil Nadu 643001", lat: 11.6090, lng: 76.6580, phone: "+91 423 222 3333" },
      { id: 2, name: "Fortune Resort Sullivan Court", address: "Elk Hill Rd, Ooty, Tamil Nadu 643001", lat: 11.6070, lng: 76.6650, phone: "+91 423 222 4444" },
    ],
    "safe-cafes": [
      { id: 1, name: "Cafe Coffee Day - Ooty", address: "Commercial Rd, Ooty, Tamil Nadu 643001", lat: 11.6035, lng: 76.6610, phone: "+91 98765 43210" },
      { id: 2, name: "The Tea Garden Cafe", address: "Upper Bazaar, Ooty, Tamil Nadu 643001", lat: 11.6095, lng: 76.6610, phone: "+91 98765 43211" },
    ],
    "petrol-stations": [
      { id: 1, name: "Indian Oil Petrol Pump", address: "Mysore Rd, Ooty, Tamil Nadu 643001", lat: 11.6010, lng: 76.6500, phone: "+91 98765 43212" },
      { id: 2, name: "BPCL Petrol Pump", address: "Coonoor Rd, Ooty, Tamil Nadu 643001", lat: 11.6150, lng: 76.6600, phone: "+91 98765 43213" },
    ],
    "atms": [
      { id: 1, name: "SBI ATM", address: "Charring Cross, Ooty, Tamil Nadu 643001", lat: 11.6052, lng: 76.6625, phone: "" },
      { id: 2, name: "HDFC ATM", address: "Commercial Rd, Ooty, Tamil Nadu 643001", lat: 11.6042, lng: 76.6595, phone: "" },
    ],
    "transport-hubs": [
      { id: 1, name: "Ooty Bus Stand", address: "Gandhi Rd, Ooty, Tamil Nadu 643001", lat: 11.6060, lng: 76.6570, phone: "" },
      { id: 2, name: "Ooty Railway Station", address: "Railway Station Rd, Ooty, Tamil Nadu 643001", lat: 11.6015, lng: 76.6630, phone: "" },
    ],
    "tourist-info-centers": [
      { id: 1, name: "Tamil Nadu Tourism Information Center", address: "Charring Cross, Ooty, Tamil Nadu 643001", lat: 11.6058, lng: 76.6622, phone: "+91 423 244 7500" },
    ],
  }

  // Helper to format title
  const formatTitle = (type) => {
    return type.split('-').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ')
  }

  const places = placesData[type] || []

  return (
    <div className="dashboard-layout">
      <Sidebar />
      <div className="dashboard-main">
        <TopNav />
        <div className="dashboard-content">
          <Link to="/dashboard" className="back-link">← Back to Dashboard</Link>
          <h1>Nearby {formatTitle(type)}</h1>

          <div className="nearby-places-grid">
            <div className="places-list card">
              <h3>List of Places</h3>
              {places.map(place => (
                <div
                  key={place.id}
                  className={`place-item ${selectedPlace?.id === place.id ? 'selected' : ''}`}
                  onClick={() => setSelectedPlace(place)}
                >
                  <div className="place-name">{place.name}</div>
                  <div className="place-address">{place.address}</div>
                  {place.phone && <div className="place-phone">📞 {place.phone}</div>}
                  <div className="place-actions">
                    <a
                      href={`https://www.openstreetmap.org/directions?from=${userLocation[0]},${userLocation[1]}&to=${place.lat},${place.lng}`}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="btn btn-primary btn-small"
                      onClick={(e) => e.stopPropagation()}
                    >
                      📍 Get Directions
                    </a>
                  </div>
                </div>
              ))}
            </div>
            <div className="places-map card">
              <h3>Map View</h3>
              <div className="nearby-leaflet-container">
                <MapContainer
                  center={selectedPlace ? [selectedPlace.lat, selectedPlace.lng] : userLocation}
                  zoom={14}
                  style={{ height: '100%', width: '100%', borderRadius: '12px' }}
                >
                  <TileLayer
                    attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                    url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                  />
                  {/* User's location */}
                  <Marker position={userLocation}>
                    <Popup>
                      <strong>Your Location</strong>
                    </Popup>
                  </Marker>
                  {/* All places */}
                  {places.map(place => (
                    <Marker
                      key={place.id}
                      position={[place.lat, place.lng]}
                      eventHandlers={{ click: () => setSelectedPlace(place) }}
                    >
                      <Popup>
                        <strong>{place.name}</strong><br/>
                        {place.address}
                        {place.phone && <><br/>{place.phone}</>}
                      </Popup>
                    </Marker>
                  ))}
                </MapContainer>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default NearbyPlaces
