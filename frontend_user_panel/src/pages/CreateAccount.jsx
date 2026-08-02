import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import './CreateAccount.css'
import { useUser } from '../UserContext.jsx'

function CreateAccount() {
  const { setUser } = useUser()
  const [formData, setFormData] = useState({
    fullName: '',
    email: '',
    mobileNumber: '',
    password: '',
    confirmPassword: '',
    dob: '',
    gender: '',
    nationality: '',
    preferredLanguage: '',
    emergencyContactName: '',
    emergencyContactPhone: '',
    emergencyContactEmail: '',
    enable2FA: false,
    securityQuestion: '',
    securityAnswer: '',
    bloodGroup: '',
    allergies: '',
    existingMedications: '',
    organDonor: '',
    locationAccess: false,
    cameraAccess: false,
    microphoneAccess: false,
    notifications: false,
    contactsAccess: false,
    kycDocumentType: '',
    kycDocumentNumber: '',
    kycIdProofNumber: ''
  })
  const [isCreated, setIsCreated] = useState(false)
  const [blockchainId, setBlockchainId] = useState('')
  const navigate = useNavigate()

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }))
  }

  const handleSubmit = (e) => {
    e.preventDefault()
    const generatedId = 'BLCK-' + Date.now().toString(36).toUpperCase()
    setBlockchainId(generatedId)
    setUser({
      name: formData.fullName,
      email: formData.email,
      phone: formData.mobileNumber,
      blockchainId: generatedId,
      password: formData.password, // Save password for login (demo only!)
      dob: formData.dob,
      gender: formData.gender,
      nationality: formData.nationality,
      preferredLanguage: formData.preferredLanguage,
      emergencyContactName: formData.emergencyContactName,
      emergencyContactPhone: formData.emergencyContactPhone,
      emergencyContactEmail: formData.emergencyContactEmail,
      enable2FA: formData.enable2FA,
      securityQuestion: formData.securityQuestion,
      securityAnswer: formData.securityAnswer,
      bloodGroup: formData.bloodGroup,
      allergies: formData.allergies,
      existingMedications: formData.existingMedications,
      organDonor: formData.organDonor,
      locationAccess: formData.locationAccess,
      cameraAccess: formData.cameraAccess,
      microphoneAccess: formData.microphoneAccess,
      notifications: formData.notifications,
      contactsAccess: formData.contactsAccess,
      kycDocumentType: formData.kycDocumentType,
      kycDocumentNumber: formData.kycDocumentNumber,
      kycIdProofNumber: formData.kycIdProofNumber
    })
    setIsCreated(true)
  }

  const handleContinue = () => {
    navigate('/dashboard')
  }

  return (
    <div className="create-account-page">
      <nav className="navbar">
        <div className="container">
          <div className="nav-content">
            <Link to="/" className="logo">🛡️ SafeTour</Link>
          </div>
        </div>
      </nav>

      <div className="create-account-container">
        <div className="card create-account-card">
          {!isCreated ? (
            <>
              <h1>Account Creation</h1>
              <form onSubmit={handleSubmit} className="create-account-form">
                <div className="form-section">
                  <h3>Basic Account Details (Required)</h3>
                  <div className="form-grid">
                    <div className="form-group">
                      <label>Full Name</label>
                      <input type="text" name="fullName" value={formData.fullName} onChange={handleChange} required />
                    </div>
                    <div className="form-group">
                      <label>Email Address</label>
                      <input type="email" name="email" value={formData.email} onChange={handleChange} required />
                    </div>
                    <div className="form-group">
                      <label>Mobile Number (with country code)</label>
                      <input type="tel" name="mobileNumber" value={formData.mobileNumber} onChange={handleChange} required placeholder="+91 XXXXX XXXXX" />
                    </div>
                    <div className="form-group">
                      <label>Password</label>
                      <input type="password" name="password" value={formData.password} onChange={handleChange} required />
                    </div>
                    <div className="form-group">
                      <label>Confirm Password</label>
                      <input type="password" name="confirmPassword" value={formData.confirmPassword} onChange={handleChange} required />
                    </div>
                  </div>
                </div>

                <div className="form-section">
                  <h3>Personal Information</h3>
                  <div className="form-grid">
                    <div className="form-group">
                      <label>Date of Birth (Optional if age restrictions apply)</label>
                      <input type="date" name="dob" value={formData.dob} onChange={handleChange} />
                    </div>
                    <div className="form-group">
                      <label>Gender (Optional: Prefer not to say)</label>
                      <select name="gender" value={formData.gender} onChange={handleChange}>
                        <option value="">Select</option>
                        <option value="male">Male</option>
                        <option value="female">Female</option>
                        <option value="other">Other</option>
                        <option value="prefer-not">Prefer not to say</option>
                      </select>
                    </div>
                    <div className="form-group">
                      <label>Nationality</label>
                      <input type="text" name="nationality" value={formData.nationality} onChange={handleChange} />
                    </div>
                    <div className="form-group">
                      <label>Preferred Language</label>
                      <select name="preferredLanguage" value={formData.preferredLanguage} onChange={handleChange}>
                        <option value="">Select Language</option>
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

                <div className="form-section">
                  <h3>Emergency Contact (Very Important)</h3>
                  <div className="form-grid">
                    <div className="form-group">
                      <label>Emergency Contact Name</label>
                      <input type="text" name="emergencyContactName" value={formData.emergencyContactName} onChange={handleChange} required />
                    </div>
                    <div className="form-group">
                      <label>Emergency Contact Phone Number</label>
                      <input type="tel" name="emergencyContactPhone" value={formData.emergencyContactPhone} onChange={handleChange} required />
                    </div>
                    <div className="form-group">
                      <label>Emergency Contact Email (optional)</label>
                      <input type="email" name="emergencyContactEmail" value={formData.emergencyContactEmail} onChange={handleChange} />
                    </div>
                    <div className="form-group">
                      <label>Multiple Emergency Contacts (recommended)</label>
                      <input type="text" placeholder="Add additional contacts" />
                    </div>
                  </div>
                </div>

                <div className="form-section">
                  <h3>Security Features</h3>
                  <div className="form-grid">
                    <div className="form-group checkbox-group">
                      <input type="checkbox" id="enable2FA" name="enable2FA" checked={formData.enable2FA} onChange={handleChange} />
                      <label for="enable2FA">Enable Two-Factor Authentication (OTP)</label>
                    </div>
                    <div className="form-group">
                      <label>Security Question (optional)</label>
                      <select name="securityQuestion" value={formData.securityQuestion} onChange={handleChange}>
                        <option value="">Select Question</option>
                        <option value="pet">What was your first pet's name?</option>
                        <option value="school">What was your first school?</option>
                      </select>
                    </div>
                    <div className="form-group">
                      <label>Security Answer</label>
                      <input type="text" name="securityAnswer" value={formData.securityAnswer} onChange={handleChange} />
                    </div>
                    <div className="form-group checkbox-group">
                      <input type="checkbox" disabled checked />
                      <label>Biometric Login (after account creation)</label>
                    </div>
                  </div>
                </div>

                <div className="form-section">
                  <h3>Medical Information (Recommended)</h3>
                  <div className="form-grid">
                    <div className="form-group">
                      <label>Blood Group</label>
                      <select name="bloodGroup" value={formData.bloodGroup} onChange={handleChange}>
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
                    <div className="form-group">
                      <label>Allergies</label>
                      <input type="text" name="allergies" value={formData.allergies} onChange={handleChange} />
                    </div>
                    <div className="form-group">
                      <label>Existing Medical Conditions</label>
                      <input type="text" name="existingMedications" value={formData.existingMedications} onChange={handleChange} />
                    </div>
                    <div className="form-group">
                      <label>Organ Donor (optional)</label>
                      <select name="organDonor" value={formData.organDonor} onChange={handleChange}>
                        <option value="">Select</option>
                        <option value="yes">Yes</option>
                        <option value="no">No</option>
                      </select>
                    </div>
                  </div>
                </div>

                <div className="form-section">
                  <h3>Permissions</h3>
                  <p className="permissions-note">Ask for permission with clear explanations</p>
                  <div className="form-grid">
                    <div className="form-group checkbox-group">
                      <input type="checkbox" id="locationAccess" name="locationAccess" checked={formData.locationAccess} onChange={handleChange} />
                      <label for="locationAccess">Location Access</label>
                    </div>
                    <div className="form-group checkbox-group">
                      <input type="checkbox" id="cameraAccess" name="cameraAccess" checked={formData.cameraAccess} onChange={handleChange} />
                      <label for="cameraAccess">Camera Access</label>
                    </div>
                    <div className="form-group checkbox-group">
                      <input type="checkbox" id="microphoneAccess" name="microphoneAccess" checked={formData.microphoneAccess} onChange={handleChange} />
                      <label for="microphoneAccess">Microphone Access</label>
                    </div>
                    <div className="form-group checkbox-group">
                      <input type="checkbox" id="notifications" name="notifications" checked={formData.notifications} onChange={handleChange} />
                      <label for="notifications">Notifications</label>
                    </div>
                    <div className="form-group checkbox-group">
                      <input type="checkbox" id="contactsAccess" name="contactsAccess" checked={formData.contactsAccess} onChange={handleChange} />
                      <label for="contactsAccess">Contacts (only for SOS feature)</label>
                    </div>
                  </div>
                </div>

                <div className="form-section">
                  <h3>Profile Picture (Optional)</h3>
                  <div className="form-group">
                    <button type="button" className="btn btn-outline">[Upload Image]</button> or <button type="button" className="btn btn-outline">[Skip for Later]</button>
                  </div>
                </div>

                <div className="form-section">
                  <h3>KYC (User must upload at least one - Required)</h3>
                  <div className="form-grid">
                    <div className="form-group">
                      <label>Document Type</label>
                      <select name="kycDocumentType" value={formData.kycDocumentType} onChange={handleChange} required>
                        <option value="">Select Document</option>
                        <option value="aadhaar">Aadhaar Card (for Indian users)</option>
                        <option value="passport">Passport (for international tourists)</option>
                        <option value="driving">Driving License (optional backup)</option>
                      </select>
                    </div>
                    <div className="form-group">
                      <label>Document Number</label>
                      <input type="text" name="kycDocumentNumber" value={formData.kycDocumentNumber} onChange={handleChange} required />
                    </div>
                    <div className="form-group">
                      <label>And enter id proof number and its id number</label>
                      <input type="text" name="kycIdProofNumber" value={formData.kycIdProofNumber} onChange={handleChange} required />
                    </div>
                  </div>
                </div>

                <button type="submit" className="btn btn-primary btn-block">Create Account</button>
              </form>
            </>
          ) : (
            <div className="success-message">
              <div className="success-icon">✅</div>
              <h2>You have successfully logged in</h2>
              <p>You KYC/Blockchain ID has been created</p>
              <div className="blockchain-id">
                <span className="id-label">Blockchain ID:</span>
                <span className="id-value">{blockchainId}</span>
              </div>
              <button onClick={handleContinue} className="btn btn-success btn-block mt-4">Continue to Dashboard</button>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default CreateAccount
