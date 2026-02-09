"""User Model"""
from datetime import datetime
from typing import List, Optional
from uuid import UUID, uuid4

from sqlmodel import SQLModel, Field, Relationship


class User(SQLModel, table=True):
    """User account model"""

    __tablename__ = "users"

    id: Optional[UUID] = Field(
        default_factory=uuid4,
        primary_key=True,
        description="Unique user identifier"
    )
    email: str = Field(
        unique=True,
        index=True,
        description="User email (login identifier)"
    )
    name: Optional[str] = Field(
        default=None,
        description="User display name"
    )
    password_hash: str = Field(
        description="Bcrypt hashed password"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Account creation timestamp"
    )

    # Relationships
    tasks: List["Task"] = Relationship(back_populates="user")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "email": "user@example.com",
                "name": "John Doe",
                "created_at": "2026-02-09T10:30:45Z"
            }
        }
