import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAdmin } from '../AdminContext.jsx'
import './TopNav.css'

function TopNav() {
  const { officer, logoutOfficer } = useAdmin()
  const [showProfile, setShowProfile] = useState(false)
  const navigate = useNavigate()

  const handleLogout = () => {
    logoutOfficer()
    setShowProfile(false)
    navigate('/login')
  }

  return (
    <nav className="top-nav">
      <div className="top-nav-content">
        <div className="top-nav-left">
          <div className="live-badge">
            <span className="live-dot"></span> LIVE MONITORING
          </div>
        </div>
        <div className="top-nav-right">
          <div className="profile-wrapper">
            <button
              type="button"
              className="profile-link"
              onClick={() => setShowProfile(!showProfile)}
            >
              <span className="profile-avatar">{officer?.badge || '👮'}</span>
              <div className="profile-text">
                <div className="profile-name">{officer?.name || 'Officer'}</div>
                <div className="profile-role">{officer?.department || 'Admin'}</div>
              </div>
              <span className={'profile-caret' + (showProfile ? ' open' : '')}>▾</span>
            </button>
            {showProfile && (
              <div className="profile-dropdown card">
                <div className="dropdown-header">
                  <div className="dropdown-avatar">{officer?.badge || '👮'}</div>
                  <div>
                    <h3>{officer?.name}</h3>
                    <p className="dd-id">ID: {officer?.officerId}</p>
                    <p className="dd-dept">{officer?.department}</p>
                  </div>
                </div>
                <div className="dropdown-divider"></div>
                <button type="button" className="btn btn-primary btn-block" onClick={handleLogout}>
                  🔒 Logout
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
    </nav>
  )
}

export default TopNav
