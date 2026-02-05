"""
Tests for the Mergington High School API
"""

import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app

client = TestClient(app)


def test_root_redirect():
    """Test that root endpoint redirects to static/index.html"""
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 307
    assert "/static/index.html" in response.headers["location"]


def test_get_activities():
    """Test that we can fetch all activities"""
    response = client.get("/activities")
    assert response.status_code == 200
    
    activities = response.json()
    assert isinstance(activities, dict)
    assert "Chess Club" in activities
    assert "Programming Class" in activities
    
    # Verify activity structure
    chess_club = activities["Chess Club"]
    assert "description" in chess_club
    assert "schedule" in chess_club
    assert "max_participants" in chess_club
    assert "participants" in chess_club
    assert isinstance(chess_club["participants"], list)


def test_signup_for_activity():
    """Test signing up for an activity"""
    response = client.post(
        "/activities/Chess Club/signup?email=test@mergington.edu"
    )
    assert response.status_code == 200
    assert "Signed up" in response.json()["message"]
    
    # Verify participant was added
    activities = client.get("/activities").json()
    assert "test@mergington.edu" in activities["Chess Club"]["participants"]


def test_signup_duplicate():
    """Test that duplicate signup fails"""
    # First signup
    client.post("/activities/Chess Club/signup?email=duplicate@mergington.edu")
    
    # Second signup with same email should fail
    response = client.post(
        "/activities/Chess Club/signup?email=duplicate@mergington.edu"
    )
    assert response.status_code == 400
    assert "already signed up" in response.json()["detail"]


def test_signup_nonexistent_activity():
    """Test signing up for non-existent activity"""
    response = client.post(
        "/activities/Nonexistent Club/signup?email=test@mergington.edu"
    )
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]


def test_unregister_from_activity():
    """Test unregistering from an activity"""
    email = "unregister@mergington.edu"
    
    # First signup
    client.post(f"/activities/Chess Club/signup?email={email}")
    
    # Then unregister
    response = client.delete(
        f"/activities/Chess Club/unregister?email={email}"
    )
    assert response.status_code == 200
    assert "Unregistered" in response.json()["message"]
    
    # Verify participant was removed
    activities = client.get("/activities").json()
    assert email not in activities["Chess Club"]["participants"]


def test_unregister_nonexistent_participant():
    """Test unregistering when not registered"""
    response = client.delete(
        "/activities/Chess Club/unregister?email=notregistered@mergington.edu"
    )
    assert response.status_code == 400
    assert "not registered" in response.json()["detail"]


def test_unregister_nonexistent_activity():
    """Test unregistering from non-existent activity"""
    response = client.delete(
        "/activities/Nonexistent Club/unregister?email=test@mergington.edu"
    )
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]
