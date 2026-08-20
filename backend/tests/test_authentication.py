# backend/tests/test_authentication.py
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_login_valid_student():
    """Test valid student login"""
    response = client.post("/api/v1/auth/login", json={"user_id": "student-001"})
    assert response.status_code == 200
    data = response.json()
    assert data["user"]["user_id"] == "student-001"
    assert data["user"]["role"] == "student"
    assert "session_id" in response.cookies


def test_login_valid_parent():
    """Test valid parent login"""
    response = client.post("/api/v1/auth/login", json={"user_id": "parent-001"})
    assert response.status_code == 200
    data = response.json()
    assert data["user"]["user_id"] == "parent-001"
    assert data["user"]["role"] == "parent"


def test_login_invalid_user():
    """Test login with invalid user_id"""
    response = client.post("/api/v1/auth/login", json={"user_id": "invalid-user"})
    assert response.status_code == 401


def test_get_current_user_authenticated():
    """Test getting current user with valid session"""
    # First login
    login_response = client.post("/api/v1/auth/login", json={"user_id": "student-001"})
    assert login_response.status_code == 200
    
    # Get current user
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 200
    data = response.json()
    assert data["user"]["user_id"] == "student-001"
    assert data["user"]["role"] == "student"


def test_get_current_user_unauthenticated():
    """Test getting current user without session"""
    client.cookies.clear()
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401


def test_logout():
    """Test logout functionality"""
    # Login first
    login_response = client.post("/api/v1/auth/login", json={"user_id": "student-001"})
    assert login_response.status_code == 200
    
    # Logout
    response = client.post("/api/v1/auth/logout")
    assert response.status_code == 200
    
    # Try to access protected endpoint after logout
    me_response = client.get("/api/v1/auth/me")
    assert me_response.status_code == 401


def test_authorization_with_session():
    """Test that authorization now uses session identity, not client-provided user_id"""
    # Login as student
    login_response = client.post("/api/v1/auth/login", json={"user_id": "student-001"})
    assert login_response.status_code == 200
    
    # Try to authorize view_all_students (should fail for student)
    response = client.post("/api/v1/authz/authorize", json={
        "intent": "view_all_students"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["authorized"] == False  # Student should not be authorized


def test_role_spoofing_prevention():
    """Test that client cannot change role by sending different user_id"""
    # Login as student
    login_response = client.post("/api/v1/auth/login", json={"user_id": "student-001"})
    assert login_response.status_code == 200
    
    # Even if client tries to send principal intent, they're still authenticated as student
    response = client.post("/api/v1/authz/authorize", json={
        "intent": "view_all_students"
    })
    # Should still be denied because the session identity is student-001
    assert response.status_code == 200
    data = response.json()
    assert data["authorized"] == False
