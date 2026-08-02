import { Routes, Route } from 'react-router-dom'
import Home from './pages/Home'
import Login from './pages/Login'
import CreateAccount from './pages/CreateAccount'
import Dashboard from './pages/Dashboard'
import PlanTrip from './pages/PlanTrip'
import MyTrips from './pages/MyTrips'
import TripDetails from './pages/TripDetails'
import Settings from './pages/Settings'
import Profile from './pages/Profile'
import NearbyPlaces from './pages/NearbyPlaces'

function App() {
  return (
    <Routes>
      <Route path="/" element={<Home />} />
      <Route path="/login" element={<Login />} />
      <Route path="/create-account" element={<CreateAccount />} />
      <Route path="/dashboard" element={<Dashboard />} />
      <Route path="/plan-trip" element={<PlanTrip />} />
      <Route path="/my-trips" element={<MyTrips />} />
      <Route path="/trip-details/:id" element={<TripDetails />} />
      <Route path="/settings" element={<Settings />} />
      <Route path="/profile" element={<Profile />} />
      <Route path="/nearby/:type" element={<NearbyPlaces />} />
    </Routes>
  )
}

export default App
