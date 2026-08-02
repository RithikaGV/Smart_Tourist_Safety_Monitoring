import Sidebar from '../components/Sidebar'
import TopNav from '../components/TopNav'
import './Settings.css'

function Settings() {
  return (
    <div className="dashboard-layout">
      <Sidebar />
      <div className="dashboard-main">
        <TopNav />
        <div className="dashboard-content">
          <h1>Settings</h1>
          
          <div className="settings-card card">
            <h2>Change Password </h2>
            <div className="settings-form">
              <div className="form-group">
                <label>Registered Email</label>
                <input type="email" placeholder="Enter registered email" />
              </div>
              <button className="btn btn-primary">Send OTP</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Settings
