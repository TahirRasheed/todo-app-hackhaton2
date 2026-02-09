"""Password Management Module

Handles password hashing, verification, and strength validation.
Uses bcrypt for secure password hashing.
"""

import re
from passlib.context import CryptContext

# Bcrypt context with cost factor 10
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """
    Hash a plain text password using bcrypt.

    Args:
        password: Plain text password to hash

    Returns:
        Bcrypt hashed password string

    Raises:
        ValueError: If hashing fails
    """
    try:
        return pwd_context.hash(password)
    except Exception as e:
        raise ValueError(f"Failed to hash password: {str(e)}")


def verify_password(password: str, hash_password_value: str) -> bool:
    """
    Verify a plain text password against a bcrypt hash.

    Uses constant-time comparison to prevent timing attacks.

    Args:
        password: Plain text password to verify
        hash_password_value: Bcrypt hash to verify against

    Returns:
        True if password matches hash, False otherwise
    """
    try:
        return pwd_context.verify(password, hash_password_value)
    except Exception:
        # Return False for any verification error
        return False


def validate_password_strength(password: str) -> tuple[bool, str]:
    """
    Validate password meets strength requirements.

    Requirements:
    - Minimum 8 characters
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one digit

    Args:
        password: Password to validate

    Returns:
        Tuple of (is_valid: bool, message: str)
    """
    if not password:
        return False, "Password is required"

    if len(password) < 8:
        return False, "Password must be at least 8 characters"

    if not re.search(r"[A-Z]", password):
        return False, "Password must contain at least one uppercase letter"

    if not re.search(r"[a-z]", password):
        return False, "Password must contain at least one lowercase letter"

    if not re.search(r"\d", password):
        return False, "Password must contain at least one digit"

    return True, "Password strength is valid"


def check_password_strength(password: str) -> bool:
    """
    Simple boolean check for password strength.

    Args:
        password: Password to check

    Returns:
        True if password meets strength requirements, False otherwise
    """
    is_valid, _ = validate_password_strength(password)
    return is_valid
