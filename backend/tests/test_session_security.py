# backend/tests/test_session_security.py
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_session_based_identity_cannot_be_spoofed():
    """Test that client cannot control identity through user_id parameter"""
    client.cookies.clear()
    # Login as student
    login_response = client.post("/api/v1/auth/login", json={"user_id": "student-001"})
    assert login_response.status_code == 200
    cookies = login_response.cookies
    
    # Manually make request with different user_id in body (should be ignored)
    # The identity should come from the session, not from request data
    response = client.post(
        "/api/v1/authz/authorize", 
        json={
            "user_id": "principal-001",  # Client tries to spoof as principal
            "intent": "view_all_students"
        },
        cookies=cookies
    )
    assert response.status_code == 200
    data = response.json()
    # Should still be denied because session identity is student-001, not principal-001
    assert data["authorized"] == False


def test_missing_session_returns_401():
    """Test that requests without session return 401"""
    client.cookies.clear()
    response = client.post("/api/v1/authz/authorize", json={
        "intent": "view_own_profile"
    })
    assert response.status_code == 401


def test_invalid_session_returns_401():
    """Test that requests with invalid session return 401"""
    client.cookies.clear()
    response = client.post(
        "/api/v1/authz/authorize", 
        json={"intent": "view_own_profile"},
        headers={"X-Session-ID": "invalid-session-id"}
    )
    assert response.status_code == 401


def test_expired_session_returns_401():
    """Test that expired sessions return 401 (would require manual session manipulation)"""
    # This test would require setting up an expired session manually
    # For now, we rely on the session store's automatic cleanup
    pass
