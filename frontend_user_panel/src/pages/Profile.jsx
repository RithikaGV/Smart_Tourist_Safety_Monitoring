import { useState, useEffect } from 'react'
import Sidebar from '../components/Sidebar'
import TopNav from '../components/TopNav'
import './Profile.css'
import { useUser } from '../UserContext.jsx'

function Profile() {
  const [isEditing, setIsEditing] = useState(false)
  const { user, setUser } = useUser()
  const [editForm, setEditForm] = useState({ ...user })

  useEffect(() => {
    setEditForm({ ...user })
  }, [user])

  const handleSave = () => {
    setUser({ ...editForm })
    setIsEditing(false)
  }

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target
    setEditForm(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }))
  }

  return (
    <div className="dashboard-layout">
      <Sidebar />
      <div className="dashboard-main">
        <TopNav />
        <div className="dashboard-content">
          <div className="profile-header">
            <h1>Profile</h1>
            <button 
              className="btn btn-primary"
              onClick={() => {
                if (isEditing) {
                  handleSave()
                } else {
                  setIsEditing(true)
                }
              }}
            >
              {isEditing ? 'Save' : 'Edit'}
            </button>
          </div>
          
          <div className="profile-card card">
            <div className="profile-avatar-large">👤</div>
            <div className="profile-info-section">
              <h2 className="section-title">Account Information</h2>
              <div className="info-grid">
                <div className="info-item">
                  <label>Full Name</label>
                  <input 
                    type="text" 
                    name="name"
                    value={editForm.name} 
                    disabled={!isEditing} 
                    onChange={handleChange}
                  />
                </div>
                <div className="info-item">
                  <label>Email Address</label>
                  <input 
                    type="email" 
                    name="email"
                    value={editForm.email} 
                    disabled={!isEditing} 
                    onChange={handleChange}
                  />
                </div>
                <div className="info-item">
                  <label>Mobile Number</label>
                  <input 
                    type="tel" 
                    name="phone"
                    value={editForm.phone} 
                    disabled={!isEditing} 
                    onChange={handleChange}
                  />
                </div>
              </div>
            </div>

            <div className="profile-info-section">
              <h2 className="section-title">Personal Information</h2>
              <div className="info-grid">
                <div className="info-item">
                  <label>Date of Birth</label>
                  <input 
                    type="date" 
                    name="dob"
                    value={editForm.dob} 
                    disabled={!isEditing} 
                    onChange={handleChange}
                  />
                </div>
                <div className="info-item">
                  <label>Gender</label>
                  <select 
                    name="gender"
                    value={editForm.gender} 
                    disabled={!isEditing} 
                    onChange={handleChange}
                  >
                    <option value="">Select</option>
                    <option value="male">Male</option>
                    <option value="female">Female</option>
                    <option value="other">Other</option>
                    <option value="prefer-not">Prefer not to say</option>
                  </select>
                </div>
                <div className="info-item">
                  <label>Nationality</label>
                  <input 
                    type="text" 
                    name="nationality"
                    value={editForm.nationality} 
                    disabled={!isEditing} 
                    onChange={handleChange}
                  />
                </div>
                <div className="info-item">
                  <label>Preferred Language</label>
                  <select 
                    name="preferredLanguage"
                    value={editForm.preferredLanguage} 
                    disabled={!isEditing} 
                    onChange={handleChange}
                  >
                    <option value="en">English</option>
                    <option value="hi">हिंदी (Hindi)</option>
                    <option value="ta">தமிழ் (Tamil)</option>
                    <option value="ml">മലയാളം (Malayalam)</option>
                    <option value="kn">ಕನ್ನಡ (Kannada)</option>
                    <option value="te">తెలుగు (Telugu)</option>
                    <option value="es">Español (Spanish)</option>
                    <option value="fr">Français (French)</option>
                  </select>
                </div>
              </div>
            </div>

            <div className="profile-info-section">
              <h2 className="section-title">KYC / Blockchain ID</h2>
              <div className="kyc-display">
                <div className="kyc-item">
                  <span className="kyc-label">Blockchain ID:</span>
                  <span className="kyc-value">{user.blockchainId}</span>
                </div>
                <div className="kyc-item">
                  <span className="kyc-label">KYC Status:</span>
                  <span className="kyc-status verified">Verified</span>
                </div>
                <div className="info-grid" style={{ marginTop: '16px' }}>
                  <div className="info-item">
                    <label>Document Type</label>
                    <select 
                      name="kycDocumentType"
                      value={editForm.kycDocumentType} 
                      disabled={!isEditing} 
                      onChange={handleChange}
                    >
                      <option value="">Select</option>
                      <option value="aadhaar">Aadhaar Card</option>
                      <option value="passport">Passport</option>
                      <option value="driving">Driving License</option>
                    </select>
                  </div>
                  <div className="info-item">
                    <label>Document Number</label>
                    <input 
                      type="text" 
                      name="kycDocumentNumber"
                      value={editForm.kycDocumentNumber} 
                      disabled={!isEditing} 
                      onChange={handleChange}
                    />
                  </div>
                  <div className="info-item">
                    <label>ID Proof Number</label>
                    <input 
                      type="text" 
                      name="kycIdProofNumber"
                      value={editForm.kycIdProofNumber} 
                      disabled={!isEditing} 
                      onChange={handleChange}
                    />
                  </div>
                </div>
              </div>
            </div>

            <div className="profile-info-section">
              <h2 className="section-title">Emergency Contact</h2>
              <div className="info-grid">
                <div className="info-item">
                  <label>Emergency Contact Name</label>
                  <input 
                    type="text" 
                    name="emergencyContactName"
                    value={editForm.emergencyContactName} 
                    disabled={!isEditing} 
                    onChange={handleChange}
                  />
                </div>
                <div className="info-item">
                  <label>Emergency Contact Number</label>
                  <input 
                    type="tel" 
                    name="emergencyContactPhone"
                    value={editForm.emergencyContactPhone} 
                    disabled={!isEditing} 
                    onChange={handleChange}
                  />
                </div>
                <div className="info-item">
                  <label>Emergency Contact Email (optional)</label>
                  <input 
                    type="email" 
                    name="emergencyContactEmail"
                    value={editForm.emergencyContactEmail} 
                    disabled={!isEditing} 
                    onChange={handleChange}
                  />
                </div>
              </div>
            </div>

            <div className="profile-info-section">
              <h2 className="section-title">Medical Information</h2>
              <div className="info-grid">
                <div className="info-item">
                  <label>Blood Group</label>
                  <select 
                    name="bloodGroup"
                    value={editForm.bloodGroup} 
                    disabled={!isEditing} 
                    onChange={handleChange}
                  >
                    <option value="">Select</option>
                    <option value="A+">A+</option>
                    <option value="A-">A-</option>
                    <option value="B+">B+</option>
                    <option value="B-">B-</option>
                    <option value="AB+">AB+</option>
                    <option value="AB-">AB-</option>
                    <option value="O+">O+</option>
                    <option value="O-">O-</option>
                  </select>
                </div>
                <div className="info-item">
                  <label>Allergies</label>
                  <input 
                    type="text" 
                    name="allergies"
                    value={editForm.allergies} 
                    disabled={!isEditing} 
                    onChange={handleChange}
                  />
                </div>
                <div className="info-item">
                  <label>Existing Medical Conditions</label>
                  <input 
                    type="text" 
                    name="existingMedications"
                    value={editForm.existingMedications} 
                    disabled={!isEditing} 
                    onChange={handleChange}
                  />
                </div>
                <div className="info-item">
                  <label>Organ Donor</label>
                  <select 
                    name="organDonor"
                    value={editForm.organDonor} 
                    disabled={!isEditing} 
                    onChange={handleChange}
                  >
                    <option value="">Select</option>
                    <option value="yes">Yes</option>
                    <option value="no">No</option>
                  </select>
                </div>
              </div>
            </div>

            <div className="profile-info-section">
              <h2 className="section-title">Security Features</h2>
              <div className="info-grid">
                <div className="info-item checkbox-item">
                  <input 
                    type="checkbox" 
                    id="enable2FA"
                    name="enable2FA"
                    checked={editForm.enable2FA} 
                    disabled={!isEditing} 
                    onChange={handleChange}
                  />
                  <label for="enable2FA">Enable Two-Factor Authentication (OTP)</label>
                </div>
                <div className="info-item">
                  <label>Security Question</label>
                  <select 
                    name="securityQuestion"
                    value={editForm.securityQuestion} 
                    disabled={!isEditing} 
                    onChange={handleChange}
                  >
                    <option value="">Select</option>
                    <option value="pet">What was your first pet's name?</option>
                    <option value="school">What was your first school?</option>
                  </select>
                </div>
                <div className="info-item">
                  <label>Security Answer</label>
                  <input 
                    type="text" 
                    name="securityAnswer"
                    value={editForm.securityAnswer} 
                    disabled={!isEditing} 
                    onChange={handleChange}
                  />
                </div>
              </div>
            </div>

            <div className="profile-info-section">
              <h2 className="section-title">Permissions</h2>
              <div className="info-grid">
                <div className="info-item checkbox-item">
                  <input 
                    type="checkbox" 
                    id="locationAccess"
                    name="locationAccess"
                    checked={editForm.locationAccess} 
                    disabled={!isEditing} 
                    onChange={handleChange}
                  />
                  <label for="locationAccess">Location Access</label>
                </div>
                <div className="info-item checkbox-item">
                  <input 
                    type="checkbox" 
                    id="cameraAccess"
                    name="cameraAccess"
                    checked={editForm.cameraAccess} 
                    disabled={!isEditing} 
                    onChange={handleChange}
                  />
                  <label for="cameraAccess">Camera Access</label>
                </div>
                <div className="info-item checkbox-item">
                  <input 
                    type="checkbox" 
                    id="microphoneAccess"
                    name="microphoneAccess"
                    checked={editForm.microphoneAccess} 
                    disabled={!isEditing} 
                    onChange={handleChange}
                  />
                  <label for="microphoneAccess">Microphone Access</label>
                </div>
                <div className="info-item checkbox-item">
                  <input 
                    type="checkbox" 
                    id="notifications"
                    name="notifications"
                    checked={editForm.notifications} 
                    disabled={!isEditing} 
                    onChange={handleChange}
                  />
                  <label for="notifications">Notifications</label>
                </div>
                <div className="info-item checkbox-item">
                  <input 
                    type="checkbox" 
                    id="contactsAccess"
                    name="contactsAccess"
                    checked={editForm.contactsAccess} 
                    disabled={!isEditing} 
                    onChange={handleChange}
                  />
                  <label for="contactsAccess">Contacts (SOS Feature)</label>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Profile
