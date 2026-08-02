import { useState } from 'react'
import Sidebar from '../components/Sidebar'
import TopNav from '../components/TopNav'
import { useAdmin } from '../AdminContext.jsx'
import './AIAnalytics.css'

const patternDetections = [
  { id: 'P-01', title: 'High-risk cluster after 22:00', desc: '3 incidents in Botanical Gardens area between 22:00–00:00 over last 7 days.', risk: 'High', rec: 'Deploy 2 additional patrol units after 21:30.', freq: '2.1x baseline', hit: '73%' },
  { id: 'P-02', title: 'Weekend theft surge on Mysore Rd', desc: 'Pickpocket reports +45% on Saturdays near city bus stand.', risk: 'Medium', rec: 'Deploy plain-clothes officers and CCTV spot checks.', freq: '1.45x baseline', hit: '61%' },
  { id: 'P-03', title: 'Landslide risk correlation with rain', desc: 'Model detects 3.2x higher SOS calls 6h after heavy rain (> 40mm).', risk: 'High', rec: 'Pre-emptively evacuate 3 zones when red rain alert issued.', freq: '3.2x baseline', hit: '89%' },
  { id: 'P-04', title: 'Language barrier incidents', desc: 'Non-Indian tourists 2.7x more likely to file harassment FIRs.', risk: 'Low', rec: 'Add multilingual kiosks and officer badges.', freq: '2.7x baseline', hit: '54%' }
]

const suspiciousMovements = [
  { id: 'SM-01', entity: 'Unregistered vehicle TN-00-XX-0000', path: 'Ooty → Coonoor → Bandipur (3 loops in 6h)', severity: 'High', firstSeen: '2026-07-26 09:12', flaggedBy: 'Anomaly Model v3', score: 91 },
  { id: 'SM-02', entity: 'Group of 4 males (crowd 47)', path: 'Circling single female tourist at Ooty Lake', severity: 'Medium', firstSeen: '2026-07-26 12:40', flaggedBy: 'Behavior Net', score: 76 },
  { id: 'SM-03', entity: 'Tourist #T-2048', path: 'Loitering in restricted zone Z-02 past entry permit expiry', severity: 'High', firstSeen: '2026-07-26 14:05', flaggedBy: 'Geo-fence Rules', score: 88 }
]

