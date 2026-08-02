import { Link } from 'react-router-dom'
import './TopNav.css'
import { useUser } from '../UserContext.jsx'

function TopNav() {
  const { user } = useUser()
  return (
    <header className="top-nav">
      <div className="top-nav-content">
        <div></div>
        <div className="top-nav-right">
          <Link to="/profile" className="profile-link">
            <div className="profile-avatar">👤</div>
            <div className="profile-info">
              <span className="profile-name">{user.name}</span>
            </div>
          </Link>
        </div>
      </div>
    </header>
  )
}

export default TopNav
