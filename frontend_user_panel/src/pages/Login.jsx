import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import './Login.css'
import { useUser } from '../UserContext.jsx'

function Login() {
  const [formData, setFormData] = useState({
    email: '',
    password: '',
  })
  const [error, setError] = useState('')
  const { setUser } = useUser()
  const navigate = useNavigate()

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value })
  }

  const handleSubmit = (e) => {
    e.preventDefault()
    setError('')
    
    // Load saved users from localStorage
    const savedUsers = JSON.parse(localStorage.getItem('safeTourUsers') || '{}')
    
    if (savedUsers[formData.email]) {
      const user = savedUsers[formData.email]
      // Check password (for demo only!)
      if (user.password === formData.password) {
        // Set the current user in context
        setUser(user)
        navigate('/dashboard')
      } else {
        setError('Incorrect password!')
      }
    } else {
      setError('No account found with this email!')
    }
  }

  return (
    <div className="login-page">
      <nav className="navbar">
        <div className="container">
          <div className="nav-content">
            <Link to="/" className="logo">🛡️ SafeTour</Link>
          </div>
        </div>
      </nav>

      <div className="login-container">
        <div className="card login-card">
          <h2 className="login-title">Login</h2>
          {error && (
            <div style={{ 
              padding: '12px', background: '#fee2e2', color: '#991b1b', borderRadius: '8px', marginBottom: '16px' }}>
              {error}
            </div>
          )}
          <form onSubmit={handleSubmit} className="login-form">
            <div className="form-group">
              <label>Email</label>
              <input
                type="email"
                name="email"
                value={formData.email}
                onChange={handleChange}
                required
                placeholder="your@email.com"
              />
            </div>
            <div className="form-group">
              <label>Password</label>
              <input
                type="password"
                name="password"
                value={formData.password}
                onChange={handleChange}
                required
                placeholder="Enter your password"
              />
            </div>
            <button type="submit" className="btn btn-primary btn-block">
              Login
            </button>
          </form>
          <div className="create-account-link">
            <p>No account? <Link to="/create-account">Create One</Link></p>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Login