function AIAnalytics() {
  const { touristCounts, incidentStats, sosAlerts, efirReports, zones } = useAdmin()
  const totalAlerts = sosAlerts.length + efirReports.length
  const [toast, setToast] = useState('')
  const showToast = (m) => { setToast(m); setTimeout(() => setToast(''), 2200) }

  const kpi = [
    { label: 'Patterns Detected', value: patternDetections.length, icon: '🧠', grad: 'indigo', sub: 'Across 6 models' },
    { label: 'Suspicious Alerts', value: suspiciousMovements.length, icon: '⚠️', grad: 'amber', sub: 'Needs review' },
    { label: 'Profiles Analyzed', value: touristCounts.active.toLocaleString(), icon: '👥', grad: 'emerald', sub: 'Active this week' },
    { label: 'Data Points Fed', value: totalAlerts + zones.length + incidentStats.reduce((s, i) => s + i.count, 0), icon: '📈', grad: 'pink', sub: 'Last 30 days' }
  ]

  const gradBg = (g) => {
    const map = {
      indigo: 'linear-gradient(145deg, #e0e7ff 0%, #c7d2fe 100%)',
      amber: 'linear-gradient(145deg, #fef3c7 0%, #fde68a 100%)',
      emerald: 'linear-gradient(145deg, #d1fae5 0%, #a7f3d0 100%)',
      pink: 'linear-gradient(145deg, #fce7f3 0%, #fbcfe8 100%)'
    }
    return map[g]
  }
  const gradText = (g) => {
    const map = { indigo: '#312e81', amber: '#78350f', emerald: '#065f46', pink: '#9d174d' }
    return map[g]
  }

  return (
    <div className="dashboard-layout">
      <Sidebar />
      <div className="dashboard-main">
        <TopNav />
        <div className="dashboard-content">
          <div className="dashboard-header">
            <h1>AI Analytics</h1>
            <p>Live detection highlights and operational insights to prioritize response and resource planning.</p>
          </div>

          {toast && <div className="toast">{toast}</div>}

          <div className="kpi-strip card">
            {kpi.map((k, i) => (
              <div key={i} className="kpi" style={{ background: gradBg(k.grad) }}>
                <span className="kpi-icon">{k.icon}</span>
                <div>
                  <h4 style={{ color: gradText(k.grad) }}>{k.value}</h4>
                  <p>{k.label}</p>
                  <small>{k.sub}</small>
                </div>
              </div>
            ))}
          </div>

          <div className="ai-row row-pattern">
            <div className="card ai-card pattern-card">
              <div className="ai-card-head">
                <h3>🔍 Pattern Detection</h3>
                <span className="ai-card-pill">{patternDetections.length} active</span>
              </div>
              <div className="pattern-list">
                {patternDetections.map(p => (
                  <div key={p.id} className="pattern-row">
                    <div className="pr-head">
                      <div className="pr-head-left">
                        <span className={'risk-badge ' + p.risk.toLowerCase()}>{p.risk} Risk</span>
                        <strong>{p.id} · {p.title}</strong>
                      </div>
                      <div className="pr-stats">
                        <div><small>Frequency</small><strong>{p.freq}</strong></div>
                        <div><small>Accuracy</small><strong>{p.hit}</strong></div>
                      </div>
                    </div>
                    <p className="pr-desc">{p.desc}</p>
                    <div className="pr-rec">
                      <span className="pr-rec-tag">💡 Recommendation</span>
                      <span className="pr-rec-text">{p.rec}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          <div className="ai-row row-suspicious">
            <div className="card ai-card suspicious-card">
              <div className="ai-card-head">
                <h3>🚨 Suspicious Movement Alerts</h3>
                <span className="ai-card-pill danger">{suspiciousMovements.filter(s => s.severity === 'High').length} high severity</span>
              </div>
              <div className="suspicious-list">
                {suspiciousMovements.map(s => (
                  <div key={s.id} className={'suspicious-row sev-' + s.severity.toLowerCase()}>
                    <div className="sr-left">
                      <div className="sr-score" style={{ background: s.severity === 'High' ? 'linear-gradient(145deg,#ef4444,#b91c1c)' : s.severity === 'Medium' ? 'linear-gradient(145deg,#f59e0b,#b45309)' : 'linear-gradient(145deg,#10b981,#047857)' }}>
                        <strong>{s.score}</strong><small>score</small>
                      </div>
                    </div>
                    <div className="sr-right">
                      <div className="sr-head">
                        <span className={'sev-badge ' + s.severity.toLowerCase()}>{s.severity}</span>
                        <strong className="sr-entity">{s.entity}</strong>
                      </div>
                      <div className="sr-path">🛤️ {s.path}</div>
                      <div className="sr-meta">
                        <span>🕒 First seen: {s.firstSeen}</span>
                        <span>🤖 Model: {s.flaggedBy}</span>
                      </div>
                      <div className="sr-actions">
                        <button className="btn btn-small btn-primary" onClick={() => showToast('🚔 Unit dispatched for ' + s.entity)}>🚔 Dispatch</button>
                        <button className="btn btn-small btn-outline" onClick={() => showToast('✅ Marked benign: ' + s.entity)}>✓ Mark Benign</button>
                        <button className="btn btn-small btn-danger" onClick={() => showToast('🚨 Escalated to senior officer: ' + s.entity)}>⛔ Escalate</button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

        </div>
      </div>
    </div>
  )
}

export default AIAnalytics
