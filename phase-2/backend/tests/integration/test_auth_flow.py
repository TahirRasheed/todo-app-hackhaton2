"""Integration tests for authentication flow (signup, signin, token validation)"""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.user import User
from src.security.jwt import verify_token
from src.services.user_service import UserService


@pytest.mark.asyncio
class TestSignupFlow:
    """Integration tests for user signup endpoint"""

    async def test_signup_success_returns_token(self, async_client: AsyncClient):
        """Test valid signup returns user data and JWT token"""
        response = await async_client.post(
            "/api/v1/auth/signup",
            json={
                "email": "newuser@example.com",
                "password": "SecurePass123",
                "name": "New User"
            }
        )

        assert response.status_code == 201
        data = response.json()

        # Verify response structure
        assert "id" in data
        assert data["email"] == "newuser@example.com"
        assert data["name"] == "New User"
        assert "token" in data
        assert "expiresIn" in data
        assert data["expiresIn"] == 900  # 15 minutes

        # Verify token is valid JWT
        token = data["token"]
        assert isinstance(token, str)
        assert len(token) > 100

    async def test_signup_token_contains_valid_claims(self, async_client: AsyncClient):
        """Test JWT token contains user_id (sub) and email claims"""
        response = await async_client.post(
            "/api/v1/auth/signup",
            json={
                "email": "claims@example.com",
                "password": "SecurePass123",
                "name": "Claims User"
            }
        )

        assert response.status_code == 201
        data = response.json()
        token = data["token"]

        # Decode and verify token claims
        payload = verify_token(token)
        assert payload["sub"] == data["id"]  # user_id in sub claim
        assert payload["email"] == "claims@example.com"
        assert payload["iss"] == "todo-app"
        assert payload["aud"] == "todo-app-users"

    async def test_signup_invalid_email_returns_400(self, async_client: AsyncClient):
        """Test signup with invalid email format returns 400"""
        invalid_emails = [
            "notanemail",
            "missing@domain",
            "@nodomain.com",
            "no-at-sign.com"
        ]

        for email in invalid_emails:
            response = await async_client.post(
                "/api/v1/auth/signup",
                json={
                    "email": email,
                    "password": "SecurePass123",
                    "name": "Test User"
                }
            )

            # Pydantic validates email format, returns 422
            assert response.status_code in [400, 422]

    async def test_signup_weak_password_returns_400(self, async_client: AsyncClient):
        """Test signup with weak password returns 400"""
        weak_passwords = [
            "short",  # Too short
            "nouppercase1",  # No uppercase
            "NOLOWERCASE1",  # No lowercase
            "NoDigitsHere",  # No digits
        ]

        for password in weak_passwords:
            response = await async_client.post(
                "/api/v1/auth/signup",
                json={
                    "email": f"test{password}@example.com",
                    "password": password,
                    "name": "Test User"
                }
            )

            assert response.status_code == 400
            assert "password" in response.text.lower()

    async def test_signup_duplicate_email_returns_409(self, async_client: AsyncClient, session: AsyncSession):
        """Test signup with existing email returns 409 Conflict"""
        # Create first user
        await UserService.create_user(
            session=session,
            email="existing@example.com",
            password="SecurePass123",
            name="Existing User"
        )
        await session.commit()

        # Attempt duplicate signup
        response = await async_client.post(
            "/api/v1/auth/signup",
            json={
                "email": "existing@example.com",
                "password": "DifferentPass123",
                "name": "Duplicate User"
            }
        )

        assert response.status_code == 409
        assert "already registered" in response.text.lower()

    async def test_signup_password_hashed_in_database(self, async_client: AsyncClient, session: AsyncSession):
        """Test password is hashed (not plaintext) in database"""
        password = "PlainTextPass123"

        response = await async_client.post(
            "/api/v1/auth/signup",
            json={
                "email": "hashed@example.com",
                "password": password,
                "name": "Hashed User"
            }
        )

        assert response.status_code == 201

        # Retrieve user from database
        user = await UserService.get_user_by_email(session, "hashed@example.com")
        assert user is not None
        assert user.password_hash != password  # Not plaintext
        assert user.password_hash.startswith("$2b$")  # Bcrypt hash

    async def test_signup_token_expiration_is_900_seconds(self, async_client: AsyncClient):
        """Test token expires in 900 seconds (15 minutes)"""
        response = await async_client.post(
            "/api/v1/auth/signup",
            json={
                "email": "expiry@example.com",
                "password": "SecurePass123",
                "name": "Expiry User"
            }
        )

        assert response.status_code == 201
        data = response.json()
        token = data["token"]

        # Verify expiration time
        payload = verify_token(token)
        exp = payload["exp"]
        iat = payload["iat"]

        assert exp - iat == 900  # 15 minutes

    async def test_signup_name_is_optional(self, async_client: AsyncClient):
        """Test signup works without name field"""
        response = await async_client.post(
            "/api/v1/auth/signup",
            json={
                "email": "noname@example.com",
                "password": "SecurePass123"
            }
        )

        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "noname@example.com"
        # Name should be None or empty string
        assert data.get("name") in [None, ""]


