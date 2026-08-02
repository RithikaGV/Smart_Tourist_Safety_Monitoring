import { useState, useMemo } from 'react'
import { Link } from 'react-router-dom'
import Sidebar from '../components/Sidebar'
import TopNav from '../components/TopNav'
import { useAdmin } from '../AdminContext.jsx'
import './Monitoring.css'

function EFIRMonitoring() {
  const { efirReports } = useAdmin()
  const [timeFilter, setTimeFilter] = useState('All')
  const [locationFilter, setLocationFilter] = useState('All Locations')
  const [statusFilter, setStatusFilter] = useState('All')

  const filtered = useMemo(() => {
    return efirReports.filter(e => {
      const locOk = locationFilter === 'All Locations' || e.location.toLowerCase().includes(locationFilter.toLowerCase().split(' ')[0])
      const statusOk = statusFilter === 'All' || e.status === statusFilter
      return locOk && statusOk
    })
  }, [efirReports, timeFilter, locationFilter, statusFilter])

  const counters = {
    pending: efirReports.filter(e => e.status === 'Pending').length,
    investigating: efirReports.filter(e => e.status === 'Investigating').length,
    closed: efirReports.filter(e => e.status === 'Closed').length,
  }

  return (
    <div className="dashboard-layout">
      <Sidebar />
      <div className="dashboard-main">
        <TopNav />
        <div className="dashboard-content">
          <div className="dashboard-header">
            <h1>E-FIR Monitoring</h1>
            <p>All filed electronic FIR reports. Click any row to view full details, download FIR copy &amp; take action.</p>
          </div>

          <div className="monitor-stats">
            <div className="mini-stat pending card">
              <span className="ms-icon">⏳</span>
              <div><h4>{counters.pending}</h4><p>Pending Review</p></div>
            </div>
            <div className="mini-stat investigating card">
              <span className="ms-icon">🔍</span>
              <div><h4>{counters.investigating}</h4><p>Under Investigation</p></div>
            </div>
            <div className="mini-stat closed card">
              <span className="ms-icon">✅</span>
              <div><h4>{counters.closed}</h4><p>Closed</p></div>
            </div>
            <div className="mini-stat total card">
              <span className="ms-icon">📋</span>
              <div><h4>{efirReports.length}</h4><p>Total E-FIRs</p></div>
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
                <option>Chamundi</option>
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
            <div className="list-header efir-head">
              <span>FIR Ref</span>
              <span>Incident</span>
              <span>Tourist</span>
              <span>Location</span>
              <span>Time</span>
              <span>Status</span>
              <span>Action</span>
            </div>
            <div className="list-body">
              {filtered.map(e => (
                <Link key={e.id} to={`/efir-details/${e.id}`} className="list-row efir-row">
                  <div className="col-req">
                  <strong className="efir-ref">{e.firCopyRef}</strong>
                  <div className="efir-internal">{e.id}</div>
                  </div>
                  <div className="col-incident">
                    <span className="incident-tag">{e.incidentType}</span>
                  </div>
                  <div className="col-tourist">
                    <div className="avatar-sm">🧑</div>
                    <div>
                      <div className="t-name">{e.touristName}</div>
                      <div className="t-phone">{e.touristPhone}</div>
                    </div>
                  </div>
                  <div className="col-loc">📍 {e.location}</div>
                  <div className="col-time">{e.time}</div>
                  <div className="col-status">
                    <span className={'status-pill ' + e.status.toLowerCase()}>{e.status}</span>
                  </div>
                  <div className="col-action">
                    <span className="view-link">View &amp; Copy FIR →</span>
                  </div>
                </Link>
              ))}
              {filtered.length === 0 && (
                <div className="empty-list">No E-FIR reports match the selected filters.</div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default EFIRMonitoring
