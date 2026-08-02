import { NavLink } from 'react-router-dom'
import './Sidebar.css'

function Sidebar() {
  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <div className="sidebar-logo">
          <span className="logo-icon">🛡️</span> SafeTour <span className="admin-badge">ADMIN</span>
        </div>
        <p className="sidebar-subtitle">Officer Control Panel</p>
      </div>
      <nav className="sidebar-nav">
        <NavLink to="/dashboard" className={({ isActive }) => 'sidebar-link' + (isActive ? ' active' : '')}>
          <span className="nav-icon">📊</span> Dashboard
        </NavLink>
        <NavLink to="/risk-heatmap" className={({ isActive }) => 'sidebar-link' + (isActive ? ' active' : '')}>
          <span className="nav-icon">🗺️</span> Risk Heatmap
        </NavLink>
        <NavLink to="/sos-monitoring" className={({ isActive }) => 'sidebar-link' + (isActive ? ' active' : '')}>
          <span className="nav-icon">🚨</span> SOS Monitoring
        </NavLink>
        <NavLink to="/efir-monitoring" className={({ isActive }) => 'sidebar-link' + (isActive ? ' active' : '')}>
          <span className="nav-icon">📋</span> E-FIR Monitoring
        </NavLink>
        <NavLink to="/zone-management" className={({ isActive }) => 'sidebar-link' + (isActive ? ' active' : '')}>
          <span className="nav-icon">🚧</span> Zone Management
        </NavLink>
        <NavLink to="/ai-analytics" className={({ isActive }) => 'sidebar-link' + (isActive ? ' active' : '')}>
          <span className="nav-icon">🤖</span> AI Analytics
        </NavLink>
      </nav>
      <div className="sidebar-footer">
        <div className="version-tag">v 1.0.0 • Admin</div>
      </div>
    </aside>
  )
}

export default Sidebar
