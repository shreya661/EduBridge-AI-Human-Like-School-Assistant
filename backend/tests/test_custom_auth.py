"""Tests for 10-character Alphanumeric Role ID Authentication & Password Hashing."""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.auth.security import (
    generate_role_id, validate_role_id_format, detect_role_from_id,
    hash_password, verify_password, ROLE_ID_PATTERNS
)
from app.session.models import Role

client = TestClient(app)


def test_10_char_role_id_generation():
    """Test that generated IDs are strictly 10-character mixed alphanumeric strings."""
    for role, prefix in [(Role.STUDENT, "STU"), (Role.TEACHER, "TCH"), (Role.PARENT, "PAR"), (Role.PRINCIPAL, "PRN")]:
        generated = generate_role_id(role)
        assert len(generated) == 10, f"Expected 10 characters, got {len(generated)} for {role}"
        assert generated.startswith(prefix), f"Expected prefix {prefix}, got {generated}"
        assert ROLE_ID_PATTERNS[role].match(generated) is not None
        
        # Verify mixture of digits and letters
        suffix = generated[3:]
        assert any(c.isdigit() for c in suffix), f"Expected at least one digit in suffix {suffix}"
        assert any(c.isalpha() for c in suffix), f"Expected at least one letter in suffix {suffix}"


def test_10_char_role_id_validation():
    """Test validation of valid and invalid 10-character role IDs."""
    # Valid IDs
    assert validate_role_id_format("STU94A72B8", Role.STUDENT)[0] is True
    assert validate_role_id_format("TCH47M19Q5", Role.TEACHER)[0] is True
    assert validate_role_id_format("PAR55N20W3", Role.PARENT)[0] is True
    assert validate_role_id_format("PRN10A99X1", Role.PRINCIPAL)[0] is True

    # Invalid lengths
    assert validate_role_id_format("STU123", Role.STUDENT)[0] is False
    assert validate_role_id_format("STU1234567890", Role.STUDENT)[0] is False

    # Invalid prefixes for role
    assert validate_role_id_format("TCH94A72B8", Role.STUDENT)[0] is False
    assert validate_role_id_format("STU47M19Q5", Role.TEACHER)[0] is False

    # Invalid characters
    assert validate_role_id_format("STU94@72!8", Role.STUDENT)[0] is False


def test_password_hashing_and_verification():
    """Test PBKDF2 salted password hashing."""
    raw_pass = "SecureSecret#2026"
    pw_hash, salt = hash_password(raw_pass)
    assert len(pw_hash) == 64
    assert len(salt) == 32

    # Verification success
    assert verify_password(raw_pass, salt, pw_hash) is True

    # Verification failure
    assert verify_password("WrongPassword", salt, pw_hash) is False


def test_generate_id_endpoint():
    """Test GET /api/v1/auth/generate-id endpoint."""
    res = client.get("/api/v1/auth/generate-id?role=TEACHER")
    assert res.status_code == 200
    data = res.json()
    assert data["role"] == "teacher"
    assert data["prefix"] == "TCH"
    assert len(data["user_id"]) == 10
    assert data["user_id"].startswith("TCH")


def test_signup_and_login_flow():
    """Test full student signup with 10-char ID and subsequent login with password."""
    # 1. Sign up with auto-generated ID
    signup_payload = {
        "name": "Dev Student",
        "role": "STUDENT",
        "password": "MySuperPassword123",
        "email": "dev.student@school.org"
    }
    signup_res = client.post("/api/v1/auth/signup", json=signup_payload)
    assert signup_res.status_code == 201
    signup_data = signup_res.json()
    assert signup_data["success"] is True
    student_id = signup_data["user"]["user_id"]
    assert len(student_id) == 10
    assert student_id.startswith("STU")

    # 2. Login with correct password
    login_res = client.post("/api/v1/auth/login", json={"user_id": student_id, "password": "MySuperPassword123"})
    assert login_res.status_code == 200
    login_data = login_res.json()
    assert login_data["success"] is True
    assert login_data["user"]["user_id"] == student_id
    assert "session_id" in login_res.cookies

    # 3. Login with incorrect password fails
    bad_login_res = client.post("/api/v1/auth/login", json={"user_id": student_id, "password": "IncorrectPassword"})
    assert bad_login_res.status_code == 401


def test_signup_custom_10_char_id_validation():
    """Test that custom ID is strictly validated upon sign-up."""
    # Invalid custom ID (wrong prefix for Teacher)
    bad_payload = {
        "name": "Math Teacher",
        "role": "TEACHER",
        "user_id": "STU99X88Y7",
        "password": "Password@123"
    }
    res = client.post("/api/v1/auth/signup", json=bad_payload)
    assert res.status_code == 400
    assert "Invalid TEACHER ID format" in res.json()["detail"]

    # Valid custom ID for Teacher
    good_id = generate_role_id(Role.TEACHER)
    good_payload = {
        "name": "Math Teacher",
        "role": "TEACHER",
        "user_id": good_id,
        "password": "Password@123",
        "email": f"math.teacher.{good_id}@school.org"
    }
    res2 = client.post("/api/v1/auth/signup", json=good_payload)
    assert res2.status_code == 201
    assert res2.json()["user"]["user_id"] == good_id
