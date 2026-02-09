"""Unit tests for security modules (password hashing, JWT, validation)"""
import pytest
from datetime import datetime, timedelta, timezone

from src.security.password import (
    hash_password,
    verify_password,
    validate_password_strength,
    check_password_strength
)
from src.security.jwt import (
    create_access_token,
    verify_token,
    extract_user_from_token,
    is_token_expired
)


class TestPasswordHashing:
    """Test password hashing and verification with bcrypt"""

    def test_hash_password_returns_hashed_string(self):
        """Test password hashing returns bcrypt hash"""
        password = "SecurePass123"
        hashed = hash_password(password)

        # Bcrypt hashes start with $2b$ or $2a$
        assert hashed.startswith("$2b$") or hashed.startswith("$2a$")
        assert len(hashed) == 60  # Bcrypt hashes are 60 characters
        assert hashed != password  # Not plaintext

    def test_hash_password_generates_different_salts(self):
        """Test same password generates different hashes (different salts)"""
        password = "SecurePass123"
        hash1 = hash_password(password)
        hash2 = hash_password(password)

        assert hash1 != hash2  # Different salts

    def test_verify_password_returns_true_for_correct_password(self):
        """Test password verification succeeds for correct password"""
        password = "SecurePass123"
        hashed = hash_password(password)

        assert verify_password(password, hashed) is True

    def test_verify_password_returns_false_for_incorrect_password(self):
        """Test password verification fails for incorrect password"""
        password = "SecurePass123"
        hashed = hash_password(password)

        assert verify_password("WrongPassword", hashed) is False

    def test_verify_password_returns_false_for_invalid_hash(self):
        """Test password verification fails gracefully for invalid hash"""
        assert verify_password("password", "invalid-hash") is False

    def test_hash_password_raises_for_empty_password(self):
        """Test hashing empty password raises error"""
        with pytest.raises(ValueError):
            hash_password("")


class TestPasswordStrengthValidation:
    """Test password strength validation rules"""

    def test_validate_password_strength_accepts_valid_password(self):
        """Test valid password passes all checks"""
        valid_passwords = [
            "SecurePass123",
            "MyP@ssw0rd",
            "Test1234User",
            "Abcd1234efgh",
        ]

        for password in valid_passwords:
            is_valid, message = validate_password_strength(password)
            assert is_valid is True
            assert message == "Password strength is valid"

    def test_validate_password_strength_rejects_too_short(self):
        """Test password shorter than 8 chars is rejected"""
        is_valid, message = validate_password_strength("Pass1")
        assert is_valid is False
        assert "at least 8 characters" in message

    def test_validate_password_strength_rejects_no_uppercase(self):
        """Test password without uppercase is rejected"""
        is_valid, message = validate_password_strength("password123")
        assert is_valid is False
        assert "uppercase letter" in message

    def test_validate_password_strength_rejects_no_lowercase(self):
        """Test password without lowercase is rejected"""
        is_valid, message = validate_password_strength("PASSWORD123")
        assert is_valid is False
        assert "lowercase letter" in message

    def test_validate_password_strength_rejects_no_digit(self):
        """Test password without digit is rejected"""
        is_valid, message = validate_password_strength("PasswordOnly")
        assert is_valid is False
        assert "digit" in message

    def test_validate_password_strength_rejects_empty(self):
        """Test empty password is rejected"""
        is_valid, message = validate_password_strength("")
        assert is_valid is False
        assert "required" in message

    def test_check_password_strength_returns_boolean(self):
        """Test simple boolean check function"""
        assert check_password_strength("SecurePass123") is True
        assert check_password_strength("weak") is False


