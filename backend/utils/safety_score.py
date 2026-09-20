"""
utils/safety_score.py
Rule-based stand-in for the "AI risk heatmap" model. Produces the exact
document shape already used in ai_safety (overallSafetyScore, crimeRisk,
womenSafety, weatherRisk, nightSafety). Swap the body of compute_safety_score
for a real trained model later - callers don't need to change.
"""
from datetime import datetime
from shapely.geometry import shape, Point
from shapely.ops import nearest_points
from database.db import get_db

SEVERITY_WEIGHT = {"low": 1, "medium": 2, "high": 3, "critical": 4}


def _band(score: float) -> str:
    if score >= 7:
        return "Low"
    if score >= 4:
        return "Medium"
    return "High"


async def compute_safety_score(lat: float, lng: float, at: datetime | None = None) -> dict:
    at = at or datetime.utcnow()
    is_night = at.hour >= 19 or at.hour < 6

    db = get_db()
    geofences = await db["geofences"].find({"active": True}).to_list(length=None)
    pt = Point(lng, lat)

    nearest_severity_penalty = 0
    for gf in geofences:
        try:
            polygon = shape(gf["area"])
            weight = SEVERITY_WEIGHT.get(gf.get("severity", "low"), 1)
            if polygon.contains(pt):
                nearest_severity_penalty = max(nearest_severity_penalty, weight * 2)
            else:
                # rough degrees->km conversion (good enough for a soft penalty, not final safety math)
                distance_km = pt.distance(nearest_points(pt, polygon)[1]) * 111
                if distance_km < 2:
                    nearest_severity_penalty = max(nearest_severity_penalty, weight)
        except Exception:
            continue

    crime_score = 9 - nearest_severity_penalty
    women_safety_score = (crime_score - 1.5) if is_night else crime_score
    night_safety_score = (6 - nearest_severity_penalty * 0.5) if is_night else 9
    weather_score = 8  # placeholder until a weather API is wired in

    crime_score = max(1, min(10, crime_score))
    women_safety_score = max(1, min(10, women_safety_score))
    night_safety_score = max(1, min(10, night_safety_score))
    weather_score = max(1, min(10, weather_score))

    overall = round((crime_score + women_safety_score + night_safety_score + weather_score) / 4, 1)

    return {
        "overallSafetyScore": overall,
        "crimeRisk": _band(crime_score),
        "womenSafety": _band(women_safety_score),
        "weatherRisk": _band(weather_score),
        "nightSafety": _band(night_safety_score),
        "generatedAt": datetime.utcnow(),
    }
