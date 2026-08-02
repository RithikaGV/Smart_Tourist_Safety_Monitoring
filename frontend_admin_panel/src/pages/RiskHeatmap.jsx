import { useState, useMemo } from 'react'
import { MapContainer, TileLayer, Circle, Marker, Popup } from 'react-leaflet'
import Sidebar from '../components/Sidebar'
import TopNav from '../components/TopNav'
import { useAdmin } from '../AdminContext.jsx'
import './RiskHeatmap.css'

const touristDensitySpots = [
  { name: 'Ooty Botanical Gardens', lat: 11.4064, lng: 76.6932, density: 95, risk: 'red' },
  { name: 'Ooty Lake', lat: 11.4100, lng: 76.6950, density: 78, risk: 'yellow' },
  { name: 'Doddabetta Peak', lat: 11.4000, lng: 76.7350, density: 45, risk: 'yellow' },
  { name: 'Sim\'s Park Coonoor', lat: 11.3450, lng: 76.7950, density: 62, risk: 'yellow' },
  { name: 'Mysore Palace', lat: 12.3051, lng: 76.6551, density: 88, risk: 'red' },
  { name: 'Chamundi Hills', lat: 12.2700, lng: 76.6700, density: 40, risk: 'green' },
  { name: 'Brindavan Gardens', lat: 12.4200, lng: 76.6000, density: 70, risk: 'yellow' },
  { name: 'Bandipur Safari', lat: 11.7500, lng: 76.6400, density: 28, risk: 'green' }
]

const districtCenter = [11.6500, 76.6500]

function RiskHeatmap() {
  const { touristCounts, zones } = useAdmin()
  const [timeFilter, setTimeFilter] = useState('Now')
  const [locationFilter, setLocationFilter] = useState('All Districts')

  const filteredSpots = useMemo(() => {
    return touristDensitySpots
      .filter(s => locationFilter === 'All Districts' || s.name.toLowerCase().includes(locationFilter.split(' ')[0].toLowerCase()))
  }, [locationFilter])

  const riskCounts = {
    red: filteredSpots.filter(s => s.risk === 'red').length,
    yellow: filteredSpots.filter(s => s.risk === 'yellow').length,
    green: filteredSpots.filter(s => s.risk === 'green').length,
  }

  return (
    <div className="dashboard-layout">
      <Sidebar />
      <div className="dashboard-main">
        <TopNav />
        <div className="dashboard-content">
          <div className="dashboard-header">
            <h1>Risk Heatmap</h1>
            <p>District-wide live map with tourist density and color-coded risk levels</p>
          </div>

          <div className="filters-bar card">
            <div className="filter-section">
              <div className="filter-heading">🕒 Filter By Time</div>
              <div className="filter-group">
                <label>Time Range</label>
                <select value={timeFilter} onChange={(e) => setTimeFilter(e.target.value)}>
                  <option>Now</option>
                  <option>Last 1 Hour</option>
                  <option>Last 6 Hours</option>
                  <option>Last 24 Hours</option>
                  <option>Last 7 Days</option>
                </select>
              </div>
            </div>
            <div className="filter-section">
              <div className="filter-heading">📍 Filter By Location</div>
              <div className="filter-group">
                <label>District / Area</label>
                <select value={locationFilter} onChange={(e) => setLocationFilter(e.target.value)}>
                  <option>All Districts</option>
                  {touristCounts.districtBreakdown.map(d => <option key={d.district}>{d.district}</option>)}
                  <option>Ooty</option>
                  <option>Coonoor</option>
                  <option>Mysore</option>
                </select>
              </div>
            </div>
          </div>

          <div className="heatmap-grid">
            <div className="card heatmap-map-card">
              <h3>🗺️ Live District Map</h3>
              <MapContainer center={districtCenter} zoom={9} className="leaflet-map-container">
                <TileLayer
                  attribution='&copy; OpenStreetMap'
                  url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                />
                {filteredSpots.map((s, i) => (
                  <div key={'d' + i}>
                    <Circle
                      center={[s.lat, s.lng]}
                      radius={300 + s.density * 18}
                      pathOptions={{
                        color: s.risk === 'red' ? '#ef4444' : s.risk === 'yellow' ? '#f59e0b' : '#10b981',
                        fillColor: s.risk === 'red' ? '#ef4444' : s.risk === 'yellow' ? '#f59e0b' : '#10b981',
                        fillOpacity: 0.28,
                        weight: 2
                      }}
                    />
                    <Marker position={[s.lat, s.lng]}>
                      <Popup>
                        <strong>{s.name}</strong><br />
                        Density: {s.density}%<br />
                        Risk: {s.risk.toUpperCase()}
                      </Popup>
                    </Marker>
                  </div>
                ))}
                {zones.filter(z => z.status === 'Active').map(z => (
                  <Circle
                    key={z.id}
                    center={[z.lat, z.lng]}
                    radius={z.radius}
                    pathOptions={{
                      color: z.color === 'red' ? '#dc2626' : '#d97706',
                      fillColor: z.color === 'red' ? '#dc2626' : '#d97706',
                      fillOpacity: 0.2,
                      weight: 3,
                      dashArray: '8 6'
                    }}
                  />
                ))}
              </MapContainer>
              <div className="heatmap-legend">
                <div className="heatmap-legend-head">🎨 Color Legend</div>
                <div className="heatmap-legend-row">
                  <div className="legend-tile safe">
                    <span className="legend-dot green"></span>
                    <div><strong>Safe</strong><span>Low • {riskCounts.green} spots</span></div>
                  </div>
                  <div className="legend-tile crowded">
                    <span className="legend-dot yellow"></span>
                    <div><strong>Crowded</strong><span>Medium • {riskCounts.yellow} spots</span></div>
                  </div>
                  <div className="legend-tile danger">
                    <span className="legend-dot red"></span>
                    <div><strong>Danger</strong><span>High • {riskCounts.red} spots</span></div>
                  </div>
                </div>
              </div>
            </div>

            <div className="heatmap-side">
              <div className="card density-card">
                <h3>👥 Tourist Density Visualization</h3>
                <div className="density-list">
                  {filteredSpots.sort((a, b) => b.density - a.density).map((s, i) => (
                    <div key={i} className="density-row">
                      <div className="density-head">
                        <span>{s.name}</span>
                        <span className={'risk-badge ' + s.risk}>{s.risk.toUpperCase()}</span>
                      </div>
                      <div className="density-bar-wrap">
                        <div
                          className={'density-bar ' + s.risk}
                          style={{ width: s.density + '%' }}
                        ></div>
                      </div>
                      <div className="density-pct">{s.density}%</div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default RiskHeatmap
