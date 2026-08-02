import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAdmin } from '../AdminContext.jsx'
import './Login.css'

function Login() {
  const [loginId, setLoginId] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const { loginOfficer, officer, loginMessage, setLoginMessage } = useAdmin()
  const navigate = useNavigate()

  useEffect(() => {
    if (officer) {
      setSuccess('Successfully logged in! Redirecting to dashboard...')
      const t = setTimeout(() => navigate('/dashboard'), 1200)
      return () => clearTimeout(t)
    }
  }, [officer, navigate])

  const handleSubmit = (e) => {
    e.preventDefault()
    setError('')
    setSuccess('')
    setLoginMessage(null)
    if (!loginId.trim() || !password.trim()) {
      setError('Please enter both Login ID and Password')
      return
    }
    const ok = loginOfficer(loginId.trim(), password.trim())
    if (!ok) setError(loginMessage || 'Invalid login credentials')
  }

  return (
    <div className="login-page">
      <div className="login-wrapper">
        <div className="brand-section">
          <div className="brand-logo-row">
            <div className="brand-big-icon">🛡️</div>
            <div>
              <div className="brand-title">SafeTour</div>
              <div className="brand-pill">ADMIN PANEL</div>
            </div>
          </div>

          <div className="brand-hero">
            <h1>Tourist Safety Operations</h1>
            <p className="brand-sub">
              Monitor SOS alerts, review e-FIRs, manage geo-fenced zones, and act on AI insights in one place.
            </p>

            <div className="brand-features">
              <div className="bf-item"><span className="bf-icon">🚨</span> SOS Monitoring</div>
              <div className="bf-item"><span className="bf-icon">🧾</span> e-FIR Workflow</div>
              <div className="bf-item"><span className="bf-icon">🗺️</span> Zone Management</div>
              <div className="bf-item"><span className="bf-icon">🧠</span> AI Analytics</div>
            </div>
          </div>

          <div className="brand-foot">
            Authorized access only · Activity is logged for audit
          </div>
        </div>

        <div className="form-section">
          <div className="form-head">
            <h2>Officer Sign In</h2>
            <p>Use your department-provided credentials.</p>
          </div>

          <form className="login-form" onSubmit={handleSubmit}>
            <div className="form-group">
              <label>Login ID</label>
              <input
                type="text"
                placeholder="e.g. officer001"
                value={loginId}
                onChange={(e) => setLoginId(e.target.value)}
                autoComplete="username"
              />
            </div>
            <div className="form-group">
              <label>Password</label>
              <input
                type="password"
                placeholder="Enter password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                autoComplete="current-password"
              />
            </div>

            {error && <div className="alert alert-error">⚠️ {error}</div>}
            {success && <div className="alert alert-success">✅ {success}</div>}

            <button type="submit" className="btn btn-primary btn-block">Sign In</button>
          </form>

          <div className="demo-creds">
            <h4>Demo Officer Credentials</h4>
            <div className="demo-list">
              <div className="demo-row" onClick={() => { setLoginId('officer001'); setPassword('admin123') }}>
                <span className="dr-user">officer001</span>
                <span className="dr-pw">admin123</span>
              </div>
              <div className="demo-row" onClick={() => { setLoginId('officer002'); setPassword('admin123') }}>
                <span className="dr-user">officer002</span>
                <span className="dr-pw">admin123</span>
              </div>
              <div className="demo-row" onClick={() => { setLoginId('officer003'); setPassword('admin123') }}>
                <span className="dr-user">officer003</span>
                <span className="dr-pw">admin123</span>
              </div>
            </div>
            <div className="demo-note">Tip: click a row to auto-fill.</div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Login
