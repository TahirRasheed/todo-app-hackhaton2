"""JWT Token Management Module

Handles JWT token creation, validation, and claims extraction.
Uses HS256 (HMAC with SHA-256) algorithm for signing and verification.
"""

from datetime import datetime, timedelta, timezone
from typing import Dict, Optional
from jose import JWTError, jwt

from src.config import settings


def create_access_token(user_id: str, email: str) -> tuple[str, int]:
    """
    Create a JWT access token for authenticated user.

    Args:
        user_id: UUID of the user
        email: Email of the user

    Returns:
        Tuple of (token: str, expires_in: int seconds)

    Raises:
        ValueError: If token creation fails
    """
    try:
        # Calculate expiration time
        now = datetime.now(timezone.utc)
        expires_in = int(settings.JWT_EXPIRATION_MINUTES * 60)
        expires_at = now + timedelta(minutes=settings.JWT_EXPIRATION_MINUTES)

        # Create token payload
        payload = {
            "sub": user_id,
            "email": email,
            "iat": int(now.timestamp()),
            "exp": int(expires_at.timestamp()),
            "iss": "todo-app",
            "aud": "todo-app-users",
        }

        # Sign token
        token = jwt.encode(
            payload,
            settings.JWT_SECRET,
            algorithm=settings.JWT_ALGORITHM,
        )

        return token, expires_in

    except Exception as e:
        raise ValueError(f"Failed to create access token: {str(e)}")


def verify_token(token: str) -> Dict:
    """
    Verify JWT token signature and extract claims.

    Args:
        token: JWT token string to verify

    Returns:
        Dictionary of decoded token claims

    Raises:
        ValueError: If token is invalid or expired
    """
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM],
        )

        # Validate required claims
        required_claims = ["sub", "email", "exp", "iat"]
        for claim in required_claims:
            if claim not in payload:
                raise ValueError(f"Missing required claim: {claim}")

        return payload

    except JWTError as e:
        if "expired" in str(e).lower():
            raise ValueError("Token has expired")
        else:
            raise ValueError(f"Invalid token: {str(e)}")
    except Exception as e:
        raise ValueError(f"Token verification failed: {str(e)}")


def extract_user_from_token(token: str) -> Dict[str, str]:
    """Extract user_id and email from verified token."""
    payload = verify_token(token)
    return {
        "user_id": payload["sub"],
        "email": payload["email"],
    }


def is_token_expired(token: str) -> bool:
    """Check if token is expired without raising exception."""
    try:
        verify_token(token)
        return False
    except ValueError as e:
        if "expired" in str(e).lower():
            return True
        return True
    except Exception:
        return True


# Alias for compatibility with deps.py
decode_token = verify_token
