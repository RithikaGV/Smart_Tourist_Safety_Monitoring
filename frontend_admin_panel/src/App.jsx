import { Routes, Route, Navigate } from 'react-router-dom'
import { AdminProvider, useAdmin } from './AdminContext.jsx'
import Login from './pages/Login.jsx'
import Dashboard from './pages/Dashboard.jsx'
import RiskHeatmap from './pages/RiskHeatmap.jsx'
import SOSMonitoring from './pages/SOSMonitoring.jsx'
import SOSDetails from './pages/SOSDetails.jsx'
import EFIRMonitoring from './pages/EFIRMonitoring.jsx'
import EFIRDetails from './pages/EFIRDetails.jsx'
import ZoneManagement from './pages/ZoneManagement.jsx'
import AIAnalytics from './pages/AIAnalytics.jsx'

function PrivateRoute({ children }) {
  const { officer } = useAdmin()
  return officer ? children : <Navigate to="/login" replace />
}

function App() {
  return (
    <AdminProvider>
      <Routes>
        <Route path="/" element={<Navigate to="/login" replace />} />
        <Route path="/login" element={<Login />} />
        <Route path="/dashboard" element={<PrivateRoute><Dashboard /></PrivateRoute>} />
        <Route path="/risk-heatmap" element={<PrivateRoute><RiskHeatmap /></PrivateRoute>} />
        <Route path="/sos-monitoring" element={<PrivateRoute><SOSMonitoring /></PrivateRoute>} />
        <Route path="/sos-details/:id" element={<PrivateRoute><SOSDetails /></PrivateRoute>} />
        <Route path="/efir-monitoring" element={<PrivateRoute><EFIRMonitoring /></PrivateRoute>} />
        <Route path="/efir-details/:id" element={<PrivateRoute><EFIRDetails /></PrivateRoute>} />
        <Route path="/zone-management" element={<PrivateRoute><ZoneManagement /></PrivateRoute>} />
        <Route path="/ai-analytics" element={<PrivateRoute><AIAnalytics /></PrivateRoute>} />
        <Route path="*" element={<Navigate to="/login" replace />} />
      </Routes>
    </AdminProvider>
  )
}

export default App