class TestJWTTokenCreation:
    """Test JWT token creation and claims"""

    def test_create_access_token_returns_token_and_expiration(self):
        """Test token creation returns JWT string and expiration time"""
        user_id = "550e8400-e29b-41d4-a716-446655440000"
        email = "test@example.com"

        token, expires_in = create_access_token(user_id, email)

        assert isinstance(token, str)
        assert len(token) > 100  # JWT tokens are long strings
        assert expires_in == 900  # 15 minutes = 900 seconds

    def test_create_access_token_contains_required_claims(self):
        """Test token contains user_id (sub) and email claims"""
        user_id = "550e8400-e29b-41d4-a716-446655440000"
        email = "test@example.com"

        token, _ = create_access_token(user_id, email)
        payload = verify_token(token)

        assert payload["sub"] == user_id
        assert payload["email"] == email
        assert payload["iss"] == "todo-app"
        assert payload["aud"] == "todo-app-users"
        assert "exp" in payload
        assert "iat" in payload

    def test_create_access_token_expiration_is_15_minutes(self):
        """Test token expires in 15 minutes (900 seconds)"""
        user_id = "550e8400-e29b-41d4-a716-446655440000"
        email = "test@example.com"

        token, expires_in = create_access_token(user_id, email)
        payload = verify_token(token)

        exp_timestamp = payload["exp"]
        iat_timestamp = payload["iat"]

        # Difference should be 900 seconds (15 minutes)
        assert exp_timestamp - iat_timestamp == 900
        assert expires_in == 900


class TestJWTTokenVerification:
    """Test JWT token verification and extraction"""

    def test_verify_token_succeeds_for_valid_token(self):
        """Test token verification succeeds for valid token"""
        user_id = "550e8400-e29b-41d4-a716-446655440000"
        email = "test@example.com"

        token, _ = create_access_token(user_id, email)
        payload = verify_token(token)

        assert payload["sub"] == user_id
        assert payload["email"] == email

    def test_verify_token_raises_for_invalid_signature(self):
        """Test token verification fails for tampered token"""
        user_id = "550e8400-e29b-41d4-a716-446655440000"
        email = "test@example.com"

        token, _ = create_access_token(user_id, email)

        # Tamper with token
        tampered_token = token[:-10] + "tamperedXX"

        with pytest.raises(ValueError, match="Invalid token"):
            verify_token(tampered_token)

    def test_verify_token_raises_for_malformed_token(self):
        """Test token verification fails for malformed token"""
        with pytest.raises(ValueError, match="Invalid token"):
            verify_token("not-a-jwt-token")

    def test_extract_user_from_token_returns_user_data(self):
        """Test extracting user_id and email from token"""
        user_id = "550e8400-e29b-41d4-a716-446655440000"
        email = "test@example.com"

        token, _ = create_access_token(user_id, email)
        user_data = extract_user_from_token(token)

        assert user_data["user_id"] == user_id
        assert user_data["email"] == email

    def test_is_token_expired_returns_false_for_valid_token(self):
        """Test token expiration check returns False for valid token"""
        user_id = "550e8400-e29b-41d4-a716-446655440000"
        email = "test@example.com"

        token, _ = create_access_token(user_id, email)

        assert is_token_expired(token) is False

    def test_is_token_expired_returns_true_for_invalid_token(self):
        """Test token expiration check returns True for invalid token"""
        assert is_token_expired("invalid-token") is True


class TestPasswordStrengthEdgeCases:
    """Test edge cases for password validation"""

    def test_password_with_special_characters_is_valid(self):
        """Test password with special characters is accepted"""
        # Special chars are not required, only uppercase, lowercase, digit
        is_valid, _ = validate_password_strength("Pass@123!")
        assert is_valid is True

    def test_password_exactly_8_chars_is_valid(self):
        """Test minimum length password (8 chars) is accepted"""
        is_valid, _ = validate_password_strength("Abcd1234")
        assert is_valid is True

    def test_password_very_long_is_valid(self):
        """Test very long password is accepted"""
        long_password = "SecurePass123" * 10
        is_valid, _ = validate_password_strength(long_password)
        assert is_valid is True
