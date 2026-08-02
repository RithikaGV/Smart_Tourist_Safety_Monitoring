import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.jsx'
import { BrowserRouter } from 'react-router-dom'
import { UserProvider } from './UserContext.jsx'
import { TripsProvider } from './TripsContext.jsx'

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <BrowserRouter>
      <UserProvider>
        <TripsProvider>
          <App />
        </TripsProvider>
      </UserProvider>
    </BrowserRouter>
  </StrictMode>,
)
