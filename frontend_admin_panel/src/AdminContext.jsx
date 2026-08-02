import React, { createContext, useState, useContext } from 'react'

const AdminContext = createContext()

const sampleOfficers = [
  {
    loginId: 'officer001',
    password: 'admin123',
    name: 'Inspector Arjun Menon',
    officerId: 'ST-OFF-001',
    department: 'Tourism Police Wing',
    badge: '👮'
  },
  {
    loginId: 'officer002',
    password: 'admin123',
    name: 'SI Priya Sharma',
    officerId: 'ST-OFF-002',
    department: 'District Emergency Control',
    badge: '👮‍♀️'
  },
  {
    loginId: 'officer003',
    password: 'admin123',
    name: 'DSP Ravi Kumar',
    officerId: 'ST-OFF-003',
    department: 'Intelligence & Risk Analysis',
    badge: '🎖️'
  }
]

const sampleSOSAlerts = [
  { id: 'SOS-2026-1001', touristName: 'Anita Desai', touristPhone: '+91 98765 43210', location: 'Ooty - Botanical Gardens', lat: 11.4064, lng: 76.6932, time: '2026-07-26 14:32:10', status: 'Pending', priority: 'High', notes: 'Feeling unsafe, surrounded by unknown people' },
  { id: 'SOS-2026-1002', touristName: 'Marcus Lee', touristPhone: '+65 8123 4567', location: 'Coonoor - Sim\'s Park', lat: 11.3450, lng: 76.7950, time: '2026-07-26 13:15:45', status: 'Investigating', priority: 'Medium', notes: 'Lost belongings, need help' },
  { id: 'SOS-2026-1003', touristName: 'Sarah Johnson', touristPhone: '+1 555 0199', location: 'Mysore Palace Entrance', lat: 12.3051, lng: 76.6551, time: '2026-07-26 11:08:22', status: 'Closed', priority: 'Low', notes: 'Minor dispute with vendor, resolved' },
  { id: 'SOS-2026-1004', touristName: 'Rajesh Nair', touristPhone: '+91 99000 11122', location: 'Bandipur Tiger Reserve', lat: 11.7500, lng: 76.6400, time: '2026-07-26 10:55:00', status: 'Pending', priority: 'High', notes: 'Vehicle breakdown in forest area' },
  { id: 'SOS-2026-1005', touristName: 'Emma Wilson', touristPhone: '+44 7700 900000', location: 'Brindavan Gardens', lat: 12.4200, lng: 76.6000, time: '2026-07-26 09:22:30', status: 'Investigating', priority: 'Medium', notes: 'Separated from travel group' }
]

const sampleEFIRReports = [
  { id: 'EFIR-2026-2001', touristName: 'Vikram Patel', touristPhone: '+91 98111 22233', incidentType: 'Theft of Wallet', location: 'Mysore City Market', lat: 12.3100, lng: 76.6600, time: '2026-07-26 15:10:00', status: 'Pending', firCopyRef: 'FIR-KR-2026-00451', description: 'Wallet with INR 8500 and cards stolen from bag' },
  { id: 'EFIR-2026-2002', touristName: 'Liu Fang', touristPhone: '+86 138 0000 1111', incidentType: 'Harassment', location: 'Ooty Lake Area', lat: 11.4100, lng: 76.6950, time: '2026-07-26 14:00:20', status: 'Investigating', firCopyRef: 'FIR-NG-2026-00187', description: 'Verbal harassment by local group' },
  { id: 'EFIR-2026-2003', touristName: 'Arjun Reddy', touristPhone: '+91 99887 76655', incidentType: 'Road Accident', location: 'Mysore-Ooty Highway', lat: 11.8500, lng: 76.6700, time: '2026-07-26 08:30:40', status: 'Closed', firCopyRef: 'FIR-HG-2026-00092', description: 'Two-wheeler collision, minor injuries' },
  { id: 'EFIR-2026-2004', touristName: 'Nina Petrova', touristPhone: '+7 903 123 4567', incidentType: 'Fraud / Scam', location: 'Chamundi Hills', lat: 12.2700, lng: 76.6700, time: '2026-07-25 18:45:00', status: 'Pending', firCopyRef: 'FIR-MR-2026-00773', description: 'Fake guide overcharging for tour' }
]

const sampleZones = [
  { id: 'Z-01', name: 'Western Catchment Forest', type: 'Landslide area', lat: 11.4500, lng: 76.6000, radius: 800, status: 'Active', color: 'red' },
  { id: 'Z-02', name: 'Avalanche Lake Restricted', type: 'Restricted zone', lat: 11.4700, lng: 76.5800, radius: 600, status: 'Active', color: 'red' },
  { id: 'Z-03', name: 'Doddabetta Slopes', type: 'Landslide area', lat: 11.4000, lng: 76.7350, radius: 500, status: 'Active', color: 'yellow' },
  { id: 'Z-04', name: 'Bandipur Core Buffer', type: 'Restricted zone', lat: 11.7200, lng: 76.6000, radius: 1200, status: 'Draft', color: 'yellow' }
]

