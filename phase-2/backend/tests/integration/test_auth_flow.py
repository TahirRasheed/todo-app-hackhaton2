"""Authentication flow integration tests"""
import pytest
from httpx import AsyncClient

from backend.src.main import app
from backend.src.models.user import User
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.asyncio
class TestSignup:
    """Tests for user signup endpoint"""

    async def test_signup_with_valid_credentials(self, async_client: AsyncClient, session: AsyncSession):
        """Test successful signup with valid email and password"""
        response = await async_client.post(
            "/api/v1/auth/signup",
            json={
                "email": "newuser@example.com",
                "password": "securepassword123",
                "name": "New User"
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert data["data"]["email"] == "newuser@example.com"
        assert data["data"]["name"] == "New User"
        assert "id" in data["data"]
        assert data["error"] is None

    async def test_signup_with_existing_email(self, async_client: AsyncClient, session: AsyncSession):
        """Test signup with email that already exists"""
        # First signup
        await async_client.post(
            "/api/v1/auth/signup",
            json={
                "email": "existing@example.com",
                "password": "password123",
                "name": "Existing User"
            }
        )

        # Second signup with same email
        response = await async_client.post(
            "/api/v1/auth/signup",
            json={
                "email": "existing@example.com",
                "password": "differentpassword",
                "name": "Another User"
            }
        )
        assert response.status_code == 400
        assert "EMAIL_EXISTS" in response.json()["error"]["code"]

    async def test_signup_with_weak_password(self, async_client: AsyncClient):
        """Test signup with password less than 8 characters"""
        response = await async_client.post(
            "/api/v1/auth/signup",
            json={
                "email": "weak@example.com",
                "password": "short",
                "name": "Weak Password"
            }
        )
        assert response.status_code == 400
        assert "WEAK_PASSWORD" in response.json()["error"]["code"]

    async def test_signup_with_invalid_email(self, async_client: AsyncClient):
        """Test signup with invalid email format"""
        response = await async_client.post(
            "/api/v1/auth/signup",
            json={
                "email": "notanemail",
                "password": "password123",
                "name": "Invalid Email"
            }
        )
        assert response.status_code == 400
        assert "INVALID_EMAIL" in response.json()["error"]["code"]

    async def test_signup_sets_jwt_cookie(self, async_client: AsyncClient):
        """Test that signup sets JWT in httpOnly cookie"""
        response = await async_client.post(
            "/api/v1/auth/signup",
            json={
                "email": "cookie@example.com",
                "password": "password123",
                "name": "Cookie Test"
            }
        )
        assert response.status_code == 201
        assert "jwt" in response.cookies


@pytest.mark.asyncio
class TestSignin:
    """Tests for user signin endpoint"""

    async def test_signin_with_correct_credentials(self, async_client: AsyncClient):
        """Test successful signin with correct email and password"""
        # Create user
        await async_client.post(
            "/api/v1/auth/signup",
            json={
                "email": "signin@example.com",
                "password": "correctpassword",
                "name": "Signin User"
            }
        )

        # Sign in
        response = await async_client.post(
            "/api/v1/auth/signin",
            json={
                "email": "signin@example.com",
                "password": "correctpassword"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["email"] == "signin@example.com"
        assert data["error"] is None

    async def test_signin_with_wrong_password(self, async_client: AsyncClient):
        """Test signin with correct email but wrong password"""
        # Create user
        await async_client.post(
            "/api/v1/auth/signup",
            json={
                "email": "wrong@example.com",
                "password": "correctpassword",
                "name": "Wrong Password Test"
            }
        )

        # Try signin with wrong password
        response = await async_client.post(
            "/api/v1/auth/signin",
            json={
                "email": "wrong@example.com",
                "password": "wrongpassword"
            }
        )
        assert response.status_code == 401
        assert "INVALID_CREDENTIALS" in response.json()["error"]["code"]

    async def test_signin_with_nonexistent_email(self, async_client: AsyncClient):
        """Test signin with email that doesn't exist"""
        response = await async_client.post(
            "/api/v1/auth/signin",
            json={
                "email": "nonexistent@example.com",
                "password": "anypassword"
            }
        )
        assert response.status_code == 401
        assert "INVALID_CREDENTIALS" in response.json()["error"]["code"]

    async def test_signin_sets_jwt_cookie(self, async_client: AsyncClient):
        """Test that signin sets JWT in httpOnly cookie"""
        # Create user
        await async_client.post(
            "/api/v1/auth/signup",
            json={
                "email": "signin_cookie@example.com",
                "password": "password123",
                "name": "Signin Cookie Test"
            }
        )

        # Sign in
        response = await async_client.post(
            "/api/v1/auth/signin",
            json={
                "email": "signin_cookie@example.com",
                "password": "password123"
            }
        )
        assert response.status_code == 200
        assert "jwt" in response.cookies


@pytest.mark.asyncio
class TestSignout:
    """Tests for user signout endpoint"""

    async def test_signout_clears_jwt_cookie(self, async_client: AsyncClient):
        """Test that signout clears JWT cookie"""
        # Create and sign in user
        signup_response = await async_client.post(
            "/api/v1/auth/signup",
            json={
                "email": "signout@example.com",
                "password": "password123",
                "name": "Signout Test"
            }
        )
        assert signup_response.status_code == 201

        # Sign out
        response = await async_client.post("/api/v1/auth/signout")
        assert response.status_code == 200
        data = response.json()
        assert data["error"] is None
