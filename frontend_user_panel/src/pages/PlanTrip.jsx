import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import Sidebar from '../components/Sidebar'
import TopNav from '../components/TopNav'
import './PlanTrip.css'
import { useTrips } from '../TripsContext'

function PlanTrip() {
  const navigate = useNavigate()
  const { addTrip } = useTrips()
  const [formData, setFormData] = useState({
    destination: '',
    date: '',
    time: '',
    travelers: '',
    type: 'family'
  })

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value })
  }

  const handleSubmit = (e) => {
    e.preventDefault()
    addTrip({
      destination: formData.destination,
      date: formData.date,
      time: formData.time,
      travelers: formData.travelers,
      type: formData.type,
      // Add sample lat/lng for Ooty area
      lat: 11.6075 + (Math.random() * 0.02 - 0.01),
      lng: 76.6635 + (Math.random() * 0.02 - 0.01),
    })
    navigate('/my-trips')
  }

  return (
    <div className="dashboard-layout">
      <Sidebar />
      <div className="dashboard-main">
        <TopNav />
        <div className="dashboard-content">
          <Link to="/dashboard" className="back-link">← Back to Dashboard</Link>
          <h1>Search & Plan Trip</h1>
          <div className="plan-trip-card card">
            <form onSubmit={handleSubmit} className="plan-trip-form">
              <div className="form-grid">
                <div className="form-group">
                  <label>Search destination (place to visit in map)</label>
                  <input
                    type="text"
                    name="destination"
                    value={formData.destination}
                    onChange={handleChange}
                    placeholder="Enter destination"
                    required
                  />
                </div>
                <div className="form-group">
                  <label>Select travel date</label>
                  <input
                    type="date"
                    name="date"
                    value={formData.date}
                    onChange={handleChange}
                    required
                  />
                </div>
                <div className="form-group">
                  <label>Select travel time</label>
                  <input
                    type="time"
                    name="time"
                    value={formData.time}
                    onChange={handleChange}
                    required
                  />
                </div>
                <div className="form-group">
                  <label>Number of travelers</label>
                  <input
                    type="number"
                    name="travelers"
                    value={formData.travelers}
                    onChange={handleChange}
                    placeholder="Enter number"
                    required
                    min="1"
                  />
                </div>
                <div className="form-group">
                  <label>Travel type:</label>
                  <select
                    name="type"
                    value={formData.type}
                    onChange={handleChange}
                  >
                    <option value="family">Family</option>
                    <option value="friends">Friends</option>
                    <option value="business">Business</option>
                    <option value="group">Group</option>
                  </select>
                </div>
              </div>
              <button type="submit" className="btn btn-primary btn-block mt-4">Create New Trip</button>
            </form>
          </div>
        </div>
      </div>
    </div>
  )
}

export default PlanTrip
