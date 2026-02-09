"""User Request/Response Schemas

Pydantic models for user authentication and API responses.
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class UserSignup(BaseModel):
    """User signup request model."""

    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., description="Password (min 8 chars, uppercase, lowercase, digit)")
    name: Optional[str] = Field(default=None, description="User display name")

    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "SecurePass123",
                "name": "John Doe",
            }
        }


class UserSignin(BaseModel):
    """User signin request model."""

    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., description="Password")

    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "SecurePass123",
            }
        }


class UserResponse(BaseModel):
    """User data response model (no password)."""

    id: str = Field(..., description="User UUID")
    email: str = Field(..., description="User email")
    name: Optional[str] = Field(default=None, description="User display name")
    created_at: datetime = Field(..., description="Account creation timestamp")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "email": "user@example.com",
                "name": "John Doe",
                "created_at": "2026-02-09T10:30:00Z",
            }
        }


class UserTokenResponse(BaseModel):
    """User authentication response with JWT token."""

    id: str = Field(..., description="User UUID")
    email: str = Field(..., description="User email")
    name: Optional[str] = Field(default=None, description="User display name")
    token: str = Field(..., description="JWT Bearer token")
    expiresIn: int = Field(..., description="Token expiration time in seconds")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "email": "user@example.com",
                "name": "John Doe",
                "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "expiresIn": 900,
            }
        }
