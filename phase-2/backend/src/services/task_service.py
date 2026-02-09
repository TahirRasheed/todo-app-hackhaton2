"""Task service for task management"""
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from backend.src.models.task import Task
from backend.src.models.user import User


class TaskService:
    """Service for task operations (create, list, retrieve)"""

    @staticmethod
    async def create_task(
        session: AsyncSession, user_id: UUID, title: str, description: str | None = None
    ) -> Task:
        """
        Create a new task

        Args:
            session: Database session
            user_id: UUID of the task owner
            title: Task title (required, max 500 chars)
            description: Task description (optional, max 5000 chars)

        Returns:
            Created Task object

        Raises:
            ValueError: If validation fails (title required, max lengths exceeded)
        """
        # Validate title
        if not title or len(title.strip()) == 0:
            raise ValueError("Title is required")
        if len(title) > 500:
            raise ValueError("Title must not exceed 500 characters")

        # Validate description
        if description and len(description) > 5000:
            raise ValueError("Description must not exceed 5000 characters")

        # Create task
        task = Task(
            user_id=user_id,
            title=title.strip(),
            description=description.strip() if description else None,
            completed=False,
        )
        session.add(task)
        await session.commit()
        await session.refresh(task)
        return task

    @staticmethod
    async def list_tasks_for_user(
        session: AsyncSession, user_id: UUID, skip: int = 0, limit: int = 20
    ) -> list[Task]:
        """
        Retrieve paginated list of tasks for a user

        Args:
            session: Database session
            user_id: UUID of the user
            skip: Number of tasks to skip (for pagination)
            limit: Maximum number of tasks to return (default 20, max 100)

        Returns:
            List of Task objects ordered by created_at DESC
        """
        # Clamp limit to 100
        limit = min(limit, 100)

        result = await session.execute(
            select(Task)
            .where(Task.user_id == user_id)
            .order_by(desc(Task.created_at))
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    @staticmethod
    async def get_task(session: AsyncSession, task_id: UUID, user_id: UUID) -> Task:
        """
        Retrieve a single task by ID with ownership verification

        Args:
            session: Database session
            task_id: UUID of the task
            user_id: UUID of the user (for ownership verification)

        Returns:
            Task object

        Raises:
            ValueError: If task not found or user_id doesn't match
        """
        result = await session.execute(
            select(Task).where((Task.id == task_id) & (Task.user_id == user_id))
        )
        task = result.scalars().first()

        if not task:
            raise ValueError("Task not found")

        return task

    @staticmethod
    async def get_task_count(session: AsyncSession, user_id: UUID) -> int:
        """
        Get total count of tasks for a user

        Args:
            session: Database session
            user_id: UUID of the user

        Returns:
            Count of tasks owned by user
        """
        result = await session.execute(
            select(Task).where(Task.user_id == user_id)
        )
        return len(result.scalars().all())

    @staticmethod
    async def update_task(
        session: AsyncSession,
        task_id: UUID,
        user_id: UUID,
        title: str | None = None,
        description: str | None = None,
        completed: bool | None = None,
    ) -> Task:
        """
        Update a task with new values

        Args:
            session: Database session
            task_id: UUID of the task
            user_id: UUID of the user (for ownership verification)
            title: New title (optional, max 500 chars)
            description: New description (optional, max 5000 chars)
            completed: New completion status (optional)

        Returns:
            Updated Task object

        Raises:
            ValueError: If task not found or user_id doesn't match
        """
        # Retrieve and verify ownership
        task = await TaskService.get_task(session, task_id, user_id)
        if not task:
            raise ValueError("Task not found")

        # Validate and update fields
        if title is not None:
            if not title or len(title.strip()) == 0:
                raise ValueError("Title cannot be empty")
            if len(title) > 500:
                raise ValueError("Title must not exceed 500 characters")
            task.title = title.strip()

        if description is not None:
            if len(description) > 5000:
                raise ValueError("Description must not exceed 5000 characters")
            task.description = description.strip() if description else None

        if completed is not None:
            task.completed = completed

        # Save changes
        await session.commit()
        await session.refresh(task)
        return task

    @staticmethod
    async def delete_task(session: AsyncSession, task_id: UUID, user_id: UUID) -> None:
        """
        Delete a task

        Args:
            session: Database session
            task_id: UUID of the task
            user_id: UUID of the user (for ownership verification)

        Raises:
            ValueError: If task not found or user_id doesn't match
        """
        # Retrieve and verify ownership
        task = await TaskService.get_task(session, task_id, user_id)
        if not task:
            raise ValueError("Task not found")

        # Delete task
        await session.delete(task)
        await session.commit()
