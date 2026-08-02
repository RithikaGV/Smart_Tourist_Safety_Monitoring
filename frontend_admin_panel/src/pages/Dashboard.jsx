import { Link } from 'react-router-dom'
import Sidebar from '../components/Sidebar'
import TopNav from '../components/TopNav'
import { useAdmin } from '../AdminContext.jsx'
import './Dashboard.css'

function Dashboard() {
  const { touristCounts, sosAlerts, efirReports, incidentStats, zones } = useAdmin()
  const pendingSOS = sosAlerts.filter(a => a.status === 'Pending').length
  const pendingEFIR = efirReports.filter(e => e.status === 'Pending').length
  const investigating = sosAlerts.filter(a => a.status === 'Investigating').length
    + efirReports.filter(e => e.status === 'Investigating').length

  const statCards = [
    { label: 'Total Tourists', value: touristCounts.total.toLocaleString(), icon: '🧑‍🤝‍🧑', gradient: 'primary', hint: 'Registered across district' },
    { label: 'Active Tourists', value: touristCounts.active.toLocaleString(), icon: '📍', gradient: 'success', hint: 'Currently in tracking zone' },
    { label: 'Live SOS Requests', value: pendingSOS, icon: '🚨', gradient: 'danger', hint: 'Unchecked by officers' },
    { label: 'Live E-FIR Requests', value: pendingEFIR, icon: '📋', gradient: 'warning', hint: 'Unchecked by officers' }
  ]

  const maxStat = Math.max(...incidentStats.map(s => s.count))

  return (
    <div className="dashboard-layout">
      <Sidebar />
      <div className="dashboard-main">
        <TopNav />
        <div className="dashboard-content">
          <div className="dashboard-header">
            <h1>Admin Dashboard</h1>
            <p>Live overview of tourist safety operations across the district</p>
          </div>

          <div className="stats-grid">
            {statCards.map((s, i) => (
              <div key={i} className={'stat-card card gradient-' + s.gradient}>
                <div className="stat-icon-wrap"><span className="stat-icon">{s.icon}</span></div>
                <div className="stat-info">
                  <div className="stat-value">{s.value}</div>
                  <div className="stat-label">{s.label}</div>
                  <div className="stat-hint">{s.hint}</div>
                </div>
              </div>
            ))}
          </div>

          <div className="dashboard-grid">
            <div className="card incident-stats">
              <h3>📈 Incident Stats (This Month)</h3>
              <div className="incident-list">
                {incidentStats.map((s, i) => (
                  <div key={i} className="incident-row">
                    <div className="incident-label">{s.category}</div>
                    <div className="incident-bar-wrap">
                      <div
                        className="incident-bar"
                        style={{ width: `${(s.count / maxStat) * 100}%` }}
                      ></div>
                    </div>
                    <div className="incident-count">
                      <strong>{s.count}</strong>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="card district-breakdown">
              <h3>🗺️ Tourists By District</h3>
              <div className="district-list">
                {touristCounts.districtBreakdown.map((d, i) => (
                  <div key={i} className="district-row">
                    <span className="district-name">{d.district}</span>
                    <span className="district-count">{d.count.toLocaleString()}</span>
                  </div>
                ))}
              </div>
              <div className="active-cases-wrap">
                <h3>⚡ Active Cases</h3>
                <div className="active-cases-grid">
                  <div className="mini-stat pending"><span>Pending</span><strong>{pendingSOS + pendingEFIR}</strong></div>
                  <div className="mini-stat investigating"><span>Investigating</span><strong>{investigating}</strong></div>
                  <div className="mini-stat zones"><span>Active Zones</span><strong>{zones.filter(z => z.status === 'Active').length}</strong></div>
                </div>
              </div>
            </div>

            <div className="card quick-alerts">
              <h3>🚨 Latest SOS Alerts</h3>
              <div className="alerts-list">
                {sosAlerts.slice(0, 4).map(a => (
                  <Link key={a.id} to={`/sos-details/${a.id}`} className="alert-row">
                    <div className={'alert-priority ' + a.priority.toLowerCase()}></div>
                    <div className="alert-body">
                      <div className="alert-top"><strong>{a.touristName}</strong> <span className={'status-pill ' + a.status.toLowerCase()}>{a.status}</span></div>
                      <div className="alert-sub">{a.location}</div>
                      <div className="alert-time">{a.time}</div>
                    </div>
                  </Link>
                ))}
              </div>
              <Link to="/sos-monitoring" className="see-all-link">View all SOS alerts →</Link>
            </div>

            <div className="card quick-efir">
              <h3>📋 Latest E-FIR Reports</h3>
              <div className="efir-list">
                {efirReports.slice(0, 4).map(e => (
                  <Link key={e.id} to={`/efir-details/${e.id}`} className="efir-row">
                    <div className="efir-id">{e.id}</div>
                    <div className="efir-body">
                      <div className="efir-top"><strong>{e.incidentType}</strong> <span className={'status-pill ' + e.status.toLowerCase()}>{e.status}</span></div>
                      <div className="efir-sub">{e.touristName} • {e.location}</div>
                      <div className="efir-time">{e.time}</div>
                    </div>
                  </Link>
                ))}
              </div>
              <Link to="/efir-monitoring" className="see-all-link">View all E-FIR reports →</Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Dashboard
