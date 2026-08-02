import { useState, useMemo } from 'react'
import { Link } from 'react-router-dom'
import Sidebar from '../components/Sidebar'
import TopNav from '../components/TopNav'
import { useAdmin } from '../AdminContext.jsx'
import './Monitoring.css'

function SOSMonitoring() {
  const { sosAlerts } = useAdmin()
  const [timeFilter, setTimeFilter] = useState('All')
  const [locationFilter, setLocationFilter] = useState('All Locations')
  const [statusFilter, setStatusFilter] = useState('All')

  const filtered = useMemo(() => {
    return sosAlerts.filter(a => {
      const timeOk = timeFilter === 'All' || true
      const locOk = locationFilter === 'All Locations' || a.location.toLowerCase().includes(locationFilter.toLowerCase().split(' ')[0])
      const statusOk = statusFilter === 'All' || a.status === statusFilter
      return timeOk && locOk && statusOk
    })
  }, [sosAlerts, timeFilter, locationFilter, statusFilter])

  const counters = {
    pending: sosAlerts.filter(a => a.status === 'Pending').length,
    investigating: sosAlerts.filter(a => a.status === 'Investigating').length,
    closed: sosAlerts.filter(a => a.status === 'Closed').length,
  }

  return (
    <div className="dashboard-layout">
      <Sidebar />
      <div className="dashboard-main">
        <TopNav />
        <div className="dashboard-content">
          <div className="dashboard-header">
            <h1>SOS Monitoring</h1>
            <p>All tourist SOS requests. Click any row to view full details and take action.</p>
          </div>

          <div className="monitor-stats">
            <div className="mini-stat pending card">
              <span className="ms-icon">⏳</span>
              <div><h4>{counters.pending}</h4><p>Pending</p></div>
            </div>
            <div className="mini-stat investigating card">
              <span className="ms-icon">🔍</span>
              <div><h4>{counters.investigating}</h4><p>Investigating</p></div>
            </div>
            <div className="mini-stat closed card">
              <span className="ms-icon">✅</span>
              <div><h4>{counters.closed}</h4><p>Closed</p></div>
            </div>
            <div className="mini-stat total card">
              <span className="ms-icon">🚨</span>
              <div><h4>{sosAlerts.length}</h4><p>Total Requests</p></div>
            </div>
          </div>

          <div className="filters-bar card">
            <div className="filter-group">
              <label>Filter: Time</label>
              <select value={timeFilter} onChange={(e) => setTimeFilter(e.target.value)}>
                <option>All</option>
                <option>Last 1 Hour</option>
                <option>Last 6 Hours</option>
                <option>Last 24 Hours</option>
                <option>Last 7 Days</option>
              </select>
            </div>
            <div className="filter-group">
              <label>Filter: Location</label>
              <select value={locationFilter} onChange={(e) => setLocationFilter(e.target.value)}>
                <option>All Locations</option>
                <option>Ooty</option>
                <option>Coonoor</option>
                <option>Mysore</option>
                <option>Bandipur</option>
                <option>Brindavan</option>
              </select>
            </div>
            <div className="filter-group">
              <label>Filter: Status</label>
              <select value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)}>
                <option>All</option>
                <option>Pending</option>
                <option>Investigating</option>
                <option>Closed</option>
              </select>
            </div>
          </div>

          <div className="monitor-list card">
            <div className="list-header">
              <span>Request</span>
              <span>Tourist</span>
              <span>Location</span>
              <span>Time</span>
              <span>Priority</span>
              <span>Status</span>
              <span>Action</span>
            </div>
            <div className="list-body">
              {filtered.map(a => (
                <Link key={a.id} to={`/sos-details/${a.id}`} className="list-row">
                  <div className="col-req">
                    <strong>{a.id}</strong>
                  </div>
                  <div className="col-tourist">
                    <div className="avatar-sm">🧑</div>
                    <div>
                      <div className="t-name">{a.touristName}</div>
                      <div className="t-phone">{a.touristPhone}</div>
                    </div>
                  </div>
                  <div className="col-loc">📍 {a.location}</div>
                  <div className="col-time">{a.time}</div>
                  <div className="col-pri">
                    <span className={'priority-pill ' + a.priority.toLowerCase()}>{a.priority}</span>
                  </div>
                  <div className="col-status">
                    <span className={'status-pill ' + a.status.toLowerCase()}>{a.status}</span>
                  </div>
                  <div className="col-action">
                    <span className="view-link">View Details →</span>
                  </div>
                </Link>
              ))}
              {filtered.length === 0 && (
                <div className="empty-list">No SOS alerts match the selected filters.</div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default SOSMonitoring
