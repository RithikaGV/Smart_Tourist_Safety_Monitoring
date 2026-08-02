import { Link } from 'react-router-dom'
import Sidebar from '../components/Sidebar'
import TopNav from '../components/TopNav'
import './MyTrips.css'
import { useTrips } from '../TripsContext'

function MyTrips() {
  const { trips, deleteTrip, classifyTrips } = useTrips()
  const { past, current, upcoming } = classifyTrips(trips)

  // Helper to render trip card
  const renderTripCard = (trip) => (
    <div key={trip.id} className="trip-card card">
      <Link to={`/trip-details/${trip.id}`} className="trip-link">
        <h3>{trip.destination}</h3>
        <p className="trip-date">{trip.date} at {trip.time}</p>
        <p className="trip-travelers">{trip.travelers} traveler(s) • {trip.type}</p>
      </Link>
      <div className="trip-actions">
        <button className="btn btn-small btn-outline">Edit</button>
        <button className="btn btn-small btn-danger" onClick={() => deleteTrip(trip.id)}>Delete</button>
      </div>
    </div>
  )

  // Helper to render a section
  const renderSection = (title, tripList) => {
    const noTripsStyle = {
      width: '100%',
      gridColumn: '1 / -1',
      padding: '24px',
      textAlign: 'center',
      color: '#64748b',
      fontSize: '18px'
    };
    return (
      <div key={title} className="trips-section">
        <h2 className="trips-section-title">{title}</h2>
        <div className="trips-grid">
          {tripList.length > 0 ? tripList.map(renderTripCard) : (
            <div className="no-trips-message" style={noTripsStyle}>
              No trips
            </div>
          )}
        </div>
      </div>
    );
  }

  return (
    <div className="dashboard-layout">
      <Sidebar />
      <div className="dashboard-main">
        <TopNav />
        <div className="dashboard-content">
          <Link to="/dashboard" className="back-link">← Back to Dashboard</Link>
          <h1>My Trips</h1>
          <p>Display upcoming, current, and past trips.</p>

          {renderSection("Current Trips", current)}
          {renderSection("Upcoming Trips", upcoming)}
          {renderSection("Past Trips", past)}
        </div>
      </div>
    </div>
  )
}

export default MyTrips
