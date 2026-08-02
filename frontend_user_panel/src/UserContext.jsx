import React, { createContext, useState, useContext, useEffect } from 'react'

const UserContext = createContext()

const defaultUser = {
  name: 'John Doe',
  email: 'john.doe@email.com',
  phone: '+91 98765 43210',
  blockchainId: 'BLCK-XYZ123ABC456',
  dob: '',
  gender: '',
  nationality: 'Indian',
  preferredLanguage: 'en',
  emergencyContactName: 'Jane Doe',
  emergencyContactPhone: '+91 98765 43211',
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
  kycIdProofNumber: '',
  password: '' // Store password temporarily for login (not secure for real app, but for demo purposes)
}

export const UserProvider = ({ children }) => {
  // Initialize user from localStorage
  const [user, setUser] = useState(() => {
    const savedUser = localStorage.getItem('safeTourUser')
    const savedUsers = localStorage.getItem('safeTourUsers') // Store multiple users for login
    if (savedUsers && !savedUser) {
      // If there are saved users but no current user, use default
      return defaultUser
    }
    return savedUser ? JSON.parse(savedUser) : defaultUser
  })

  // Save user to localStorage whenever it changes
  useEffect(() => {
    localStorage.setItem('safeTourUser', JSON.stringify(user))
  }, [user])

  // Also, when setting user, make sure to update the users list if needed
  const updateUser = (newUser) => {
    setUser(newUser)
    // Update the users list in localStorage to save this user's data
    const savedUsers = JSON.parse(localStorage.getItem('safeTourUsers') || '{}')
    savedUsers[newUser.email] = newUser
    localStorage.setItem('safeTourUsers', JSON.stringify(savedUsers))
  }

  return (
    <UserContext.Provider value={{ user, setUser: updateUser }}>
      {children}
    </UserContext.Provider>
  )
}

export const useUser = () => useContext(UserContext);
