"""Security, password hashing, and 10-character mixed alphanumeric ID formatting for school roles."""

import re
import secrets
import hashlib
import string
from typing import Optional, Tuple, Union
from app.session.models import Role

# 10-character role format regular expressions
# Format: 3-character uppercase role prefix + 7 alphanumeric characters (digits and uppercase letters)
ROLE_ID_PATTERNS = {
    Role.STUDENT: re.compile(r"^STU[A-Z0-9]{7}$"),
    Role.TEACHER: re.compile(r"^TCH[A-Z0-9]{7}$"),
    Role.PARENT: re.compile(r"^PAR[A-Z0-9]{7}$"),
    Role.PRINCIPAL: re.compile(r"^PRN[A-Z0-9]{7}$"),
}

ROLE_PREFIXES = {
    Role.STUDENT: "STU",
    Role.TEACHER: "TCH",
    Role.PARENT: "PAR",
    Role.PRINCIPAL: "PRN",
}

ROLE_DISPLAY_NAMES = {
    Role.STUDENT: "Student",
    Role.TEACHER: "Teacher",
    Role.PARENT: "Parent",
    Role.PRINCIPAL: "Principal",
}


def hash_password(password: str, salt: Optional[str] = None) -> Tuple[str, str]:
    """
    Hash a password securely using PBKDF2-HMAC-SHA256 with a cryptographically secure salt.
    Returns (password_hash_hex, salt_hex).
    """
    if not salt:
        salt = secrets.token_hex(16)
    
    salt_bytes = bytes.fromhex(salt)
    key = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt_bytes,
        100000
    )
    return key.hex(), salt


def verify_password(password: str, salt: str, password_hash: str) -> bool:
    """Verify a plain-text password against a stored salt and password hash."""
    try:
        calculated_hash, _ = hash_password(password, salt=salt)
        return secrets.compare_digest(calculated_hash, password_hash)
    except Exception:
        return False


def generate_role_id(role: Union[Role, str]) -> str:
    """
    Generate a distinct 10-character alphanumeric ID for the given role.
    Example:
      - STUDENT   -> STU83K92P1
      - TEACHER   -> TCH47M19Q5
      - PARENT    -> PAR55N20W3
      - PRINCIPAL -> PRN10A99X1
    """
    if isinstance(role, str):
        try:
            role = Role(role.upper())
        except ValueError:
            role = Role.STUDENT

    prefix = ROLE_PREFIXES.get(role, "STU")
    
    # Ensure a mixture of digits and uppercase letters
    letters = string.ascii_uppercase
    digits = string.digits
    
    # Guarantee at least 2 letters and 2 digits in the 7-character suffix
    body = [
        secrets.choice(letters),
        secrets.choice(letters),
        secrets.choice(digits),
        secrets.choice(digits),
        secrets.choice(letters + digits),
        secrets.choice(letters + digits),
        secrets.choice(letters + digits),
    ]
    # Shuffle the characters securely
    shuffled_body = "".join(secrets.SystemRandom().sample(body, len(body)))
    return f"{prefix}{shuffled_body}"


def validate_role_id_format(user_id: str, role: Optional[Union[Role, str]] = None) -> Tuple[bool, Optional[str]]:
    """
    Validate whether user_id strictly adheres to the 10-character alphanumeric format for the role.
    """
    cleaned = user_id.strip()
    
    if len(cleaned) != 10:
        return False, f"ID must be exactly 10 characters long. Received {len(cleaned)} characters."

    if role:
        if isinstance(role, str):
            try:
                role = Role(role.upper())
            except ValueError:
                return False, f"Invalid role: {role}"

        pattern = ROLE_ID_PATTERNS.get(role)
        if pattern and not pattern.match(cleaned):
            prefix = ROLE_PREFIXES.get(role, "ID")
            return False, f"Invalid {role.value} ID format. Must start with '{prefix}' followed by 7 letters/digits (e.g., {prefix}74K92P1)."
    else:
        # Check against any role pattern
        matches_any = any(pattern.match(cleaned) for pattern in ROLE_ID_PATTERNS.values())
        if not matches_any:
            return False, "ID must start with a valid role prefix ('STU', 'TCH', 'PAR', or 'PRN') followed by 7 alphanumeric characters."

    return True, None


def detect_role_from_id(user_id: str) -> Optional[Role]:
    """Infer the user's role from their 10-character ID prefix or legacy identifier."""
    cleaned = user_id.strip().upper()
    if cleaned.startswith("STU"):
        return Role.STUDENT
    elif cleaned.startswith("TCH"):
        return Role.TEACHER
    elif cleaned.startswith("PAR"):
        return Role.PARENT
    elif cleaned.startswith("PRN"):
        return Role.PRINCIPAL
    
    # Legacy fallbacks
    if cleaned.startswith("S") or "STUDENT" in cleaned:
        return Role.STUDENT
    elif cleaned.startswith("T") or "TEACHER" in cleaned:
        return Role.TEACHER
    elif cleaned.startswith("P0") or "PARENT" in cleaned:
        return Role.PARENT
    elif "PRINCIPAL" in cleaned:
        return Role.PRINCIPAL
    
    return None
