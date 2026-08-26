"""
Phase 14 — Testing.

Real test cases matching the exact scenarios from the Phase 0 plan:
  - Safe tourist / place
  - Dangerous tourist / place
  - Off-route tourist
  - Restricted zone entry
  - Multiple abnormal movements

Run from the ml/ root:
    pip install pytest
    pytest tests/test_api.py -v
"""

import os
import sys

# main.py lives in src/api/ — add it to the path so tests can import it
# regardless of which directory pytest is run from.
_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_THIS_DIR, "..", "src", "api"))

import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


# ---------------------------------------------------------------------
# /predict-risk — Safe place vs Dangerous place
# ---------------------------------------------------------------------
def test_predict_risk_safe_place():
    """A popular, low-crime, non-restricted place should predict Safe."""
    response = client.post("/predict-risk", json={
        "crime_score": 1, "heavy_rain_days_count": 0, "restricted": False,
        "distance_to_hospital_km": 2, "crowd_density_avg": 80,
        "cluster": "Ooty", "type": "garden",
    })
    assert response.status_code == 200
    data = response.json()
    assert data["prediction"] == "Safe"


def test_predict_risk_dangerous_place():
    """A restricted, high-crime, isolated place should predict Dangerous."""
    response = client.post("/predict-risk", json={
        "crime_score": 8, "heavy_rain_days_count": 9, "restricted": True,
        "distance_to_hospital_km": 30, "crowd_density_avg": 5,
        "cluster": "Kunda", "type": "wildlife",
    })
    assert response.status_code == 200
    data = response.json()
    assert data["prediction"] == "Dangerous"


def test_predict_risk_returns_confidence():
    """Every prediction should come with a confidence score between 0 and 1."""
    response = client.post("/predict-risk", json={"crime_score": 5})
    data = response.json()
    assert 0 <= data["confidence"] <= 1


# ---------------------------------------------------------------------
# /safety-score — should score restricted/risky places lower than safe ones
# ---------------------------------------------------------------------
def test_safety_score_restricted_place_scores_lower():
    """A restricted place should score meaningfully lower than a safe one."""
    restricted_response = client.post("/safety-score", json={
        "crime_score": 6, "heavy_rain_days_count": 8, "restricted": True,
        "distance_to_hospital_km": 25, "crowd_density_avg": 10,
    })
    safe_response = client.post("/safety-score", json={
        "crime_score": 1, "heavy_rain_days_count": 0, "restricted": False,
        "distance_to_hospital_km": 2, "crowd_density_avg": 80,
    })
    restricted_score = restricted_response.json()["safety_score"]
    safe_score = safe_response.json()["safety_score"]
    assert restricted_score < safe_score


def test_safety_score_is_within_valid_range():
    response = client.post("/safety-score", json={"crime_score": 5})
    score = response.json()["safety_score"]
    assert 0 <= score <= 100


# ---------------------------------------------------------------------
# /detect-deviation — on-route tourist vs off-route tourist
# ---------------------------------------------------------------------
PLANNED_ROUTE = [[11.410000, 76.699997], [11.418752, 76.711038], [11.402417, 76.736722]]


def test_deviation_on_route_tourist():
    """A tourist very close to the planned route should NOT be flagged."""
    response = client.post("/detect-deviation", json={
        "planned_route": PLANNED_ROUTE,
        "current_location": [11.4180, 76.7105],  # near the 2nd waypoint
        "threshold_km": 0.5,
    })
    assert response.status_code == 200
    data = response.json()
    assert data["is_deviated"] is False


def test_deviation_off_route_tourist():
    """A tourist far from the planned route (e.g. wandered toward a
    restricted zone) SHOULD be flagged."""
    response = client.post("/detect-deviation", json={
        "planned_route": PLANNED_ROUTE,
        "current_location": [11.322, 76.611],  # near Avalanche Lake, far away
        "threshold_km": 0.5,
    })
    assert response.status_code == 200
    data = response.json()
    assert data["is_deviated"] is True
    assert data["distance_from_route_km"] > 5  # sanity check it's genuinely far


# ---------------------------------------------------------------------
# /detect-anomaly — restricted zone entry / suspicious tourist
# ---------------------------------------------------------------------
def test_anomaly_normal_tourist_not_flagged():
    """A tourist with no restricted-zone visits and typical stats should
    NOT be flagged suspicious."""
    response = client.post("/detect-anomaly", json={
        "n_visits": 12, "n_unique_clusters": 3, "n_restricted_visits": 0,
        "restricted_ratio": 0.0, "avg_dwell_minutes": 60, "total_distance_km": 100,
        "avg_distance_per_hop_km": 8, "revisit_ratio": 0.1,
    })
    assert response.status_code == 200
    data = response.json()
    assert data["is_suspicious"] is False


def test_anomaly_restricted_zone_entry_flagged():
    """A tourist with repeated restricted-zone entries and unusual stats
    SHOULD be flagged — this is the 'restricted area entry' scenario
    from the Phase 0 test plan."""
    response = client.post("/detect-anomaly", json={
        "n_visits": 15, "n_unique_clusters": 5, "n_restricted_visits": 6,
        "restricted_ratio": 0.4, "avg_dwell_minutes": 20, "total_distance_km": 250,
        "avg_distance_per_hop_km": 18, "revisit_ratio": 0.5,
    })
    assert response.status_code == 200
    data = response.json()
    assert data["is_suspicious"] is True


# ---------------------------------------------------------------------
# /pattern-detection — multiple abnormal movements (repeated in/out loop)
# ---------------------------------------------------------------------
def test_pattern_normal_tourist_not_flagged():
    """Values here are based on the ACTUAL distribution of normal tourists
    in tourist_pattern_features.csv (unique_bigram_ratio averages ~0.99
    for normal tourists — barely any repeated back-and-forth), not a guess."""
    response = client.post("/pattern-detection", json={
        "n_visits": 13, "restricted_entries": 0, "alternation_count": 1,
        "alternation_ratio": 0.08, "most_common_bigram_freq": 1, "unique_bigram_ratio": 1.0,
    })
    assert response.status_code == 200
    data = response.json()
    assert data["is_flagged_pattern"] is False


def test_pattern_repeated_restricted_loop_flagged():
    """This is the exact scenario from the Phase 0 plan: 'Forest -> Exit
    -> Forest -> Exit' — repeated back-and-forth into a restricted zone
    should be flagged."""
    response = client.post("/pattern-detection", json={
        "n_visits": 16, "restricted_entries": 5, "alternation_count": 10,
        "alternation_ratio": 0.7, "most_common_bigram_freq": 7, "unique_bigram_ratio": 0.25,
    })
    assert response.status_code == 200
    data = response.json()
    assert data["is_flagged_pattern"] is True


# ---------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------
def test_health_check():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


# ---------------------------------------------------------------------
# Input validation — malformed requests should fail cleanly, not crash
# ---------------------------------------------------------------------
def test_deviation_missing_required_field_returns_422():
    """FastAPI should reject a request missing a required field with a
    clean validation error, not a server crash."""
    response = client.post("/detect-deviation", json={"planned_route": PLANNED_ROUTE})
    assert response.status_code == 422  # missing current_location
