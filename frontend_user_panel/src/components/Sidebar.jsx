import { Link, useLocation } from 'react-router-dom'
import './Sidebar.css'

function Sidebar() {
  const location = useLocation()

  return (
    <div className="sidebar">
      <div className="sidebar-header">
        <Link to="/dashboard" className="sidebar-logo">
          🛡️ SafeTour
        </Link>
      </div>
      <nav className="sidebar-nav">
        <Link 
          to="/dashboard" 
          className={`sidebar-link ${location.pathname === '/dashboard' ? 'active' : ''}`}
        >
          Dashboard
        </Link>
        <Link 
          to="/plan-trip" 
          className={`sidebar-link ${location.pathname === '/plan-trip' ? 'active' : ''}`}
        >
          Search & Plan Trip
        </Link>
        <Link 
          to="/my-trips" 
          className={`sidebar-link ${location.pathname === '/my-trips' ? 'active' : ''}`}
        >
          My Trips
        </Link>
        <Link 
          to="/settings" 
          className={`sidebar-link ${location.pathname === '/settings' ? 'active' : ''}`}
        >
          Settings
        </Link>
      </nav>
    </div>
  )
}

export default Sidebar
