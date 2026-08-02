import { useState } from 'react'
import { Link, useParams, useNavigate } from 'react-router-dom'
import { MapContainer, TileLayer, Marker, Popup, Circle } from 'react-leaflet'
import Sidebar from '../components/Sidebar'
import TopNav from '../components/TopNav'
import { useAdmin } from '../AdminContext.jsx'
import './Monitoring.css'

function SOSDetails() {
  const { id } = useParams()
  const navigate = useNavigate()
  const { sosAlerts, officer, officersList, assignSOS, updateSOSStatus } = useAdmin()
  const alert = sosAlerts.find(a => a.id === id)
  const [assignee, setAssignee] = useState(alert?.assignedTo || '')
  const [toast, setToast] = useState('')

  if (!alert) {
    return (
      <div className="dashboard-layout">
        <Sidebar />
        <div className="dashboard-main">
          <TopNav />
          <div className="dashboard-content">
            <Link to="/sos-monitoring" className="back-link">← Back to SOS Monitoring</Link>
            <div className="card"><h2>SOS Alert not found.</h2></div>
          </div>
        </div>
      </div>
    )
  }

  const showToast = (m) => { setToast(m); setTimeout(() => setToast(''), 2200) }

  const handleAccept = () => {
    assignSOS(alert.id, officer.name)
    setAssignee(officer.name)
    showToast('✅ Request accepted & assigned to you')
  }

  const handleAssign = () => {
    if (!assignee) return
    assignSOS(alert.id, assignee)
    showToast('👮 Assigned to: ' + assignee)
  }

  const handleStatus = (s) => {
    updateSOSStatus(alert.id, s)
    showToast('📌 Status updated: ' + s)
  }

  return (
    <div className="dashboard-layout">
      <Sidebar />
      <div className="dashboard-main">
        <TopNav />
        <div className="dashboard-content">
          <Link to="/sos-monitoring" className="back-link">← Back to SOS Monitoring</Link>
          {toast && <div className="toast">{toast}</div>}

          <div className="details-header card">
            <div>
              <div className="id-badge">{alert.id}</div>
              <h1>SOS Request Details</h1>
              <div className="detail-meta">
                <span className={'priority-pill ' + alert.priority.toLowerCase()}>{alert.priority} Priority</span>
                <span className={'status-pill ' + alert.status.toLowerCase()}>{alert.status}</span>
                {alert.assignedTo && <span className="assign-pill">👮 {alert.assignedTo}</span>}
              </div>
            </div>
            <div className="detail-actions">
              {alert.status === 'Pending' && (
                <button className="btn btn-success" onClick={handleAccept}>✋ Accept Request</button>
              )}
              <button className="btn btn-danger" onClick={() => navigate('/sos-monitoring')}>🚨 Emergency Dispatch</button>
            </div>
          </div>

          <div className="details-grid">
            <div className="card details-info">
              <h3>📅 Date &amp; Time of Request</h3>
              <div className="info-box">{alert.time}</div>

              <h3>🧑 Tourist Details</h3>
              <div className="info-grid-2">
                <div className="info-item">
                  <label>Name</label><div>{alert.touristName}</div>
                </div>
                <div className="info-item">
                  <label>Contact</label><div>{alert.touristPhone}</div>
                </div>
              </div>

              <h3>📍 Location Tracking</h3>
              <div className="info-box">
                <div className="loc-main"><strong>{alert.location}</strong></div>
                <div className="loc-coords">Lat {alert.lat.toFixed(4)}, Lng {alert.lng.toFixed(4)}</div>
                <div className="loc-trail">Live trail updated 2 min ago • Signal: Strong 📶</div>
              </div>

              <h3>📝 Tourist Note</h3>
              <div className="info-box note-box">"{alert.notes}"</div>
            </div>

            <div className="card details-map-card">
              <h3>🗺️ Live Location Map</h3>
              <MapContainer center={[alert.lat, alert.lng]} zoom={14} className="leaflet-map-container small">
                <TileLayer attribution='&copy; OpenStreetMap' url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
                <Circle center={[alert.lat, alert.lng]} radius={500} pathOptions={{ color: '#ef4444', fillColor: '#ef4444', fillOpacity: 0.18, weight: 2 }} />
                <Marker position={[alert.lat, alert.lng]}>
                  <Popup>
                    <strong>{alert.touristName}</strong><br />
                    SOS: {alert.id}<br />
                    {alert.location}
                  </Popup>
                </Marker>
              </MapContainer>
            </div>

            <div className="card details-actions-card">
              <h3>🤝 Accept / Assign Officer</h3>
              <div className="action-row">
                <label>Assign to officer</label>
                <select value={assignee} onChange={(e) => setAssignee(e.target.value)}>
                  <option value="">-- Select an officer --</option>
                  {officersList.map(o => <option key={o.officerId} value={o.name}>{o.name} ({o.department})</option>)}
                </select>
                <button className="btn btn-primary" onClick={handleAssign}>Assign</button>
              </div>

              <h3 style={{ marginTop: 24 }}>📌 Update Status</h3>
              <div className="status-buttons">
                <button className={'status-btn pending' + (alert.status === 'Pending' ? ' active' : '')} onClick={() => handleStatus('Pending')}>⏳ Pending</button>
                <button className={'status-btn investigating' + (alert.status === 'Investigating' ? ' active' : '')} onClick={() => handleStatus('Investigating')}>🔍 Investigating</button>
                <button className={'status-btn closed' + (alert.status === 'Closed' ? ' active' : '')} onClick={() => handleStatus('Closed')}>✅ Closed</button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default SOSDetails
