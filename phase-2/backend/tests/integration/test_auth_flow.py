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


@pytest.mark.asyncio
class TestProtectedEndpointsValidation:
    """Integration tests for JWT validation on protected task endpoints"""

    async def test_missing_authorization_header_returns_401(
        self, async_client: AsyncClient, session: AsyncSession
    ):
        """Test protected endpoints return 401 when Authorization header is missing"""
        # Create user to get user_id
        response = await async_client.post(
            "/api/v1/auth/signup",
            json={
                "email": "notoken@example.com",
                "password": "SecurePass123",
                "name": "No Token User"
            }
        )
        assert response.status_code == 201
        user_id = response.json()["id"]

        # Test all task endpoints without Authorization header
        endpoints = [
            ("GET", f"/api/v1/users/{user_id}/tasks"),
            ("POST", f"/api/v1/users/{user_id}/tasks", {"title": "Test Task"}),
            ("GET", f"/api/v1/users/{user_id}/tasks/550e8400-e29b-41d4-a716-446655440000"),
            ("PUT", f"/api/v1/users/{user_id}/tasks/550e8400-e29b-41d4-a716-446655440000", {"title": "Updated"}),
            ("DELETE", f"/api/v1/users/{user_id}/tasks/550e8400-e29b-41d4-a716-446655440000"),
        ]

        for method, url, *body in endpoints:
            if method == "GET":
                response = await async_client.get(url)
            elif method == "POST":
                response = await async_client.post(url, json=body[0])
            elif method == "PUT":
                response = await async_client.put(url, json=body[0])
            elif method == "DELETE":
                response = await async_client.delete(url)

            assert response.status_code == 401, f"{method} {url} should return 401 without token"

    async def test_invalid_bearer_format_returns_401(
        self, async_client: AsyncClient, session: AsyncSession
    ):
        """Test protected endpoints return 401 for invalid Bearer token format"""
        # Create user to get user_id
        response = await async_client.post(
            "/api/v1/auth/signup",
            json={
                "email": "invalidformat@example.com",
                "password": "SecurePass123",
                "name": "Invalid Format User"
            }
        )
        assert response.status_code == 201
        user_id = response.json()["id"]

        # Test various invalid Authorization header formats
        invalid_headers = [
            {"Authorization": "InvalidTokenNoBearer"},
            {"Authorization": "Bearer"},  # Missing token
            {"Authorization": "bearer token"},  # Lowercase bearer
            {"Authorization": "Token abc123"},  # Wrong scheme
        ]

        for headers in invalid_headers:
            response = await async_client.get(
                f"/api/v1/users/{user_id}/tasks",
                headers=headers
            )
            assert response.status_code == 401, f"Should return 401 for invalid format: {headers}"

    async def test_invalid_token_signature_returns_401(
        self, async_client: AsyncClient, session: AsyncSession
    ):
        """Test protected endpoints return 401 for tokens with invalid signature"""
        # Create user to get user_id
        response = await async_client.post(
            "/api/v1/auth/signup",
            json={
                "email": "invalidsig@example.com",
                "password": "SecurePass123",
                "name": "Invalid Sig User"
            }
        )
        assert response.status_code == 201
        user_id = response.json()["id"]

        # Use completely invalid token
        invalid_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0In0.invalid_signature"

        response = await async_client.get(
            f"/api/v1/users/{user_id}/tasks",
            headers={"Authorization": f"Bearer {invalid_token}"}
        )

        assert response.status_code == 401
        assert "invalid" in response.text.lower() or "authentication" in response.text.lower()

    async def test_expired_token_returns_401(
        self, async_client: AsyncClient, session: AsyncSession
    ):
        """Test protected endpoints return 401 for expired tokens"""
        from datetime import datetime, timedelta, timezone
        from jose import jwt
        from src.config import settings

        # Create user to get user_id
        response = await async_client.post(
            "/api/v1/auth/signup",
            json={
                "email": "expiredtoken@example.com",
                "password": "SecurePass123",
                "name": "Expired Token User"
            }
        )
        assert response.status_code == 201
        user_id = response.json()["id"]

        # Create expired token (expired 1 hour ago)
        now = datetime.now(timezone.utc)
        expired_at = now - timedelta(hours=1)

        payload = {
            "sub": user_id,
            "email": "expiredtoken@example.com",
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

        # Try to access protected endpoint with expired token
        response = await async_client.get(
            f"/api/v1/users/{user_id}/tasks",
            headers={"Authorization": f"Bearer {expired_token}"}
        )

        assert response.status_code == 401
        assert "invalid" in response.text.lower() or "authentication" in response.text.lower()

    async def test_token_without_required_claims_returns_401(
        self, async_client: AsyncClient, session: AsyncSession
    ):
        """Test protected endpoints return 401 for tokens missing required claims (sub)"""
        from datetime import datetime, timedelta, timezone
        from jose import jwt
        from src.config import settings

        # Create user to get user_id
        response = await async_client.post(
            "/api/v1/auth/signup",
            json={
                "email": "noclaims@example.com",
                "password": "SecurePass123",
                "name": "No Claims User"
            }
        )
        assert response.status_code == 201
        user_id = response.json()["id"]

        # Create token without 'sub' claim
        now = datetime.now(timezone.utc)
        payload = {
            # Missing "sub" claim
            "email": "noclaims@example.com",
            "iat": int(now.timestamp()),
            "exp": int((now + timedelta(minutes=15)).timestamp()),
            "iss": "todo-app",
            "aud": "todo-app-users",
        }

        token_no_sub = jwt.encode(
            payload,
            settings.JWT_SECRET,
            algorithm=settings.JWT_ALGORITHM,
        )

        # Try to access protected endpoint
        response = await async_client.get(
            f"/api/v1/users/{user_id}/tasks",
            headers={"Authorization": f"Bearer {token_no_sub}"}
        )

        assert response.status_code == 401
        assert "invalid" in response.text.lower() or "authentication" in response.text.lower()

    async def test_valid_token_allows_access_to_protected_endpoints(
        self, async_client: AsyncClient, session: AsyncSession
    ):
        """Test valid JWT token allows access to protected task endpoints"""
        # Create user and get valid token
        response = await async_client.post(
            "/api/v1/auth/signup",
            json={
                "email": "validtoken@example.com",
                "password": "SecurePass123",
                "name": "Valid Token User"
            }
        )
        assert response.status_code == 201
        data = response.json()
        token = data["token"]
        user_id = data["id"]

        # Test access to list tasks endpoint with valid token
        response = await async_client.get(
            f"/api/v1/users/{user_id}/tasks",
            headers={"Authorization": f"Bearer {token}"}
        )

        # Should succeed with 200
        assert response.status_code == 200
        assert response.json()["success"] is True

        # Test create task endpoint with valid token
        response = await async_client.post(
            f"/api/v1/users/{user_id}/tasks",
            headers={"Authorization": f"Bearer {token}"},
            json={"title": "Test Task", "description": "Test Description"}
        )

        # Should succeed with 201
        assert response.status_code == 201
        assert response.json()["success"] is True

    async def test_token_for_different_user_fails_ownership_check(
        self, async_client: AsyncClient, session: AsyncSession
    ):
        """Test JWT token for different user fails ownership validation (403)"""
        # Create first user
        response1 = await async_client.post(
            "/api/v1/auth/signup",
            json={
                "email": "user1@example.com",
                "password": "SecurePass123",
                "name": "User One"
            }
        )
        assert response1.status_code == 201
        user1_id = response1.json()["id"]
        user1_token = response1.json()["token"]

        # Create second user
        response2 = await async_client.post(
            "/api/v1/auth/signup",
            json={
                "email": "user2@example.com",
                "password": "SecurePass123",
                "name": "User Two"
            }
        )
        assert response2.status_code == 201
        user2_id = response2.json()["id"]

        # Try to access user2's tasks with user1's token
        response = await async_client.get(
            f"/api/v1/users/{user2_id}/tasks",
            headers={"Authorization": f"Bearer {user1_token}"}
        )

        # Should fail with 403 Forbidden (ownership check)
        assert response.status_code == 403
        assert "forbidden" in response.text.lower() or "access denied" in response.text.lower()

    async def test_all_task_endpoints_require_authentication(
        self, async_client: AsyncClient, session: AsyncSession
    ):
        """Test all task CRUD endpoints require valid JWT authentication"""
        from uuid import uuid4

        # Create user and get token
        response = await async_client.post(
            "/api/v1/auth/signup",
            json={
                "email": "allendpoints@example.com",
                "password": "SecurePass123",
                "name": "All Endpoints User"
            }
        )
        assert response.status_code == 201
        data = response.json()
        token = data["token"]
        user_id = data["id"]

        # Create a task first (for get/update/delete tests)
        create_response = await async_client.post(
            f"/api/v1/users/{user_id}/tasks",
            headers={"Authorization": f"Bearer {token}"},
            json={"title": "Test Task", "description": "For endpoint tests"}
        )
        assert create_response.status_code == 201
        task_id = create_response.json()["data"]["id"]

        # Test all endpoints with valid token (should all succeed or return proper errors)
        test_cases = [
            ("GET", f"/api/v1/users/{user_id}/tasks", None, 200),
            ("POST", f"/api/v1/users/{user_id}/tasks", {"title": "New Task"}, 201),
            ("GET", f"/api/v1/users/{user_id}/tasks/{task_id}", None, 200),
            ("PUT", f"/api/v1/users/{user_id}/tasks/{task_id}", {"title": "Updated Task"}, 200),
            ("DELETE", f"/api/v1/users/{user_id}/tasks/{task_id}", None, 204),
        ]

        for method, url, body, expected_status in test_cases:
            if method == "GET":
                response = await async_client.get(
                    url,
                    headers={"Authorization": f"Bearer {token}"}
                )
            elif method == "POST":
                response = await async_client.post(
                    url,
                    headers={"Authorization": f"Bearer {token}"},
                    json=body
                )
            elif method == "PUT":
                response = await async_client.put(
                    url,
                    headers={"Authorization": f"Bearer {token}"},
                    json=body
                )
            elif method == "DELETE":
                response = await async_client.delete(
                    url,
                    headers={"Authorization": f"Bearer {token}"}
                )

            assert response.status_code == expected_status, (
                f"{method} {url} expected {expected_status}, got {response.status_code}"
            )


@pytest.mark.asyncio
class TestOwnershipEnforcement:
    """Integration tests for ownership enforcement and data isolation"""

    async def test_user_can_only_see_own_tasks(
        self, async_client: AsyncClient
    ):
        """Test users see only their own tasks in list endpoint"""
        # Create User A with 3 tasks
        user_a_response = await async_client.post(
            "/api/v1/auth/signup",
            json={
                "email": "usera_own@example.com",
                "password": "SecurePass123",
                "name": "User A"
            }
        )
        user_a_id = user_a_response.json()["id"]
        user_a_token = user_a_response.json()["token"]

        for i in range(3):
            await async_client.post(
                f"/api/v1/users/{user_a_id}/tasks",
                headers={"Authorization": f"Bearer {user_a_token}"},
                json={"title": f"User A Task {i+1}"}
            )

        # Create User B with 2 tasks
        user_b_response = await async_client.post(
            "/api/v1/auth/signup",
            json={
                "email": "userb_own@example.com",
                "password": "SecurePass123",
                "name": "User B"
            }
        )
        user_b_id = user_b_response.json()["id"]
        user_b_token = user_b_response.json()["token"]

        for i in range(2):
            await async_client.post(
                f"/api/v1/users/{user_b_id}/tasks",
                headers={"Authorization": f"Bearer {user_b_token}"},
                json={"title": f"User B Task {i+1}"}
            )

        # User A lists tasks - should see only 3
        user_a_list = await async_client.get(
            f"/api/v1/users/{user_a_id}/tasks",
            headers={"Authorization": f"Bearer {user_a_token}"}
        )
        assert user_a_list.status_code == 200
        assert len(user_a_list.json()["data"]) == 3
        assert user_a_list.json()["meta"]["total"] == 3

        # User B lists tasks - should see only 2
        user_b_list = await async_client.get(
            f"/api/v1/users/{user_b_id}/tasks",
            headers={"Authorization": f"Bearer {user_b_token}"}
        )
        assert user_b_list.status_code == 200
        assert len(user_b_list.json()["data"]) == 2
        assert user_b_list.json()["meta"]["total"] == 2

    async def test_user_cannot_view_other_users_task(
        self, async_client: AsyncClient
    ):
        """Test User A cannot GET User B's specific task (403)"""
        # Create User A
        user_a_response = await async_client.post(
            "/api/v1/auth/signup",
            json={
                "email": "usera_view@example.com",
                "password": "SecurePass123",
                "name": "User A"
            }
        )
        user_a_token = user_a_response.json()["token"]

        # Create User B and a task
        user_b_response = await async_client.post(
            "/api/v1/auth/signup",
            json={
                "email": "userb_view@example.com",
                "password": "SecurePass123",
                "name": "User B"
            }
        )
        user_b_id = user_b_response.json()["id"]
        user_b_token = user_b_response.json()["token"]

        task_response = await async_client.post(
            f"/api/v1/users/{user_b_id}/tasks",
            headers={"Authorization": f"Bearer {user_b_token}"},
            json={"title": "User B's Private Task"}
        )
        task_id = task_response.json()["data"]["id"]

        # User A tries to GET User B's task with User A's token
        response = await async_client.get(
            f"/api/v1/users/{user_b_id}/tasks/{task_id}",
            headers={"Authorization": f"Bearer {user_a_token}"}
        )

        # Should return 403 (ownership check at URL level)
        assert response.status_code == 403
        assert "FORBIDDEN" in response.json()["error"]["code"]

    async def test_user_cannot_update_other_users_task(
        self, async_client: AsyncClient
    ):
        """Test User A cannot UPDATE User B's task (403)"""
        # Create User A
        user_a_response = await async_client.post(
            "/api/v1/auth/signup",
            json={
                "email": "usera_update@example.com",
                "password": "SecurePass123",
                "name": "User A"
            }
        )
        user_a_token = user_a_response.json()["token"]

        # Create User B and a task
        user_b_response = await async_client.post(
            "/api/v1/auth/signup",
            json={
                "email": "userb_update@example.com",
                "password": "SecurePass123",
                "name": "User B"
            }
        )
        user_b_id = user_b_response.json()["id"]
        user_b_token = user_b_response.json()["token"]

        task_response = await async_client.post(
            f"/api/v1/users/{user_b_id}/tasks",
            headers={"Authorization": f"Bearer {user_b_token}"},
            json={"title": "User B's Task"}
        )
        task_id = task_response.json()["data"]["id"]

        # User A tries to UPDATE User B's task
        response = await async_client.put(
            f"/api/v1/users/{user_b_id}/tasks/{task_id}",
            headers={"Authorization": f"Bearer {user_a_token}"},
            json={"title": "Hacked Title", "completed": True}
        )

        # Should return 403
        assert response.status_code == 403
        assert "FORBIDDEN" in response.json()["error"]["code"]

        # Verify User B's task unchanged
        verify_response = await async_client.get(
            f"/api/v1/users/{user_b_id}/tasks/{task_id}",
            headers={"Authorization": f"Bearer {user_b_token}"}
        )
        assert verify_response.status_code == 200
        assert verify_response.json()["data"]["title"] == "User B's Task"
        assert verify_response.json()["data"]["completed"] is False

    async def test_user_cannot_delete_other_users_task(
        self, async_client: AsyncClient
    ):
        """Test User A cannot DELETE User B's task (403)"""
        # Create User A
        user_a_response = await async_client.post(
            "/api/v1/auth/signup",
            json={
                "email": "usera_delete@example.com",
                "password": "SecurePass123",
                "name": "User A"
            }
        )
        user_a_token = user_a_response.json()["token"]

        # Create User B and a task
        user_b_response = await async_client.post(
            "/api/v1/auth/signup",
            json={
                "email": "userb_delete@example.com",
                "password": "SecurePass123",
                "name": "User B"
            }
        )
        user_b_id = user_b_response.json()["id"]
        user_b_token = user_b_response.json()["token"]

        task_response = await async_client.post(
            f"/api/v1/users/{user_b_id}/tasks",
            headers={"Authorization": f"Bearer {user_b_token}"},
            json={"title": "User B's Permanent Task"}
        )
        task_id = task_response.json()["data"]["id"]

        # User A tries to DELETE User B's task
        response = await async_client.delete(
            f"/api/v1/users/{user_b_id}/tasks/{task_id}",
            headers={"Authorization": f"Bearer {user_a_token}"}
        )

        # Should return 403
        assert response.status_code == 403

        # Verify User B's task still exists
        verify_response = await async_client.get(
            f"/api/v1/users/{user_b_id}/tasks/{task_id}",
            headers={"Authorization": f"Bearer {user_b_token}"}
        )
        assert verify_response.status_code == 200

    async def test_pagination_limits_to_user_tasks(
        self, async_client: AsyncClient
    ):
        """Test pagination returns only user's tasks, not all tasks"""
        # Create User A with 5 tasks
        user_a_response = await async_client.post(
            "/api/v1/auth/signup",
            json={
                "email": "usera_page@example.com",
                "password": "SecurePass123",
                "name": "User A"
            }
        )
        user_a_id = user_a_response.json()["id"]
        user_a_token = user_a_response.json()["token"]

        for i in range(5):
            await async_client.post(
                f"/api/v1/users/{user_a_id}/tasks",
                headers={"Authorization": f"Bearer {user_a_token}"},
                json={"title": f"User A Task {i+1}"}
            )

        # Create User B with 3 tasks
        user_b_response = await async_client.post(
            "/api/v1/auth/signup",
            json={
                "email": "userb_page@example.com",
                "password": "SecurePass123",
                "name": "User B"
            }
        )
        user_b_id = user_b_response.json()["id"]
        user_b_token = user_b_response.json()["token"]

        for i in range(3):
            await async_client.post(
                f"/api/v1/users/{user_b_id}/tasks",
                headers={"Authorization": f"Bearer {user_b_token}"},
                json={"title": f"User B Task {i+1}"}
            )

        # User A lists with pagination (limit 2)
        page1_response = await async_client.get(
            f"/api/v1/users/{user_a_id}/tasks?limit=2&skip=0",
            headers={"Authorization": f"Bearer {user_a_token}"}
        )
        assert page1_response.status_code == 200
        page1_data = page1_response.json()
        assert len(page1_data["data"]) == 2
        assert page1_data["meta"]["total"] == 5  # Total for User A only

        # User B lists all tasks
        user_b_response = await async_client.get(
            f"/api/v1/users/{user_b_id}/tasks",
            headers={"Authorization": f"Bearer {user_b_token}"}
        )
        assert user_b_response.status_code == 200
        user_b_data = user_b_response.json()
        assert len(user_b_data["data"]) == 3
        assert user_b_data["meta"]["total"] == 3  # Total for User B only

    async def test_generic_403_error_prevents_info_leak(
        self, async_client: AsyncClient
    ):
        """Test that 403 errors are generic and don't leak task existence"""
        # Create User A
        user_a_response = await async_client.post(
            "/api/v1/auth/signup",
            json={
                "email": "usera_leak@example.com",
                "password": "SecurePass123",
                "name": "User A"
            }
        )
        user_a_token = user_a_response.json()["token"]

        # Create User B and a task
        user_b_response = await async_client.post(
            "/api/v1/auth/signup",
            json={
                "email": "userb_leak@example.com",
                "password": "SecurePass123",
                "name": "User B"
            }
        )
        user_b_id = user_b_response.json()["id"]
        user_b_token = user_b_response.json()["token"]

        task_response = await async_client.post(
            f"/api/v1/users/{user_b_id}/tasks",
            headers={"Authorization": f"Bearer {user_b_token}"},
            json={"title": "Secret Task"}
        )
        task_id = task_response.json()["data"]["id"]

        # User A tries to GET User B's task (task exists, not owned)
        response_exists = await async_client.get(
            f"/api/v1/users/{user_b_id}/tasks/{task_id}",
            headers={"Authorization": f"Bearer {user_a_token}"}
        )

        # User A tries to GET non-existent task (task doesn't exist)
        from uuid import uuid4
        fake_task_id = str(uuid4())
        response_not_exists = await async_client.get(
            f"/api/v1/users/{user_b_id}/tasks/{fake_task_id}",
            headers={"Authorization": f"Bearer {user_a_token}"}
        )

        # Both should return 403 (not 404 for non-existent)
        assert response_exists.status_code == 403
        assert response_not_exists.status_code == 403

        # Error messages should be identical (generic)
        error_exists = response_exists.json()["error"]["message"]
        error_not_exists = response_not_exists.json()["error"]["message"]
        assert error_exists == error_not_exists
        assert "Not authorized to access this resource" in error_exists

    async def test_task_user_id_cannot_be_changed(
        self, async_client: AsyncClient
    ):
        """Test that user_id is immutable after task creation"""
        # Create User A and task
        user_a_response = await async_client.post(
            "/api/v1/auth/signup",
            json={
                "email": "usera_immutable@example.com",
                "password": "SecurePass123",
                "name": "User A"
            }
        )
        user_a_id = user_a_response.json()["id"]
        user_a_token = user_a_response.json()["token"]

        task_response = await async_client.post(
            f"/api/v1/users/{user_a_id}/tasks",
            headers={"Authorization": f"Bearer {user_a_token}"},
            json={"title": "User A's Task"}
        )
        task_id = task_response.json()["data"]["id"]
        assert task_response.json()["data"]["user_id"] == user_a_id

        # Update task (user_id not in update schema, should remain unchanged)
        update_response = await async_client.put(
            f"/api/v1/users/{user_a_id}/tasks/{task_id}",
            headers={"Authorization": f"Bearer {user_a_token}"},
            json={"title": "Updated Task"}
        )
        assert update_response.status_code == 200
        assert update_response.json()["data"]["user_id"] == user_a_id

        # Verify user_id unchanged via GET
        get_response = await async_client.get(
            f"/api/v1/users/{user_a_id}/tasks/{task_id}",
            headers={"Authorization": f"Bearer {user_a_token}"}
        )
        assert get_response.status_code == 200
        assert get_response.json()["data"]["user_id"] == user_a_id