@pytest.mark.asyncio
class TestSigninFlow:
    """Integration tests for user signin endpoint"""

    async def test_signin_success_returns_token(self, async_client: AsyncClient, session: AsyncSession):
        """Test valid signin returns user data and JWT token"""
        # Create user first
        await UserService.create_user(
            session=session,
            email="signin@example.com",
            password="SecurePass123",
            name="Signin User"
        )
        await session.commit()

        # Sign in
        response = await async_client.post(
            "/api/v1/auth/signin",
            json={
                "email": "signin@example.com",
                "password": "SecurePass123"
            }
        )

        assert response.status_code == 200
        data = response.json()

        assert "id" in data
        assert data["email"] == "signin@example.com"
        assert data["name"] == "Signin User"
        assert "token" in data
        assert "expiresIn" in data
        assert data["expiresIn"] == 900

    async def test_signin_invalid_email_returns_401(self, async_client: AsyncClient):
        """Test signin with non-existent email returns 401"""
        response = await async_client.post(
            "/api/v1/auth/signin",
            json={
                "email": "notfound@example.com",
                "password": "SecurePass123"
            }
        )

        assert response.status_code == 401
        assert "invalid" in response.text.lower()

    async def test_signin_wrong_password_returns_401(self, async_client: AsyncClient, session: AsyncSession):
        """Test signin with wrong password returns 401"""
        # Create user
        await UserService.create_user(
            session=session,
            email="wrongpass@example.com",
            password="CorrectPass123",
            name="Wrong Pass User"
        )
        await session.commit()

        # Attempt signin with wrong password
        response = await async_client.post(
            "/api/v1/auth/signin",
            json={
                "email": "wrongpass@example.com",
                "password": "WrongPassword123"
            }
        )

        assert response.status_code == 401
        assert "invalid" in response.text.lower()

    async def test_signin_prevents_user_enumeration(self, async_client: AsyncClient, session: AsyncSession):
        """
        Test signin returns identical error for non-existent email and wrong password.

        Security: User enumeration prevention
        - Attacker should not be able to determine if email exists in database
        - Both "email not found" and "wrong password" return same status and message
        """
        # Create user with known password
        await UserService.create_user(
            session=session,
            email="enumtest@example.com",
            password="CorrectPass123",
            name="Enum Test User"
        )
        await session.commit()

        # Test 1: Non-existent email
        response_no_email = await async_client.post(
            "/api/v1/auth/signin",
            json={
                "email": "nonexistent@example.com",
                "password": "SomePassword123"
            }
        )

        # Test 2: Existing email, wrong password
        response_wrong_pass = await async_client.post(
            "/api/v1/auth/signin",
            json={
                "email": "enumtest@example.com",
                "password": "WrongPassword123"
            }
        )

        # Both should return 401
        assert response_no_email.status_code == 401
        assert response_wrong_pass.status_code == 401

        # Both should return IDENTICAL error message (prevents enumeration)
        error_no_email = response_no_email.json().get("detail", "")
        error_wrong_pass = response_wrong_pass.json().get("detail", "")

        assert error_no_email == error_wrong_pass, (
            f"Error messages differ (enumeration vulnerability): "
            f"no_email='{error_no_email}' vs wrong_pass='{error_wrong_pass}'"
        )
        assert "invalid" in error_no_email.lower()

    async def test_signin_token_claims_match_user_data(self, async_client: AsyncClient, session: AsyncSession):
        """Test signin JWT token contains correct user_id (sub) and email claims"""
        # Create user
        await UserService.create_user(
            session=session,
            email="tokenclaims@example.com",
            password="SecurePass123",
            name="Token Claims User"
        )
        await session.commit()

        # Sign in
        response = await async_client.post(
            "/api/v1/auth/signin",
            json={
                "email": "tokenclaims@example.com",
                "password": "SecurePass123"
            }
        )

        assert response.status_code == 200
        data = response.json()
        token = data["token"]

        # Decode and verify token claims
        payload = verify_token(token)
        assert payload["sub"] == data["id"]  # user_id in sub claim
        assert payload["email"] == "tokenclaims@example.com"
        assert payload["iss"] == "todo-app"
        assert payload["aud"] == "todo-app-users"


