"""Task endpoints (create, list, retrieve, update, delete)"""
from uuid import UUID
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from backend.src.db.session import get_session
from backend.src.models.user import User
from backend.src.schemas.task import TaskCreate, TaskUpdate, TaskResponse
from backend.src.services.task_service import TaskService
from backend.src.api.deps import get_current_user
from backend.src.utils.response import APIResponse


router = APIRouter(prefix="/users", tags=["tasks"])


@router.post("/{user_id}/tasks", status_code=201, response_model=APIResponse)
async def create_task(
    user_id: UUID,
    task_data: TaskCreate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """
    Create a new task for a user

    Args:
        user_id: UUID of the user
        task_data: TaskCreate with title and description
        current_user: Authenticated user (dependency injection)
        session: Database session

    Returns:
        APIResponse with TaskResponse data

    Raises:
        HTTPException 403: If current_user.id != user_id
        HTTPException 400: If validation fails
    """
    # Verify user_id matches current user
    if current_user.id != user_id:
        raise HTTPException(
            status_code=403,
            detail=APIResponse.error("FORBIDDEN", "Not authorized to access this resource").dict(),
        )

    # Create task
    try:
        task = await TaskService.create_task(
            session, user_id, task_data.title, task_data.description
        )
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=APIResponse.error("INVALID_TASK", str(e)).dict(),
        )

    task_response = TaskResponse.from_attributes(task)
    return APIResponse.success(task_response.dict())


@router.get("/{user_id}/tasks", response_model=APIResponse)
async def list_tasks(
    user_id: UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """
    List all tasks for a user (paginated)

    Args:
        user_id: UUID of the user
        skip: Number of tasks to skip (for pagination)
        limit: Maximum number of tasks to return (1-100, default 20)
        current_user: Authenticated user (dependency injection)
        session: Database session

    Returns:
        APIResponse with list of TaskResponse objects and pagination meta

    Raises:
        HTTPException 403: If current_user.id != user_id
    """
    # Verify user_id matches current user
    if current_user.id != user_id:
        raise HTTPException(
            status_code=403,
            detail=APIResponse.error("FORBIDDEN", "Not authorized to access this resource").dict(),
        )

    # Retrieve tasks
    tasks = await TaskService.list_tasks_for_user(session, user_id, skip, limit)
    task_responses = [TaskResponse.from_attributes(t).dict() for t in tasks]

    # Get total count for pagination meta
    total = await TaskService.get_task_count(session, user_id)

    response = APIResponse.success(task_responses)
    # Add pagination info to meta
    response.meta["total"] = total
    response.meta["skip"] = skip
    response.meta["limit"] = limit
    response.meta["returned"] = len(task_responses)

    return response


@router.get("/{user_id}/tasks/{task_id}", response_model=APIResponse)
async def get_task(
    user_id: UUID,
    task_id: UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """
    Retrieve a single task by ID

    Args:
        user_id: UUID of the user
        task_id: UUID of the task
        current_user: Authenticated user (dependency injection)
        session: Database session

    Returns:
        APIResponse with TaskResponse data

    Raises:
        HTTPException 403: If current_user.id != user_id or task not owned

    Security Note:
        Returns 403 for both "task not found" and "not owned by user" to prevent
        information leakage about task existence.
    """
    # Verify user_id matches current user
    if current_user.id != user_id:
        raise HTTPException(
            status_code=403,
            detail=APIResponse.error("FORBIDDEN", "Not authorized to access this resource").dict(),
        )

    # Retrieve task with ownership verification
    try:
        task = await TaskService.get_task(session, task_id, user_id)
    except ValueError:
        # Return 403 instead of 404 to prevent leaking task existence
        raise HTTPException(
            status_code=403,
            detail=APIResponse.error("FORBIDDEN", "Not authorized to access this resource").dict(),
        )

    task_response = TaskResponse.from_attributes(task)
    return APIResponse.success(task_response.dict())


@router.put("/{user_id}/tasks/{task_id}", response_model=APIResponse)
async def update_task(
    user_id: UUID,
    task_id: UUID,
    task_data: TaskUpdate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """
    Update a task

    Args:
        user_id: UUID of the user
        task_id: UUID of the task
        task_data: TaskUpdate with optional title, description, completed
        current_user: Authenticated user (dependency injection)
        session: Database session

    Returns:
        APIResponse with updated TaskResponse

    Raises:
        HTTPException 403: If current_user.id != user_id or task not owned
        HTTPException 400: If validation fails

    Security Note:
        Returns 403 for both "task not found" and "not owned by user" to prevent
        information leakage about task existence.
    """
    # Verify user_id matches current user
    if current_user.id != user_id:
        raise HTTPException(
            status_code=403,
            detail=APIResponse.error("FORBIDDEN", "Not authorized to access this resource").dict(),
        )

    # Update task with ownership verification
    try:
        task = await TaskService.update_task(
            session,
            task_id,
            user_id,
            title=task_data.title,
            description=task_data.description,
            completed=task_data.completed,
        )
    except ValueError as e:
        error_code = "NOT_FOUND" if "not found" in str(e).lower() else "INVALID_TASK"
        if error_code == "NOT_FOUND":
            # Return 403 instead of 404 to prevent leaking task existence
            raise HTTPException(
                status_code=403,
                detail=APIResponse.error("FORBIDDEN", "Not authorized to access this resource").dict(),
            )
        else:
            raise HTTPException(
                status_code=400,
                detail=APIResponse.error(error_code, str(e)).dict(),
            )

    task_response = TaskResponse.from_attributes(task)
    return APIResponse.success(task_response.dict())


@router.delete("/{user_id}/tasks/{task_id}", status_code=204)
async def delete_task_endpoint(
    user_id: UUID,
    task_id: UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """
    Delete a task

    Args:
        user_id: UUID of the user
        task_id: UUID of the task
        current_user: Authenticated user (dependency injection)
        session: Database session

    Returns:
        204 No Content (empty response)

    Raises:
        HTTPException 403: If current_user.id != user_id or task not owned

    Security Note:
        Returns 403 for both "task not found" and "not owned by user" to prevent
        information leakage about task existence.
    """
    # Verify user_id matches current user
    if current_user.id != user_id:
        raise HTTPException(
            status_code=403,
            detail=APIResponse.error("FORBIDDEN", "Not authorized to access this resource").dict(),
        )

    # Delete task with ownership verification
    try:
        await TaskService.delete_task(session, task_id, user_id)
    except ValueError:
        # Return 403 instead of 404 to prevent leaking task existence
        raise HTTPException(
            status_code=403,
            detail=APIResponse.error("FORBIDDEN", "Not authorized to access this resource").dict(),
        )

    return None