const sampleIncidentStats = [
  { category: 'Theft', count: 18, trend: '+3' },
  { category: 'Harassment', count: 7, trend: '-2' },
  { category: 'Accident', count: 12, trend: '+1' },
  { category: 'Missing', count: 3, trend: '-1' },
  { category: 'Fraud', count: 9, trend: '+4' },
  { category: 'Medical', count: 5, trend: '0' }
]

export const AdminProvider = ({ children }) => {
  const [officer, setOfficer] = useState(() => {
    const saved = localStorage.getItem('safeTourOfficer')
    return saved ? JSON.parse(saved) : null
  })
  const [loginMessage, setLoginMessage] = useState(null)
  const [sosAlerts, setSosAlerts] = useState(() => {
    const saved = localStorage.getItem('safeTourSOS')
    return saved ? JSON.parse(saved) : sampleSOSAlerts
  })
  const [efirReports, setEfirReports] = useState(() => {
    const saved = localStorage.getItem('safeTourEFIR')
    return saved ? JSON.parse(saved) : sampleEFIRReports
  })
  const [zones, setZones] = useState(() => {
    const saved = localStorage.getItem('safeTourZones')
    return saved ? JSON.parse(saved) : sampleZones
  })
  const [incidentStats] = useState(sampleIncidentStats)
  const [officersList] = useState(sampleOfficers)

  const loginOfficer = (loginId, password) => {
    const match = sampleOfficers.find(o => o.loginId === loginId && o.password === password)
    if (match) {
      const { password, ...safeOfficer } = match
      setOfficer(safeOfficer)
      localStorage.setItem('safeTourOfficer', JSON.stringify(safeOfficer))
      setLoginMessage('Successfully logged in as ' + safeOfficer.name)
      return true
    }
    setLoginMessage('Invalid login credentials')
    return false
  }

  const logoutOfficer = () => {
    setOfficer(null)
    localStorage.removeItem('safeTourOfficer')
    setLoginMessage(null)
  }

  const updateSOSStatus = (id, status) => {
    const updated = sosAlerts.map(a => a.id === id ? { ...a, status } : a)
    setSosAlerts(updated)
    localStorage.setItem('safeTourSOS', JSON.stringify(updated))
  }

  const assignSOS = (id, officerName) => {
    const updated = sosAlerts.map(a => a.id === id ? { ...a, assignedTo: officerName, status: 'Investigating' } : a)
    setSosAlerts(updated)
    localStorage.setItem('safeTourSOS', JSON.stringify(updated))
  }

  const updateEFIRStatus = (id, status) => {
    const updated = efirReports.map(e => e.id === id ? { ...e, status } : e)
    setEfirReports(updated)
    localStorage.setItem('safeTourEFIR', JSON.stringify(updated))
  }

  const assignEFIR = (id, officerName) => {
    const updated = efirReports.map(e => e.id === id ? { ...e, assignedTo: officerName, status: 'Investigating' } : e)
    setEfirReports(updated)
    localStorage.setItem('safeTourEFIR', JSON.stringify(updated))
  }

  const addZone = (zone) => {
    const newZone = { ...zone, id: 'Z-' + Date.now().toString().slice(-4) }
    const updated = [...zones, newZone]
    setZones(updated)
    localStorage.setItem('safeTourZones', JSON.stringify(updated))
  }

  const updateZone = (id, changes) => {
    const updated = zones.map(z => z.id === id ? { ...z, ...changes } : z)
    setZones(updated)
    localStorage.setItem('safeTourZones', JSON.stringify(updated))
  }

  const deleteZone = (id) => {
    const updated = zones.filter(z => z.id !== id)
    setZones(updated)
    localStorage.setItem('safeTourZones', JSON.stringify(updated))
  }

  const touristCounts = {
    total: 1847,
    active: 632,
    districtBreakdown: [
      { district: 'Nilgiris (Ooty)', count: 712 },
      { district: 'Mysuru', count: 548 },
      { district: 'Bandipur', count: 187 },
      { district: 'Coonoor', count: 243 },
      { district: 'Chamarajanagar', count: 157 }
    ]
  }

  return (
    <AdminContext.Provider value={{
      officer, setOfficer, loginOfficer, logoutOfficer, loginMessage, setLoginMessage,
      sosAlerts, updateSOSStatus, assignSOS,
      efirReports, updateEFIRStatus, assignEFIR,
      zones, addZone, updateZone, deleteZone,
      incidentStats, officersList, touristCounts
    }}>
      {children}
    </AdminContext.Provider>
  )
}

export const useAdmin = () => useContext(AdminContext)