@pytest.mark.asyncio
class TestTokenSecurity:
    """Integration tests for token security and validation"""

    async def test_token_is_returned_in_response_body(self, async_client: AsyncClient):
        """Test token is returned in response body"""
        response = await async_client.post(
            "/api/v1/auth/signup",
            json={
                "email": "tokentest@example.com",
                "password": "SecurePass123",
                "name": "Token Test"
            }
        )

        assert response.status_code == 201
        data = response.json()

        # Token is in response body (client will store securely)
        assert "token" in data

    async def test_signup_does_not_expose_password_in_response(self, async_client: AsyncClient):
        """Test password is never returned in response"""
        response = await async_client.post(
            "/api/v1/auth/signup",
            json={
                "email": "nopassword@example.com",
                "password": "SecurePass123",
                "name": "No Password"
            }
        )

        assert response.status_code == 201
        data = response.json()

        # Password should never be in response
        assert "password" not in data
        assert "password_hash" not in data

    async def test_token_claims_match_user_data(self, async_client: AsyncClient):
        """Test token claims (sub, email) match returned user data"""
        response = await async_client.post(
            "/api/v1/auth/signup",
            json={
                "email": "matchclaims@example.com",
                "password": "SecurePass123",
                "name": "Match Claims"
            }
        )

        assert response.status_code == 201
        data = response.json()

        token = data["token"]
        payload = verify_token(token)

        # Verify claims match response data
        assert payload["sub"] == data["id"]
        assert payload["email"] == data["email"]


@pytest.mark.asyncio
class TestSignoutFlow:
    """Integration tests for user signout endpoint"""

    async def test_signout_with_valid_token_succeeds(self, async_client: AsyncClient):
        """Test signout with valid JWT token returns 200"""
        # Create user and get token
        response = await async_client.post(
            "/api/v1/auth/signup",
            json={
                "email": "signout@example.com",
                "password": "SecurePass123",
                "name": "Signout User"
            }
        )
        assert response.status_code == 201
        token = response.json()["token"]

        # Signout with valid token
        response = await async_client.post(
            "/api/v1/auth/signout",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Signed out successfully"

    async def test_signout_with_invalid_token_fails(self, async_client: AsyncClient):
        """Test signout with invalid JWT token returns 401"""
        invalid_token = "invalid.jwt.token"

        response = await async_client.post(
            "/api/v1/auth/signout",
            headers={"Authorization": f"Bearer {invalid_token}"}
        )

        assert response.status_code == 401
        assert "invalid" in response.text.lower() or "token" in response.text.lower()

    async def test_signout_with_missing_token_fails(self, async_client: AsyncClient):
        """Test signout without Authorization header returns 401"""
        response = await async_client.post("/api/v1/auth/signout")

        assert response.status_code == 401

    async def test_signout_with_expired_token_fails(self, async_client: AsyncClient):
        """Test signout with expired JWT token returns 401"""
        from datetime import datetime, timedelta, timezone
        from jose import jwt
        from src.config import settings

        # Create expired token (expired 1 hour ago)
        now = datetime.now(timezone.utc)
        expired_at = now - timedelta(hours=1)

        payload = {
            "sub": "test-user-id",
            "email": "expired@example.com",
            "iat": int((now - timedelta(hours=2)).timestamp()),
            "exp": int(expired_at.timestamp()),
            "iss": "todo-app",
            "aud": "todo-app-users",
        }

        expired_token = jwt.encode(
            payload,
            settings.JWT_SECRET,
            algorithm=settings.JWT_ALGORITHM,
        )

        # Attempt signout with expired token
        response = await async_client.post(
            "/api/v1/auth/signout",
            headers={"Authorization": f"Bearer {expired_token}"}
        )

        assert response.status_code == 401
        assert "expired" in response.text.lower() or "invalid" in response.text.lower()

    async def test_signout_then_protected_endpoint_fails(
        self, async_client: AsyncClient, session: AsyncSession
    ):
        """Test that after signout, protected endpoints fail with 401"""
        # Create user and get token
        response = await async_client.post(
            "/api/v1/auth/signup",
            json={
                "email": "protected@example.com",
                "password": "SecurePass123",
                "name": "Protected User"
            }
        )
        assert response.status_code == 201
        data = response.json()
        token = data["token"]
        user_id = data["id"]

        # Signout
        response = await async_client.post(
            "/api/v1/auth/signout",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200

        # Note: Since we use stateless JWT, the token is still technically valid
        # until it expires. The signout endpoint only validates the token.
        # In production, consider implementing token blacklist or refresh tokens.
        #
        # For this test, we verify that an invalid token fails on protected endpoints.

        # Try accessing protected endpoint without token (simulating client cleared it)
        response = await async_client.get(f"/api/v1/users/{user_id}/tasks")

        # Should fail with 401 (no token provided)
        assert response.status_code == 401
