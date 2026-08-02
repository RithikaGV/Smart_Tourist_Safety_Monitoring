import React, { createContext, useState, useContext, useEffect } from 'react'

const TripsContext = createContext()

// Helper functions to classify trips
export const classifyTrips = (trips) => {
  const now = new Date()
  const oneDayMs = 24 * 60 * 60 * 1000 // 1 day in milliseconds

  return trips.reduce((acc, trip) => {
    const tripDateTime = new Date(`${trip.date}T${trip.time}`)
    const timeDiff = tripDateTime - now

    if (timeDiff < -oneDayMs) {
      // Trip was over a day ago → past
      acc.past.push(trip)
    } else if (timeDiff <= oneDayMs && timeDiff >= -oneDayMs) {
      // Trip is within ±1 day → current (ongoing)
      acc.current.push(trip)
    } else {
      // Trip is more than a day in the future → upcoming
      acc.upcoming.push(trip)
    }
    return acc
  }, { past: [], current: [], upcoming: [] })
}

export const TripsProvider = ({ children }) => {
  // Initial sample trips with varying dates for testing
  const today = new Date()
  const tomorrow = new Date(today.getTime() + 24 * 60 * 60 * 1000)
  const yesterday = new Date(today.getTime() - 24 * 60 * 60 * 1000)
  const nextWeek = new Date(today.getTime() + 7 * 24 * 60 * 60 * 1000)
  const lastWeek = new Date(today.getTime() - 7 * 24 * 60 * 60 * 1000)

  const formatDate = (date) => date.toISOString().split('T')[0]

  const initialTrips = [
    {
      id: 1,
      destination: "Past Trip Example",
      date: formatDate(lastWeek),
      time: "09:00",
      travelers: 2,
      type: "friends",
      lat: 11.5950,
      lng: 76.6700,
    },
    {
      id: 2,
      destination: "Current Trip Example",
      date: formatDate(yesterday),
      time: "07:00",
      travelers: 4,
      type: "family",
      lat: 11.6200,
      lng: 76.6300,
    },
    {
      id: 3,
      destination: "Upcoming Trip 1",
      date: formatDate(tomorrow),
      time: "10:00",
      travelers: 3,
      type: "solo",
      lat: 11.4064,
      lng: 76.6932,
    },
    {
      id: 4,
      destination: "Upcoming Trip 2",
      date: formatDate(nextWeek),
      time: "08:00",
      travelers: 5,
      type: "family",
      lat: 11.6075,
      lng: 76.6635,
    },
  ]

  const [trips, setTrips] = useState(() => {
    const saved = localStorage.getItem('smartTouristTrips')
    return saved ? JSON.parse(saved) : initialTrips
  })

  // Save to localStorage when trips change
  useEffect(() => {
    localStorage.setItem('smartTouristTrips', JSON.stringify(trips))
  }, [trips])

  const addTrip = (trip) => {
    const newTrip = {
      ...trip,
      id: Date.now(),
    }
    setTrips([...trips, newTrip])
  }

  const deleteTrip = (id) => {
    setTrips(trips.filter(trip => trip.id !== id))
  }

  const updateTrip = (id, updatedTrip) => {
    setTrips(trips.map(trip => trip.id === id ? { ...trip, ...updatedTrip } : trip))
  }

  return (
    <TripsContext.Provider value={{ trips, addTrip, deleteTrip, updateTrip, classifyTrips }}>
      {children}
    </TripsContext.Provider>
  )
}

export const useTrips = () => useContext(TripsContext)
