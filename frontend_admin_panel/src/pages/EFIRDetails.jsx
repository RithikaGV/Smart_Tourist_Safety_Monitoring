import { useEffect, useMemo, useState } from 'react'
import { Link, useParams, useNavigate } from 'react-router-dom'
import { MapContainer, TileLayer, Marker, Popup, Circle, useMap } from 'react-leaflet'
import Sidebar from '../components/Sidebar'
import TopNav from '../components/TopNav'
import { useAdmin } from '../AdminContext.jsx'
import { geocodeLocation } from '../utils/geocode.js'
import './Monitoring.css'

function MapCenter({ center }) {
  const map = useMap()
  useEffect(() => {
    if (center) {
      map.setView(center, 14)
    }
  }, [center, map])
  return null
}

function EFIRDetails() {
  const { id } = useParams()
  const navigate = useNavigate()
  const { efirReports, officer, officersList, assignEFIR, updateEFIRStatus } = useAdmin()
  const report = efirReports.find(e => e.id === id)
  const [assignee, setAssignee] = useState(report?.assignedTo || '')
  const [copied, setCopied] = useState(false)
  const [toast, setToast] = useState('')
  const [resolvedPosition, setResolvedPosition] = useState(null)
  const [lookupStatus, setLookupStatus] = useState('')

  const mapCenter = useMemo(() => resolvedPosition || [report?.lat || 11.5, report?.lng || 76.67], [report?.lat, report?.lng, resolvedPosition])

  useEffect(() => {
    let cancelled = false
    if (!report) return

    const runLookup = async () => {
      setLookupStatus('Resolving map location…')
      const result = await geocodeLocation(report.location)
      if (!cancelled && result) {
        setResolvedPosition([result.lat, result.lng])
        setLookupStatus('Location resolved from place name')
      } else if (!cancelled) {
        setResolvedPosition([report.lat, report.lng])
        setLookupStatus('Using saved coordinates')
      }
    }

    runLookup()
    return () => {
      cancelled = true
    }
  }, [report])

  if (!report) {
    return (
      <div className="dashboard-layout">
        <Sidebar />
        <div className="dashboard-main">
          <TopNav />
          <div className="dashboard-content">
            <Link to="/efir-monitoring" className="back-link">← Back to E-FIR Monitoring</Link>
            <div className="card"><h2>E-FIR report not found.</h2></div>
          </div>
        </div>
      </div>
    )
  }

  const showToast = (m) => { setToast(m); setTimeout(() => setToast(''), 2200) }

  const handleCopyFIR = async () => {
    const firText = `===== E-FIR COPY =====\nReference: ${report.firCopyRef}\nInternal ID: ${report.id}\nIncident Type: ${report.incidentType}\nDate & Time: ${report.time}\nComplainant: ${report.touristName} (${report.touristPhone})\nLocation: ${report.location}\nCoords: ${report.lat}, ${report.lng}\n\nDescription:\n${report.description}\n\nStatus: ${report.status}\nAssigned: ${report.assignedTo || 'Unassigned'}`
    try {
      await navigator.clipboard.writeText(firText)
      setCopied(true)
      showToast('📋 FIR Copy copied to clipboard!')
      setTimeout(() => setCopied(false), 2400)
    } catch {
      showToast('📋 Copied locally (see FIR card below)')
    }
  }

  const handleAccept = () => {
    assignEFIR(report.id, officer.name)
    setAssignee(officer.name)
    showToast('✅ Report accepted & assigned to you')
  }

  const handleAssign = () => {
    if (!assignee) return
    assignEFIR(report.id, assignee)
    showToast('👮 Assigned to: ' + assignee)
  }

  const handleStatus = (s) => {
    updateEFIRStatus(report.id, s)
    showToast('📌 Status updated: ' + s)
  }

  return (
    <div className="dashboard-layout">
      <Sidebar />
      <div className="dashboard-main">
        <TopNav />
        <div className="dashboard-content">
          <Link to="/efir-monitoring" className="back-link">← Back to E-FIR Monitoring</Link>
          {toast && <div className="toast">{toast}</div>}

          <div className="details-header card">
            <div>
              <div className="id-badge fir-badge">{report.firCopyRef}</div>
              <h1>E-FIR Report Details</h1>
              <div className="detail-meta">
                <span className="incident-tag-lg">{report.incidentType}</span>
                <span className={'status-pill ' + report.status.toLowerCase()}>{report.status}</span>
                {report.assignedTo && <span className="assign-pill">👮 {report.assignedTo}</span>}
              </div>
            </div>
            <div className="detail-actions">
              <button className={'btn btn-outline' + (copied ? ' copied' : '')} onClick={handleCopyFIR}>
                {copied ? '✅ Copied!' : '📋 Copy E-FIR'}
              </button>
              {report.status === 'Pending' && (
                <button className="btn btn-success" onClick={handleAccept}>✋ Accept Report</button>
              )}
            </div>
          </div>

          <div className="details-grid">
            <div className="card details-info">
              <h3>📅 Date &amp; Time of Report</h3>
              <div className="info-box">{report.time}</div>

              <h3>🧾 E-FIR Copy</h3>
              <div className="fir-copy-card">
                <div className="fir-head">
                <strong>Reference: {report.firCopyRef}</strong>
                <span className="badge">Filed Online</span>
                </div>
                <div className="fir-row"><span>Incident Type:</span><strong>{report.incidentType}</strong></div>
                <div className="fir-row"><span>Complainant:</span><strong>{report.touristName}</strong></div>
                <div className="fir-row"><span>Contact:</span><strong>{report.touristPhone}</strong></div>
                <div className="fir-row"><span>Occurrence Place:</span><strong>{report.location}</strong></div>
                <div className="fir-row"><span>Date / Time:</span><strong>{report.time}</strong></div>
                <div className="fir-desc">
                  <span>Statement / Description:</span>
                  <p>{report.description}</p>
                </div>
              </div>

              <h3>🧑 Tourist Details</h3>
              <div className="info-grid-2">
                <div className="info-item">
                  <label>Name</label><div>{report.touristName}</div>
                </div>
                <div className="info-item">
                  <label>Contact</label><div>{report.touristPhone}</div>
                </div>
              </div>

              <h3>📍 Location Tracking</h3>
              <div className="info-box">
                <div className="loc-main"><strong>{report.location}</strong></div>
                <div className="loc-coords">Lat {report.lat.toFixed(4)}, Lng {report.lng.toFixed(4)}</div>
                <div className="loc-trail">Geo-tagged at time of FIR filing • GPS verified</div>
              </div>
            </div>

            <div className="card details-map-card">
              <h3>🗺️ Incident Location Map</h3>
              <div className="loc-trail" style={{ marginBottom: 8 }}>{lookupStatus}</div>
              <MapContainer center={mapCenter} zoom={14} className="leaflet-map-container small">
                <TileLayer attribution='&copy; OpenStreetMap' url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
                <MapCenter center={mapCenter} />
                <Circle center={mapCenter} radius={400} pathOptions={{ color: '#6366f1', fillColor: '#6366f1', fillOpacity: 0.18, weight: 2 }} />
                <Marker position={mapCenter}>
                  <Popup>
                    <strong>{report.incidentType}</strong><br />
                    FIR: {report.firCopyRef}<br />
                    {report.location}
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
                <button className={'status-btn pending' + (report.status === 'Pending' ? ' active' : '')} onClick={() => handleStatus('Pending')}>⏳ Pending</button>
                <button className={'status-btn investigating' + (report.status === 'Investigating' ? ' active' : '')} onClick={() => handleStatus('Investigating')}>🔍 Investigating</button>
                <button className={'status-btn closed' + (report.status === 'Closed' ? ' active' : '')} onClick={() => handleStatus('Closed')}>✅ Closed</button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default EFIRDetails
