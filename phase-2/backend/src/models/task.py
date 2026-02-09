"""Task Model"""
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from sqlmodel import SQLModel, Field, Relationship


class Task(SQLModel, table=True):
    """User task model"""

    __tablename__ = "tasks"

    id: Optional[UUID] = Field(
        default_factory=uuid4,
        primary_key=True,
        description="Unique task identifier"
    )
    user_id: UUID = Field(
        foreign_key="users.id",
        index=True,
        description="Owner of this task"
    )
    title: str = Field(
        max_length=500,
        description="Task title (required)"
    )
    description: Optional[str] = Field(
        default=None,
        max_length=5000,
        description="Task description (optional)"
    )
    completed: bool = Field(
        default=False,
        description="Completion status"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        index=True,
        description="Task creation timestamp"
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Last modification timestamp"
    )

    # Relationships
    user: Optional["User"] = Relationship(back_populates="tasks")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "660e8400-e29b-41d4-a716-446655440001",
                "user_id": "550e8400-e29b-41d4-a716-446655440000",
                "title": "Buy groceries",
                "description": "Milk, eggs, bread",
                "completed": False,
                "created_at": "2026-02-09T10:30:00Z",
                "updated_at": "2026-02-09T10:30:00Z"
            }
        }
