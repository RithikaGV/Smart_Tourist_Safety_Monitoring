export const geocodeLocation = async (query) => {
  if (!query || typeof query !== 'string') return null

  const normalizedQuery = query.trim()
  if (!normalizedQuery) return null

  try {
    const response = await fetch(
      `https://nominatim.openstreetmap.org/search?format=jsonv2&limit=1&addressdetails=1&q=${encodeURIComponent(normalizedQuery)}`,
      {
        headers: {
          'Accept-Language': 'en'
        }
      }
    )

    if (!response.ok) throw new Error('Geocoding request failed')

    const data = await response.json()
    if (!Array.isArray(data) || data.length === 0) return null

    const match = data[0]
    return {
      lat: parseFloat(match.lat),
      lng: parseFloat(match.lon),
      displayName: match.display_name || normalizedQuery
    }
  } catch (error) {
    console.warn('Location lookup failed:', error)
    return null
  }
}
