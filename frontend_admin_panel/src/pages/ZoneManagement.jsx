import { useState } from 'react'
import { MapContainer, TileLayer, Circle, Marker, Popup } from 'react-leaflet'
import Sidebar from '../components/Sidebar'
import TopNav from '../components/TopNav'
import { useAdmin } from '../AdminContext.jsx'
import './ZoneManagement.css'

const defaultCenter = [11.5000, 76.6700]

const zoneTypeColors = {
  'Landslide area': { stroke: '#dc2626', fill: '#ef4444', dot: 'red' },
  'Restricted zone': { stroke: '#7c3aed', fill: '#8b5cf6', dot: 'purple' },
  'Danger zone': { stroke: '#b91c1c', fill: '#f87171', dot: 'red' },
  'Flood prone': { stroke: '#0369a1', fill: '#38bdf8', dot: 'blue' },
  'Wildlife area': { stroke: '#15803d', fill: '#4ade80', dot: 'green' }
}

function ZoneManagement() {
  const { zones, addZone, updateZone, deleteZone } = useAdmin()
  const [toast, setToast] = useState('')
  const [editingId, setEditingId] = useState(null)

  const [form, setForm] = useState({
    name: '', type: 'Landslide area',
    lat: '11.4500', lng: '76.6000', radius: '600',
    status: 'Active', color: 'red'
  })

  const showToast = (m) => { setToast(m); setTimeout(() => setToast(''), 2200) }
  const updateField = (k, v) => setForm(f => ({ ...f, [k]: v }))

  const resetForm = () => setForm({ name: '', type: 'Landslide area', lat: '11.4500', lng: '76.6000', radius: '600', status: 'Active', color: 'red' })

  const handleAdd = () => {
    if (!form.name.trim() || !form.lat || !form.lng) {
      showToast('⚠️ Please fill Name, Lat, Lng')
      return
    }
    const zone = {
      name: form.name.trim(),
      type: form.type,
      lat: parseFloat(form.lat),
      lng: parseFloat(form.lng),
      radius: parseInt(form.radius) || 500,
      status: form.status,
      color: (zoneTypeColors[form.type] || zoneTypeColors['Danger zone']).dot
    }
    addZone(zone)
    showToast('✅ Zone added & pushed to nearby users instantly')
    resetForm()
  }

  const startEdit = (z) => {
    setEditingId(z.id)
    setForm({ name: z.name, type: z.type, lat: String(z.lat), lng: String(z.lng), radius: String(z.radius), status: z.status, color: z.color })
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }

  const handleUpdate = () => {
    if (!editingId) return
    updateZone(editingId, {
      name: form.name.trim(),
      type: form.type,
      lat: parseFloat(form.lat),
      lng: parseFloat(form.lng),
      radius: parseInt(form.radius) || 500,
      status: form.status,
      color: (zoneTypeColors[form.type] || zoneTypeColors['Danger zone']).dot
    })
    setEditingId(null)
    resetForm()
    showToast('📝 Zone updated. Alert pushed.')
  }

  const handleDelete = (id) => {
    const z = zones.find(x => x.id === id)
    deleteZone(id)
    if (editingId === id) { setEditingId(null); resetForm() }
    showToast(`🗑️ Zone "${z?.name}" removed`)
  }

  const pushAlert = (z) => {
    updateZone(z.id, { lastAlertAt: new Date().toISOString() })
    showToast(`📣 Alert pushed instantly to users near "${z.name}"`)
  }

  const colorsForType = (t) => (zoneTypeColors[t] || zoneTypeColors['Danger zone'])

  return (
    <div className="dashboard-layout">
      <Sidebar />
      <div className="dashboard-main">
        <TopNav />
        <div className="dashboard-content">
          <div className="dashboard-header">
            <h1>Zone Management</h1>
            <p>Draw danger zones on the map, mark landslide / restricted areas, push alerts and edit or remove zones.</p>
          </div>

          {toast && <div className="toast">{toast}</div>}

          <div className="zone-top-card card">
            <div className="zone-top-main">
              <div className={'zone-form-card' + (editingId ? ' is-editing' : '')}>
                <div className="zone-form-head">
                  <h3>{editingId ? '✏️ Edit Existing Zone' : '➕ Draw / Mark New Zone'}</h3>
                  {editingId && <span className="editing-badge">Editing mode</span>}
                </div>
                <div className="form-grid">
                  <div className="form-group full">
                    <label>Zone Name</label>
                    <input type="text" placeholder="e.g. Western Catchment Slopes" value={form.name} onChange={e => updateField('name', e.target.value)} />
                  </div>
                  <div className="form-group">
                    <label>Mark as (Type)</label>
                    <select value={form.type} onChange={e => updateField('type', e.target.value)}>
                      <option>Landslide area</option>
                      <option>Restricted zone</option>
                      <option>Danger zone</option>
                      <option>Flood prone</option>
                      <option>Wildlife area</option>
                    </select>
                  </div>
                  <div className="form-group">
                    <label>Status</label>
                    <select value={form.status} onChange={e => updateField('status', e.target.value)}>
                      <option>Active</option>
                      <option>Draft</option>
                      <option>Expired</option>
                    </select>
                  </div>
                  <div className="form-group">
                    <label>Latitude</label>
                    <input type="number" step="0.0001" value={form.lat} onChange={e => updateField('lat', e.target.value)} />
                  </div>
                  <div className="form-group">
                    <label>Longitude</label>
                    <input type="number" step="0.0001" value={form.lng} onChange={e => updateField('lng', e.target.value)} />
                  </div>
                  <div className="form-group">
                    <label>Radius (m)</label>
                    <input type="number" value={form.radius} onChange={e => updateField('radius', e.target.value)} />
                  </div>
                </div>
                <div className="form-actions">
                  {editingId
                    ? <>
                        <button className="btn btn-primary" onClick={handleUpdate}>💾 Save Changes</button>
                        <button className="btn btn-outline" onClick={() => { setEditingId(null); resetForm() }}>✕ Cancel Edit</button>
                      </>
                    : <button className="btn btn-primary btn-block" onClick={handleAdd}>➕ Add Zone &amp; Push Instant Alert</button>
                  }
                </div>
              </div>

              <div className="zone-legend-card">
                <div className="legend-heading">
                  <span className="legend-icon">🎯</span>
                  <h3>Zone Type Legend</h3>
                </div>
                <div className="legend-grid">
                  {Object.entries(zoneTypeColors).map(([k, v]) => (
                    <div key={k} className={'lg-row ' + v.dot}>
                      <span className={'lg-dot ' + v.dot}></span>
                      <span>{k}</span>
                    </div>
                  ))}
                </div>
                <div className="legend-foot">
                  <p><strong>{zones.length}</strong> zones currently in system<br />
                  <strong>{zones.filter(z => z.status === 'Active').length}</strong> active • <strong>{zones.filter(z => z.status === 'Draft').length}</strong> draft • <strong>{zones.filter(z => z.status === 'Expired').length}</strong> expired</p>
                </div>
              </div>
            </div>
          </div>

          <div className="zone-map-card card">
            <div className="zone-map-head">
              <h3>🗺️ Danger Zones on Map</h3>
              <div className="zone-map-stats">
                <div className="zms-item zms-active"><span>{zones.filter(z => z.status === 'Active').length}</span><label>Active Zones</label></div>
                <div className="zms-item zms-zone"><span>{zones.length}</span><label>Total Zones</label></div>
              </div>
            </div>
            <MapContainer center={defaultCenter} zoom={9} className="leaflet-map-container">
              <TileLayer attribution='&copy; OpenStreetMap' url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
              {zones.map(z => {
                const c = colorsForType(z.type)
                return (
                  <div key={z.id}>
                    <Circle
                      center={[z.lat, z.lng]}
                      radius={z.radius}
                      pathOptions={{
                        color: c.stroke,
                        fillColor: c.fill,
                        fillOpacity: z.status === 'Active' ? 0.25 : 0.1,
                        weight: z.status === 'Active' ? 3 : 2,
                        dashArray: z.status === 'Draft' ? '6 6' : undefined,
                        opacity: z.status === 'Expired' ? 0.4 : 1
                      }}
                    />
                    <Marker position={[z.lat, z.lng]}>
                      <Popup>
                        <strong>{z.name}</strong><br />
                        {z.type} • {z.status}<br />
                        Radius: {z.radius}m
                      </Popup>
                    </Marker>
                  </div>
                )
              })}
            </MapContainer>
          </div>

          <div className="zone-table-card card">
            <div className="zone-table-head">
              <h3>🚧 Zone List (Edit / Push / Remove)</h3>
              <div className="zone-table-count">{zones.length} {zones.length === 1 ? 'zone' : 'zones'}</div>
            </div>
            {zones.length === 0 ? (
              <div className="empty-list">No zones yet. Add your first zone using the form above 👆</div>
            ) : (
              <div className="zone-table">
                <div className="zt-head">
                  <span>Zone</span><span>Type</span><span>Radius</span><span>Status</span><span>Actions</span>
                </div>
                <div className="zt-body">
                  {zones.map(z => (
                    <div key={z.id} className="zt-row">
                      <div className="zt-name">
                        <span className={'zt-dot ' + colorsForType(z.type).dot}></span>
                        <div className="zt-text">
                          <strong>{z.name}</strong>
                          <div className="zt-coords">{z.lat.toFixed(4)}, {z.lng.toFixed(4)}</div>
                        </div>
                      </div>
                      <span className="zt-type">
                        <span className="zt-type-chip">{z.type}</span>
                      </span>
                      <span className="zt-radius">{z.radius}m</span>
                      <span className="zt-status"><span className={'status-pill ' + z.status.toLowerCase()}>{z.status}</span></span>
                      <div className="zt-actions">
                        <button className="btn btn-small btn-success" onClick={() => pushAlert(z)} title="Push instant alert to users">📣 Alert</button>
                        <button className="btn btn-small btn-primary" onClick={() => startEdit(z)}>✏️ Edit</button>
                        <button className="btn btn-small btn-danger" onClick={() => handleDelete(z.id)}>🗑️ Remove</button>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

        </div>
      </div>
    </div>
  )
}

export default ZoneManagement
