"""Task CRUD integration tests"""
import pytest
from httpx import AsyncClient

from backend.src.main import app


@pytest.mark.asyncio
class TestCreateTask:
    """Tests for task creation endpoint"""

    async def test_create_task_with_valid_title(self, async_client: AsyncClient):
        """Test successful task creation with valid title"""
        # First, signup to get user_id
        signup_response = await async_client.post(
            "/api/v1/auth/signup",
            json={
                "email": "user@example.com",
                "password": "password123",
                "name": "Test User"
            }
        )
        assert signup_response.status_code == 201
        user_id = signup_response.json()["data"]["id"]

        # Create task
        response = await async_client.post(
            f"/api/v1/users/{user_id}/tasks",
            json={
                "title": "My First Task",
                "description": "This is my first task"
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert data["data"]["title"] == "My First Task"
        assert data["data"]["description"] == "This is my first task"
        assert data["data"]["completed"] is False
        assert data["error"] is None

    async def test_create_task_without_title(self, async_client: AsyncClient):
        """Test task creation without title (should fail)"""
        # Signup
        signup_response = await async_client.post(
            "/api/v1/auth/signup",
            json={
                "email": "notitle@example.com",
                "password": "password123",
                "name": "No Title User"
            }
        )
        user_id = signup_response.json()["data"]["id"]

        # Try to create task without title
        response = await async_client.post(
            f"/api/v1/users/{user_id}/tasks",
            json={"description": "Missing title"}
        )
        assert response.status_code == 400
        assert "INVALID_TASK" in response.json()["error"]["code"]

    async def test_create_task_with_title_too_long(self, async_client: AsyncClient):
        """Test task creation with title > 500 chars (should fail)"""
        signup_response = await async_client.post(
            "/api/v1/auth/signup",
            json={
                "email": "longtitle@example.com",
                "password": "password123",
                "name": "Long Title User"
            }
        )
        user_id = signup_response.json()["data"]["id"]

        long_title = "x" * 501

        response = await async_client.post(
            f"/api/v1/users/{user_id}/tasks",
            json={"title": long_title}
        )
        assert response.status_code == 400
        assert "INVALID_TASK" in response.json()["error"]["code"]


@pytest.mark.asyncio
class TestListTasks:
    """Tests for task list endpoint"""

    async def test_list_tasks_empty(self, async_client: AsyncClient):
        """Test listing tasks when user has no tasks"""
        signup_response = await async_client.post(
            "/api/v1/auth/signup",
            json={
                "email": "emptytasks@example.com",
                "password": "password123",
                "name": "Empty Tasks User"
            }
        )
        user_id = signup_response.json()["data"]["id"]

        response = await async_client.get(f"/api/v1/users/{user_id}/tasks")
        assert response.status_code == 200
        data = response.json()
        assert data["data"] == []
        assert data["meta"]["total"] == 0

    async def test_list_tasks_with_pagination(self, async_client: AsyncClient):
        """Test listing tasks with pagination"""
        signup_response = await async_client.post(
            "/api/v1/auth/signup",
            json={
                "email": "pagination@example.com",
                "password": "password123",
                "name": "Pagination User"
            }
        )
        user_id = signup_response.json()["data"]["id"]

        # Create 3 tasks
        for i in range(3):
            await async_client.post(
                f"/api/v1/users/{user_id}/tasks",
                json={"title": f"Task {i+1}"}
            )

        # List with limit=2
        response = await async_client.get(
            f"/api/v1/users/{user_id}/tasks?skip=0&limit=2"
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]) == 2
        assert data["meta"]["total"] == 3
        assert data["meta"]["skip"] == 0
        assert data["meta"]["limit"] == 2

    async def test_list_tasks_ordered_by_created_at(self, async_client: AsyncClient):
        """Test that tasks are ordered by created_at DESC"""
        signup_response = await async_client.post(
            "/api/v1/auth/signup",
            json={
                "email": "ordered@example.com",
                "password": "password123",
                "name": "Ordered User"
            }
        )
        user_id = signup_response.json()["data"]["id"]

        # Create tasks
        titles = ["First", "Second", "Third"]
        for title in titles:
            await async_client.post(
                f"/api/v1/users/{user_id}/tasks",
                json={"title": title}
            )

        # List tasks
        response = await async_client.get(f"/api/v1/users/{user_id}/tasks")
        data = response.json()
        returned_titles = [t["title"] for t in data["data"]]

        # Should be in reverse order (newest first)
        assert returned_titles == ["Third", "Second", "First"]


@pytest.mark.asyncio
class TestGetTask:
    """Tests for get single task endpoint"""

    async def test_get_task_success(self, async_client: AsyncClient):
        """Test retrieving a single task"""
        signup_response = await async_client.post(
            "/api/v1/auth/signup",
            json={
                "email": "gettask@example.com",
                "password": "password123",
                "name": "Get Task User"
            }
        )
        user_id = signup_response.json()["data"]["id"]

        # Create task
        create_response = await async_client.post(
            f"/api/v1/users/{user_id}/tasks",
            json={"title": "Task to Get"}
        )
        task_id = create_response.json()["data"]["id"]

        # Get task
        response = await async_client.get(
            f"/api/v1/users/{user_id}/tasks/{task_id}"
        )
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["id"] == task_id
        assert data["data"]["title"] == "Task to Get"

    async def test_get_nonexistent_task(self, async_client: AsyncClient):
        """Test getting a task that doesn't exist"""
        signup_response = await async_client.post(
            "/api/v1/auth/signup",
            json={
                "email": "notask@example.com",
                "password": "password123",
                "name": "No Task User"
            }
        )
        user_id = signup_response.json()["data"]["id"]

        fake_task_id = "00000000-0000-0000-0000-000000000000"

        response = await async_client.get(
            f"/api/v1/users/{user_id}/tasks/{fake_task_id}"
        )
        assert response.status_code == 404
        assert "NOT_FOUND" in response.json()["error"]["code"]

    async def test_get_task_without_jwt(self, async_client: AsyncClient):
        """Test getting task without JWT (should fail)"""
        fake_user_id = "00000000-0000-0000-0000-000000000000"
        fake_task_id = "00000000-0000-0000-0000-000000000001"

        response = await async_client.get(
            f"/api/v1/users/{fake_user_id}/tasks/{fake_task_id}"
        )
        assert response.status_code == 401


@pytest.mark.asyncio
class TestTaskValidation:
    """Tests for task validation"""

    async def test_create_task_with_long_description(self, async_client: AsyncClient):
        """Test task creation with description > 5000 chars (should fail)"""
        signup_response = await async_client.post(
            "/api/v1/auth/signup",
            json={
                "email": "longdesc@example.com",
                "password": "password123",
                "name": "Long Desc User"
            }
        )
        user_id = signup_response.json()["data"]["id"]

        long_description = "x" * 5001

        response = await async_client.post(
            f"/api/v1/users/{user_id}/tasks",
            json={
                "title": "Task",
                "description": long_description
            }
        )
        assert response.status_code == 400
        assert "INVALID_TASK" in response.json()["error"]["code"]

    async def test_create_task_with_valid_max_lengths(self, async_client: AsyncClient):
        """Test task creation with max-length title and description"""
        signup_response = await async_client.post(
            "/api/v1/auth/signup",
            json={
                "email": "maxlen@example.com",
                "password": "password123",
                "name": "Max Len User"
            }
        )
        user_id = signup_response.json()["data"]["id"]

        max_title = "x" * 500
        max_description = "y" * 5000

        response = await async_client.post(
            f"/api/v1/users/{user_id}/tasks",
            json={
                "title": max_title,
                "description": max_description
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert len(data["data"]["title"]) == 500
        assert len(data["data"]["description"]) == 5000


@pytest.mark.asyncio
class TestUpdateTask:
    """Tests for task update endpoint"""

    async def test_update_task_completed_status(self, async_client: AsyncClient):
        """Test marking task as complete"""
        # Create user and task
        signup_response = await async_client.post(
            "/api/v1/auth/signup",
            json={
                "email": "updatetest@example.com",
                "password": "password123",
                "name": "Update Test"
            }
        )
        user_id = signup_response.json()["data"]["id"]

        create_response = await async_client.post(
            f"/api/v1/users/{user_id}/tasks",
            json={"title": "Task to update"}
        )
        task_id = create_response.json()["data"]["id"]

        # Update task to complete
        response = await async_client.put(
            f"/api/v1/users/{user_id}/tasks/{task_id}",
            json={"completed": True}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["completed"] is True

    async def test_update_task_title(self, async_client: AsyncClient):
        """Test updating task title"""
        signup_response = await async_client.post(
            "/api/v1/auth/signup",
            json={
                "email": "titleupdate@example.com",
                "password": "password123",
                "name": "Title Update"
            }
        )
        user_id = signup_response.json()["data"]["id"]

        create_response = await async_client.post(
            f"/api/v1/users/{user_id}/tasks",
            json={"title": "Old Title"}
        )
        task_id = create_response.json()["data"]["id"]

        # Update title
        response = await async_client.put(
            f"/api/v1/users/{user_id}/tasks/{task_id}",
            json={"title": "New Title"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["title"] == "New Title"

    async def test_update_task_description(self, async_client: AsyncClient):
        """Test updating task description"""
        signup_response = await async_client.post(
            "/api/v1/auth/signup",
            json={
                "email": "descupdate@example.com",
                "password": "password123",
                "name": "Desc Update"
            }
        )
        user_id = signup_response.json()["data"]["id"]

        create_response = await async_client.post(
            f"/api/v1/users/{user_id}/tasks",
            json={"title": "Task", "description": "Old description"}
        )
        task_id = create_response.json()["data"]["id"]

        # Update description
        response = await async_client.put(
            f"/api/v1/users/{user_id}/tasks/{task_id}",
            json={"description": "New description"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["description"] == "New description"

    async def test_update_nonexistent_task(self, async_client: AsyncClient):
        """Test updating a task that doesn't exist"""
        signup_response = await async_client.post(
            "/api/v1/auth/signup",
            json={
                "email": "notask@example.com",
                "password": "password123",
                "name": "No Task"
            }
        )
        user_id = signup_response.json()["data"]["id"]

        fake_task_id = "00000000-0000-0000-0000-000000000000"

        response = await async_client.put(
            f"/api/v1/users/{user_id}/tasks/{fake_task_id}",
            json={"title": "Updated"}
        )
        assert response.status_code == 404


@pytest.mark.asyncio
class TestDeleteTask:
    """Tests for task delete endpoint"""

    async def test_delete_task_success(self, async_client: AsyncClient):
        """Test successful task deletion"""
        signup_response = await async_client.post(
            "/api/v1/auth/signup",
            json={
                "email": "deletetest@example.com",
                "password": "password123",
                "name": "Delete Test"
            }
        )
        user_id = signup_response.json()["data"]["id"]

        create_response = await async_client.post(
            f"/api/v1/users/{user_id}/tasks",
            json={"title": "Task to delete"}
        )
        task_id = create_response.json()["data"]["id"]

        # Delete task
        response = await async_client.delete(
            f"/api/v1/users/{user_id}/tasks/{task_id}"
        )
        assert response.status_code == 204

        # Verify task is deleted
        get_response = await async_client.get(
            f"/api/v1/users/{user_id}/tasks/{task_id}"
        )
        assert get_response.status_code == 404

    async def test_delete_nonexistent_task(self, async_client: AsyncClient):
        """Test deleting a task that doesn't exist"""
        signup_response = await async_client.post(
            "/api/v1/auth/signup",
            json={
                "email": "deletenonexist@example.com",
                "password": "password123",
                "name": "Delete Nonexist"
            }
        )
        user_id = signup_response.json()["data"]["id"]

        fake_task_id = "00000000-0000-0000-0000-000000000000"

        response = await async_client.delete(
            f"/api/v1/users/{user_id}/tasks/{fake_task_id}"
        )
        assert response.status_code == 404

    async def test_delete_removes_from_list(self, async_client: AsyncClient):
        """Test that deleted task doesn't appear in list"""
        signup_response = await async_client.post(
            "/api/v1/auth/signup",
            json={
                "email": "deleteremove@example.com",
                "password": "password123",
                "name": "Delete Remove"
            }
        )
        user_id = signup_response.json()["data"]["id"]

        # Create 2 tasks
        task1_response = await async_client.post(
            f"/api/v1/users/{user_id}/tasks",
            json={"title": "Task 1"}
        )
        task1_id = task1_response.json()["data"]["id"]

        task2_response = await async_client.post(
            f"/api/v1/users/{user_id}/tasks",
            json={"title": "Task 2"}
        )
        task2_id = task2_response.json()["data"]["id"]

        # Delete task 1
        await async_client.delete(f"/api/v1/users/{user_id}/tasks/{task1_id}")

        # List tasks
        list_response = await async_client.get(f"/api/v1/users/{user_id}/tasks")
        assert list_response.status_code == 200
        data = list_response.json()

        # Only task 2 should remain
        assert len(data["data"]) == 1
        assert data["data"][0]["id"] == task2_id
