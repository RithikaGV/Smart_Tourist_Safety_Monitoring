import { Link } from 'react-router-dom'
import './Home.css'

function Home() {
  return (
    <div className="home">
      <nav className="navbar">
        <div className="container">
          <div className="nav-content">
            <div className="logo">🛡️ SafeTour</div>
            <div className="nav-links">
              <Link to="/">Home</Link>
              <Link to="/login">Login</Link>
            </div>
          </div>
        </div>
      </nav>

      <div className="hero-section">
        <div className="container">
          <div className="hero-content">
            <h1 className="hero-title">Smart Tourist Safety & Security</h1>
            <p className="hero-subtitle">
              Your safety companion, powered by AI, GeoFencing, and Blockchain.
            </p>
            <div className="hero-buttons">
              <Link to="/login" className="btn btn-primary">Get Started</Link>
            </div>
          </div>
        </div>
      </div>

      <div className="features-section">
        <div className="container">
          <h2 className="section-title">Key Features</h2>
          <div className="features-grid">
            <div className="feature-card card">
              <div className="feature-icon">🔐</div>
              <h3>Secure KYC Onboarding</h3>
              <p>Blockchain-based digital ID verification for secure access.</p>
            </div>
            <div className="feature-card card">
              <div className="feature-icon">📍</div>
              <h3>Edge Intelligence Geofencing</h3>
              <p>Real-time danger zone alerts even without internet.</p>
            </div>
            <div className="feature-card card">
              <div className="feature-icon">🚨</div>
              <h3>One-Touch SOS</h3>
              <p>Emergency alerts with mesh network support for no-network areas.</p>
            </div>
            <div className="feature-card card">
              <div className="feature-icon">👻</div>
              <h3>Ghost Mode</h3>
              <p>Privacy-first tracking with encrypted location history.</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Home
