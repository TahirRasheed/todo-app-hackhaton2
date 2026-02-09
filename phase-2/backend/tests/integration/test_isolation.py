"""Multi-user data isolation tests"""
import pytest
from httpx import AsyncClient

from backend.src.main import app


@pytest.mark.asyncio
class TestDataIsolation:
    """Tests to verify users cannot access other users' data"""

    async def test_user_cannot_access_other_users_task_list(
        self, async_client: AsyncClient
    ):
        """Test that User A cannot GET User B's task list"""
        # Create User A
        user_a_response = await async_client.post(
            "/api/v1/auth/signup",
            json={
                "email": "usera@example.com",
                "password": "password123",
                "name": "User A"
            }
        )
        user_a_id = user_a_response.json()["data"]["id"]

        # Create User B
        user_b_response = await async_client.post(
            "/api/v1/auth/signup",
            json={
                "email": "userb@example.com",
                "password": "password123",
                "name": "User B"
            }
        )
        user_b_id = user_b_response.json()["data"]["id"]

        # User B creates a task
        await async_client.post(
            f"/api/v1/users/{user_b_id}/tasks",
            json={"title": "User B's Task"}
        )

        # User A tries to access User B's task list → should get 403
        response = await async_client.get(f"/api/v1/users/{user_b_id}/tasks")
        assert response.status_code == 403
        assert "FORBIDDEN" in response.json()["error"]["code"]

    async def test_user_cannot_access_other_users_specific_task(
        self, async_client: AsyncClient
    ):
        """Test that User A cannot GET User B's specific task"""
        # Create User A
        user_a_response = await async_client.post(
            "/api/v1/auth/signup",
            json={
                "email": "usera2@example.com",
                "password": "password123",
                "name": "User A2"
            }
        )
        user_a_id = user_a_response.json()["data"]["id"]

        # Create User B
        user_b_response = await async_client.post(
            "/api/v1/auth/signup",
            json={
                "email": "userb2@example.com",
                "password": "password123",
                "name": "User B2"
            }
        )
        user_b_id = user_b_response.json()["data"]["id"]

        # User B creates a task
        create_response = await async_client.post(
            f"/api/v1/users/{user_b_id}/tasks",
            json={"title": "User B's Task"}
        )
        task_id = create_response.json()["data"]["id"]

        # User A tries to access User B's specific task → should get 403
        response = await async_client.get(
            f"/api/v1/users/{user_b_id}/tasks/{task_id}"
        )
        assert response.status_code == 403
        assert "FORBIDDEN" in response.json()["error"]["code"]

    async def test_user_cannot_create_task_for_other_user(
        self, async_client: AsyncClient
    ):
        """Test that User A cannot POST to User B's task endpoint"""
        # Create User A
        user_a_response = await async_client.post(
            "/api/v1/auth/signup",
            json={
                "email": "usera3@example.com",
                "password": "password123",
                "name": "User A3"
            }
        )
        user_a_id = user_a_response.json()["data"]["id"]

        # Create User B
        user_b_response = await async_client.post(
            "/api/v1/auth/signup",
            json={
                "email": "userb3@example.com",
                "password": "password123",
                "name": "User B3"
            }
        )
        user_b_id = user_b_response.json()["data"]["id"]

        # User A tries to create a task for User B → should get 403
        response = await async_client.post(
            f"/api/v1/users/{user_b_id}/tasks",
            json={"title": "Hacked Task"}
        )
        assert response.status_code == 403
        assert "FORBIDDEN" in response.json()["error"]["code"]

    async def test_tasks_created_by_user_a_invisible_to_user_b(
        self, async_client: AsyncClient
    ):
        """Test that User A's tasks don't appear in User B's task list"""
        # Create User A
        user_a_response = await async_client.post(
            "/api/v1/auth/signup",
            json={
                "email": "usera4@example.com",
                "password": "password123",
                "name": "User A4"
            }
        )
        user_a_id = user_a_response.json()["data"]["id"]

        # Create User B
        user_b_response = await async_client.post(
            "/api/v1/auth/signup",
            json={
                "email": "userb4@example.com",
                "password": "password123",
                "name": "User B4"
            }
        )
        user_b_id = user_b_response.json()["data"]["id"]

        # User A creates task
        await async_client.post(
            f"/api/v1/users/{user_a_id}/tasks",
            json={"title": "User A's Task"}
        )

        # User B lists their tasks
        response = await async_client.get(f"/api/v1/users/{user_b_id}/tasks")
        assert response.status_code == 200
        data = response.json()

        # User B should see no tasks (User A's tasks invisible)
        assert len(data["data"]) == 0
        assert data["meta"]["total"] == 0

    async def test_different_users_task_lists_are_independent(
        self, async_client: AsyncClient
    ):
        """Test that task lists are properly isolated between users"""
        # Create User A and create 2 tasks
        user_a_response = await async_client.post(
            "/api/v1/auth/signup",
            json={
                "email": "usera5@example.com",
                "password": "password123",
                "name": "User A5"
            }
        )
        user_a_id = user_a_response.json()["data"]["id"]

        await async_client.post(
            f"/api/v1/users/{user_a_id}/tasks",
            json={"title": "A Task 1"}
        )
        await async_client.post(
            f"/api/v1/users/{user_a_id}/tasks",
            json={"title": "A Task 2"}
        )

        # Create User B and create 3 tasks
        user_b_response = await async_client.post(
            "/api/v1/auth/signup",
            json={
                "email": "userb5@example.com",
                "password": "password123",
                "name": "User B5"
            }
        )
        user_b_id = user_b_response.json()["data"]["id"]

        await async_client.post(
            f"/api/v1/users/{user_b_id}/tasks",
            json={"title": "B Task 1"}
        )
        await async_client.post(
            f"/api/v1/users/{user_b_id}/tasks",
            json={"title": "B Task 2"}
        )
        await async_client.post(
            f"/api/v1/users/{user_b_id}/tasks",
            json={"title": "B Task 3"}
        )

        # User A lists their tasks
        user_a_tasks = await async_client.get(f"/api/v1/users/{user_a_id}/tasks")
        assert user_a_tasks.status_code == 200
        assert len(user_a_tasks.json()["data"]) == 2
        assert user_a_tasks.json()["meta"]["total"] == 2

        # User B lists their tasks
        user_b_tasks = await async_client.get(f"/api/v1/users/{user_b_id}/tasks")
        assert user_b_tasks.status_code == 200
        assert len(user_b_tasks.json()["data"]) == 3
        assert user_b_tasks.json()["meta"]["total"] == 3

        # Verify no cross-contamination
        user_a_titles = [t["title"] for t in user_a_tasks.json()["data"]]
        user_b_titles = [t["title"] for t in user_b_tasks.json()["data"]]

        for title in user_a_titles:
            assert title not in user_b_titles

        for title in user_b_titles:
            assert title not in user_a_titles
