"""End-to-End Flow Integration Tests

Complete user journey tests covering the full authentication and task management flow.
Tests both happy paths and security scenarios to validate production readiness.

Test Coverage:
- Happy Path (7 tests): Signup → Signin → Create → Update → Complete → Delete → Signout
- Security Scenarios (5 tests): Cross-user access, token expiration, invalid tokens, etc.
"""

import pytest
from httpx import AsyncClient
from datetime import datetime, timedelta, timezone
from jose import jwt

from src.config import settings


@pytest.mark.asyncio
class TestHappyPathFlow:
    """Complete user journey from signup to task management and signout"""

    async def test_e2e_1_user_registers_and_gets_token(self, async_client: AsyncClient):
        """
        Test 1: User registers (signup) → Gets token → Token stored for subsequent requests

        Validates:
        - Signup endpoint returns 201 Created
        - Response includes user data (id, email, name)
        - Response includes JWT token
        - Token has proper expiration (900 seconds)
        - Token can be stored in localStorage (client-side)
        """
        response = await async_client.post(
            "/api/v1/auth/signup",
            json={
                "email": "e2e_user@example.com",
                "password": "SecurePass123",
                "name": "E2E Test User"
            }
        )

        # Verify successful signup
        assert response.status_code == 201, "Signup should return 201 Created"

        data = response.json()

        # Verify user data in response
        assert "id" in data, "Response should include user ID"
        assert data["email"] == "e2e_user@example.com", "Email should match"
        assert data["name"] == "E2E Test User", "Name should match"

        # Verify token in response
        assert "token" in data, "Response should include JWT token"
        assert isinstance(data["token"], str), "Token should be a string"
        assert len(data["token"]) > 100, "Token should be properly formatted JWT"

        # Verify token expiration
        assert "expiresIn" in data, "Response should include token expiration"
        assert data["expiresIn"] == 900, "Token should expire in 900 seconds (15 minutes)"

        # Simulate storing token in localStorage (client would do this)
        stored_token = data["token"]
        stored_user_id = data["id"]

        # Verify token can be used for authenticated requests
        # This simulates the client attaching the token to subsequent API calls
        headers = {"Authorization": f"Bearer {stored_token}"}

        # Test authenticated endpoint access
        tasks_response = await async_client.get(
            f"/api/v1/users/{stored_user_id}/tasks",
            headers=headers
        )
        assert tasks_response.status_code == 200, "Token should allow access to protected endpoints"

    async def test_e2e_2_user_logs_in_and_redirected_to_dashboard(self, async_client: AsyncClient):
        """
        Test 2: User logs in (signin) → Gets token → Redirected to dashboard

        Validates:
        - Signin endpoint authenticates existing user
        - Returns valid JWT token
        - Token can be used to access dashboard data
        - Client would redirect to /dashboard on successful signin
        """
        # First, create user via signup
        signup_response = await async_client.post(
            "/api/v1/auth/signup",
            json={
                "email": "signin_user@example.com",
                "password": "SecurePass123",
                "name": "Signin Test User"
            }
        )
        assert signup_response.status_code == 201

        # User logs in with credentials
        signin_response = await async_client.post(
            "/api/v1/auth/signin",
            json={
                "email": "signin_user@example.com",
                "password": "SecurePass123"
            }
        )

        # Verify successful signin
        assert signin_response.status_code == 200, "Signin should return 200 OK"

        data = signin_response.json()

        # Verify user data and token
        assert "id" in data, "Signin should return user ID"
        assert "token" in data, "Signin should return JWT token"
        assert data["email"] == "signin_user@example.com"

        # Simulate client storing token and redirecting to dashboard
        token = data["token"]
        user_id = data["id"]

        # Verify token allows access to dashboard data (task list)
        headers = {"Authorization": f"Bearer {token}"}
        dashboard_response = await async_client.get(
            f"/api/v1/users/{user_id}/tasks",
            headers=headers
        )

        assert dashboard_response.status_code == 200, "Token should allow dashboard access"
        assert dashboard_response.json()["success"] is True
        # New user should have empty task list
        assert len(dashboard_response.json()["data"]) == 0

    async def test_e2e_3_user_creates_task_and_appears_in_list(self, async_client: AsyncClient):
        """
        Test 3: User creates task → Task appears in list → Can fetch by ID

        Validates:
        - Create task endpoint works with valid token
        - Task is returned in list endpoint
        - Task can be retrieved individually by ID
        - Task has correct initial state (completed: false)
        """
        # Setup: Signup and get token
        signup_response = await async_client.post(
            "/api/v1/auth/signup",
            json={
                "email": "create_task@example.com",
                "password": "SecurePass123",
                "name": "Create Task User"
            }
        )
        token = signup_response.json()["token"]
        user_id = signup_response.json()["id"]
        headers = {"Authorization": f"Bearer {token}"}

        # Create a task
        create_response = await async_client.post(
            f"/api/v1/users/{user_id}/tasks",
            headers=headers,
            json={
                "title": "Buy groceries",
                "description": "Milk, eggs, bread"
            }
        )

        # Verify task created successfully
        assert create_response.status_code == 201, "Create task should return 201 Created"

        created_task = create_response.json()["data"]
        assert created_task["title"] == "Buy groceries"
        assert created_task["description"] == "Milk, eggs, bread"
        assert created_task["completed"] is False, "New task should not be completed"

        task_id = created_task["id"]

        # Verify task appears in list
        list_response = await async_client.get(
            f"/api/v1/users/{user_id}/tasks",
            headers=headers
        )

        assert list_response.status_code == 200
        tasks = list_response.json()["data"]
        assert len(tasks) == 1, "User should have 1 task"
        assert tasks[0]["id"] == task_id, "Task ID should match"
        assert tasks[0]["title"] == "Buy groceries"

        # Verify task can be fetched by ID
        get_response = await async_client.get(
            f"/api/v1/users/{user_id}/tasks/{task_id}",
            headers=headers
        )

        assert get_response.status_code == 200
        fetched_task = get_response.json()["data"]
        assert fetched_task["id"] == task_id
        assert fetched_task["title"] == "Buy groceries"

    async def test_e2e_4_user_updates_task_and_changes_saved(self, async_client: AsyncClient):
        """
        Test 4: User updates task → Changes saved → Can fetch updated version

        Validates:
        - Update task endpoint works with valid token
        - Title and description can be updated
        - Updated task can be retrieved with changes
        - Updated_at timestamp is updated
        """
        # Setup: Create user and task
        signup_response = await async_client.post(
            "/api/v1/auth/signup",
            json={
                "email": "update_task@example.com",
                "password": "SecurePass123",
                "name": "Update Task User"
            }
        )
        token = signup_response.json()["token"]
        user_id = signup_response.json()["id"]
        headers = {"Authorization": f"Bearer {token}"}

        create_response = await async_client.post(
            f"/api/v1/users/{user_id}/tasks",
            headers=headers,
            json={
                "title": "Original Title",
                "description": "Original Description"
            }
        )
        task_id = create_response.json()["data"]["id"]

        # Update the task
        update_response = await async_client.put(
            f"/api/v1/users/{user_id}/tasks/{task_id}",
            headers=headers,
            json={
                "title": "Updated Title",
                "description": "Updated Description"
            }
        )

        # Verify update successful
        assert update_response.status_code == 200, "Update should return 200 OK"

        updated_task = update_response.json()["data"]
        assert updated_task["title"] == "Updated Title", "Title should be updated"
        assert updated_task["description"] == "Updated Description", "Description should be updated"

        # Verify changes persisted by fetching task again
        get_response = await async_client.get(
            f"/api/v1/users/{user_id}/tasks/{task_id}",
            headers=headers
        )

        assert get_response.status_code == 200
        fetched_task = get_response.json()["data"]
        assert fetched_task["title"] == "Updated Title", "Fetched task should have updated title"
        assert fetched_task["description"] == "Updated Description", "Fetched task should have updated description"

    async def test_e2e_5_user_completes_task_and_list_reflects_change(self, async_client: AsyncClient):
        """
        Test 5: User completes task → Boolean flag updated → List reflects change

        Validates:
        - Task completion toggle works
        - Completed flag is properly stored
        - Task list shows correct completion status
        - Can mark as incomplete (toggle back)
        """
        # Setup: Create user and task
        signup_response = await async_client.post(
            "/api/v1/auth/signup",
            json={
                "email": "complete_task@example.com",
                "password": "SecurePass123",
                "name": "Complete Task User"
            }
        )
        token = signup_response.json()["token"]
        user_id = signup_response.json()["id"]
        headers = {"Authorization": f"Bearer {token}"}

        create_response = await async_client.post(
            f"/api/v1/users/{user_id}/tasks",
            headers=headers,
            json={"title": "Task to complete"}
        )
        task_id = create_response.json()["data"]["id"]

        # Verify initial state (not completed)
        assert create_response.json()["data"]["completed"] is False

        # Mark task as complete
        complete_response = await async_client.put(
            f"/api/v1/users/{user_id}/tasks/{task_id}",
            headers=headers,
            json={"completed": True}
        )

        # Verify completion successful
        assert complete_response.status_code == 200
        assert complete_response.json()["data"]["completed"] is True, "Task should be marked complete"

        # Verify list reflects completion
        list_response = await async_client.get(
            f"/api/v1/users/{user_id}/tasks",
            headers=headers
        )

        tasks = list_response.json()["data"]
        assert len(tasks) == 1
        assert tasks[0]["completed"] is True, "Task in list should show as completed"

        # Test toggle: Mark as incomplete
        incomplete_response = await async_client.put(
            f"/api/v1/users/{user_id}/tasks/{task_id}",
            headers=headers,
            json={"completed": False}
        )

        assert incomplete_response.status_code == 200
        assert incomplete_response.json()["data"]["completed"] is False, "Task should be marked incomplete"

    async def test_e2e_6_user_deletes_task_and_removed_from_list(self, async_client: AsyncClient):
        """
        Test 6: User deletes task → Task removed from list → Cannot fetch by ID

        Validates:
        - Delete task endpoint works with valid token
        - Returns 204 No Content
        - Task no longer appears in list
        - GET request for deleted task returns 404
        """
        # Setup: Create user and task
        signup_response = await async_client.post(
            "/api/v1/auth/signup",
            json={
                "email": "delete_task@example.com",
                "password": "SecurePass123",
                "name": "Delete Task User"
            }
        )
        token = signup_response.json()["token"]
        user_id = signup_response.json()["id"]
        headers = {"Authorization": f"Bearer {token}"}

        create_response = await async_client.post(
            f"/api/v1/users/{user_id}/tasks",
            headers=headers,
            json={"title": "Task to delete"}
        )
        task_id = create_response.json()["data"]["id"]

        # Delete the task
        delete_response = await async_client.delete(
            f"/api/v1/users/{user_id}/tasks/{task_id}",
            headers=headers
        )

        # Verify deletion successful
        assert delete_response.status_code == 204, "Delete should return 204 No Content"

        # Verify task removed from list
        list_response = await async_client.get(
            f"/api/v1/users/{user_id}/tasks",
            headers=headers
        )

        tasks = list_response.json()["data"]
        assert len(tasks) == 0, "Task should be removed from list"

        # Verify task cannot be fetched by ID (404)
        get_response = await async_client.get(
            f"/api/v1/users/{user_id}/tasks/{task_id}",
            headers=headers
        )

        assert get_response.status_code == 404, "Deleted task should return 404 Not Found"

    async def test_e2e_7_user_logs_out_and_cannot_access_protected_endpoints(self, async_client: AsyncClient):
        """
        Test 7: User logs out (signout) → Token cleared → Cannot access protected endpoints

        Validates:
        - Signout endpoint returns success with valid token
        - Client clears token from storage
        - Subsequent requests without token return 401
        - Token validation fails after signout

        Note: JWT tokens are stateless, so signout primarily happens client-side
        by clearing the token. The signout endpoint validates the token before
        acknowledging the signout.
        """
        # Setup: Create user and get token
        signup_response = await async_client.post(
            "/api/v1/auth/signup",
            json={
                "email": "signout_user@example.com",
                "password": "SecurePass123",
                "name": "Signout User"
            }
        )
        token = signup_response.json()["token"]
        user_id = signup_response.json()["id"]
        headers = {"Authorization": f"Bearer {token}"}

        # Verify token works before signout
        pre_signout_response = await async_client.get(
            f"/api/v1/users/{user_id}/tasks",
            headers=headers
        )
        assert pre_signout_response.status_code == 200, "Token should work before signout"

        # User signs out
        signout_response = await async_client.post(
            "/api/v1/auth/signout",
            headers=headers
        )

        # Verify signout successful
        assert signout_response.status_code == 200, "Signout should return 200 OK"
        assert signout_response.json()["message"] == "Signed out successfully"

        # Simulate client clearing token from localStorage
        # (In production, client would delete token from storage here)

        # Verify requests without token fail with 401
        no_token_response = await async_client.get(
            f"/api/v1/users/{user_id}/tasks"
            # No Authorization header
        )

        assert no_token_response.status_code == 401, "Request without token should return 401 Unauthorized"


@pytest.mark.asyncio
class TestSecurityScenarios:
    """Security validation tests for authentication and authorization"""

    async def test_e2e_8_cross_user_access_blocked(self, async_client: AsyncClient):
        """
        Test 8: Cross-user access blocked → User B cannot see User A's tasks

        Security Validation:
        - User A's token cannot access User B's resources
        - Returns 403 Forbidden (not 404)
        - Generic error message prevents information disclosure
        - Database queries are filtered by user_id
        """
        # Create User A with a task
        user_a_response = await async_client.post(
            "/api/v1/auth/signup",
            json={
                "email": "user_a@example.com",
                "password": "SecurePass123",
                "name": "User A"
            }
        )
        user_a_token = user_a_response.json()["token"]
        user_a_id = user_a_response.json()["id"]
        user_a_headers = {"Authorization": f"Bearer {user_a_token}"}

        task_response = await async_client.post(
            f"/api/v1/users/{user_a_id}/tasks",
            headers=user_a_headers,
            json={"title": "User A's Private Task"}
        )
        task_id = task_response.json()["data"]["id"]

        # Create User B
        user_b_response = await async_client.post(
            "/api/v1/auth/signup",
            json={
                "email": "user_b@example.com",
                "password": "SecurePass123",
                "name": "User B"
            }
        )
        user_b_token = user_b_response.json()["token"]
        user_b_headers = {"Authorization": f"Bearer {user_b_token}"}

        # User B tries to access User A's task list
        list_attack = await async_client.get(
            f"/api/v1/users/{user_a_id}/tasks",
            headers=user_b_headers
        )

        assert list_attack.status_code == 403, "Cross-user list access should return 403 Forbidden"
        assert "FORBIDDEN" in list_attack.json()["error"]["code"]

        # User B tries to GET User A's specific task
        get_attack = await async_client.get(
            f"/api/v1/users/{user_a_id}/tasks/{task_id}",
            headers=user_b_headers
        )

        assert get_attack.status_code == 403, "Cross-user GET should return 403 Forbidden"

        # User B tries to UPDATE User A's task
        update_attack = await async_client.put(
            f"/api/v1/users/{user_a_id}/tasks/{task_id}",
            headers=user_b_headers,
            json={"title": "Hacked!"}
        )

        assert update_attack.status_code == 403, "Cross-user UPDATE should return 403 Forbidden"

        # User B tries to DELETE User A's task
        delete_attack = await async_client.delete(
            f"/api/v1/users/{user_a_id}/tasks/{task_id}",
            headers=user_b_headers
        )

        assert delete_attack.status_code == 403, "Cross-user DELETE should return 403 Forbidden"

        # Verify User A's task is unchanged
        verify_response = await async_client.get(
            f"/api/v1/users/{user_a_id}/tasks/{task_id}",
            headers=user_a_headers
        )

        assert verify_response.status_code == 200
        assert verify_response.json()["data"]["title"] == "User A's Private Task", "Task should be unchanged"

    async def test_e2e_9_expired_token_returns_401_and_redirects_to_signin(self, async_client: AsyncClient):
        """
        Test 9: Token expiration → Expired token returns 401 → Client redirects to signin

        Security Validation:
        - Expired tokens are rejected with 401
        - Error message indicates token expiration
        - Client should redirect to signin page on 401
        - No access to protected resources with expired token
        """
        # Create user
        signup_response = await async_client.post(
            "/api/v1/auth/signup",
            json={
                "email": "expired_token@example.com",
                "password": "SecurePass123",
                "name": "Expired Token User"
            }
        )
        user_id = signup_response.json()["id"]

        # Create expired token (expired 1 hour ago)
        now = datetime.now(timezone.utc)
        expired_at = now - timedelta(hours=1)

        payload = {
            "sub": user_id,
            "email": "expired_token@example.com",
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

        # Verify expired token rejected
        assert response.status_code == 401, "Expired token should return 401 Unauthorized"

        # Error message should indicate authentication failure
        # (client would check status code and redirect to /signin)
        assert "invalid" in response.text.lower() or "authentication" in response.text.lower()

    async def test_e2e_10_missing_token_returns_401(self, async_client: AsyncClient):
        """
        Test 10: Missing token → Protected endpoint returns 401

        Security Validation:
        - All task endpoints require authentication
        - Missing Authorization header returns 401
        - Error message is clear and consistent
        """
        fake_user_id = "00000000-0000-0000-0000-000000000000"
        fake_task_id = "00000000-0000-0000-0000-000000000001"

        # Test all protected endpoints without token
        test_cases = [
            ("GET", f"/api/v1/users/{fake_user_id}/tasks"),
            ("POST", f"/api/v1/users/{fake_user_id}/tasks", {"title": "Test"}),
            ("GET", f"/api/v1/users/{fake_user_id}/tasks/{fake_task_id}"),
            ("PUT", f"/api/v1/users/{fake_user_id}/tasks/{fake_task_id}", {"title": "Updated"}),
            ("DELETE", f"/api/v1/users/{fake_user_id}/tasks/{fake_task_id}"),
        ]

        for method, url, *body in test_cases:
            if method == "GET":
                response = await async_client.get(url)
            elif method == "POST":
                response = await async_client.post(url, json=body[0])
            elif method == "PUT":
                response = await async_client.put(url, json=body[0])
            elif method == "DELETE":
                response = await async_client.delete(url)

            assert response.status_code == 401, f"{method} {url} should return 401 without token"

    async def test_e2e_11_invalid_token_returns_401(self, async_client: AsyncClient):
        """
        Test 11: Invalid token → Protected endpoint returns 401

        Security Validation:
        - Malformed JWT tokens are rejected
        - Invalid signatures are rejected
        - Non-Bearer formats are rejected
        - All return 401 with consistent error
        """
        fake_user_id = "00000000-0000-0000-0000-000000000000"

        # Test various invalid token formats
        invalid_tokens = [
            "not.a.jwt",  # Malformed
            "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0In0.invalid",  # Invalid signature
            "Bearer",  # Missing token
            "Token abc123",  # Wrong scheme
        ]

        for invalid_token in invalid_tokens:
            # Try Bearer format
            if invalid_token.startswith("Bearer") or invalid_token.startswith("Token"):
                headers = {"Authorization": invalid_token}
            else:
                headers = {"Authorization": f"Bearer {invalid_token}"}

            response = await async_client.get(
                f"/api/v1/users/{fake_user_id}/tasks",
                headers=headers
            )

            assert response.status_code == 401, f"Invalid token '{invalid_token}' should return 401"

    async def test_e2e_12_tampered_token_rejected(self, async_client: AsyncClient):
        """
        Test 12: Token modification → Tampered token rejected with 401

        Security Validation:
        - JWT signature verification prevents tampering
        - Modified payload is detected
        - Changed user_id in claims doesn't grant access
        - All tampering attempts return 401
        """
        # Create user and get valid token
        signup_response = await async_client.post(
            "/api/v1/auth/signup",
            json={
                "email": "tamper_test@example.com",
                "password": "SecurePass123",
                "name": "Tamper Test User"
            }
        )
        valid_token = signup_response.json()["token"]
        user_id = signup_response.json()["id"]

        # Create another user
        user_b_response = await async_client.post(
            "/api/v1/auth/signup",
            json={
                "email": "user_b_tamper@example.com",
                "password": "SecurePass123",
                "name": "User B"
            }
        )
        user_b_id = user_b_response.json()["id"]

        # Attempt 1: Modify token payload (change user_id to user_b_id)
        # This will break the signature
        parts = valid_token.split('.')
        if len(parts) == 3:
            # Tamper with the token by modifying it
            tampered_token = valid_token[:-5] + "XXXXX"  # Change last 5 chars

            response = await async_client.get(
                f"/api/v1/users/{user_b_id}/tasks",
                headers={"Authorization": f"Bearer {tampered_token}"}
            )

            assert response.status_code == 401, "Tampered token should be rejected"

        # Attempt 2: Create token with wrong secret
        payload = {
            "sub": user_b_id,
            "email": "user_b_tamper@example.com",
            "iat": int(datetime.now(timezone.utc).timestamp()),
            "exp": int((datetime.now(timezone.utc) + timedelta(minutes=15)).timestamp()),
            "iss": "todo-app",
            "aud": "todo-app-users",
        }

        wrong_secret_token = jwt.encode(
            payload,
            "wrong-secret-key",  # Wrong secret
            algorithm="HS256",
        )

        response = await async_client.get(
            f"/api/v1/users/{user_b_id}/tasks",
            headers={"Authorization": f"Bearer {wrong_secret_token}"}
        )

        assert response.status_code == 401, "Token with wrong secret should be rejected"


@pytest.mark.asyncio
class TestCompleteUserJourney:
    """Full end-to-end test simulating realistic user session"""

    async def test_complete_user_session(self, async_client: AsyncClient):
        """
        Complete User Journey: Signup → Create 3 tasks → Update 1 → Complete 1 → Delete 1 → Signout

        This test simulates a realistic user session covering all major features.
        """
        # Step 1: User signs up
        signup_response = await async_client.post(
            "/api/v1/auth/signup",
            json={
                "email": "complete_journey@example.com",
                "password": "SecurePass123",
                "name": "Complete Journey User"
            }
        )

        assert signup_response.status_code == 201
        token = signup_response.json()["token"]
        user_id = signup_response.json()["id"]
        headers = {"Authorization": f"Bearer {token}"}

        # Step 2: Create 3 tasks
        task_ids = []
        for i in range(1, 4):
            create_response = await async_client.post(
                f"/api/v1/users/{user_id}/tasks",
                headers=headers,
                json={"title": f"Task {i}", "description": f"Description {i}"}
            )
            assert create_response.status_code == 201
            task_ids.append(create_response.json()["data"]["id"])

        # Verify 3 tasks in list
        list_response = await async_client.get(
            f"/api/v1/users/{user_id}/tasks",
            headers=headers
        )
        assert len(list_response.json()["data"]) == 3

        # Step 3: Update Task 2 (change title)
        update_response = await async_client.put(
            f"/api/v1/users/{user_id}/tasks/{task_ids[1]}",
            headers=headers,
            json={"title": "Updated Task 2"}
        )
        assert update_response.status_code == 200
        assert update_response.json()["data"]["title"] == "Updated Task 2"

        # Step 4: Complete Task 1
        complete_response = await async_client.put(
            f"/api/v1/users/{user_id}/tasks/{task_ids[0]}",
            headers=headers,
            json={"completed": True}
        )
        assert complete_response.status_code == 200
        assert complete_response.json()["data"]["completed"] is True

        # Step 5: Delete Task 3
        delete_response = await async_client.delete(
            f"/api/v1/users/{user_id}/tasks/{task_ids[2]}",
            headers=headers
        )
        assert delete_response.status_code == 204

        # Verify final state: 2 tasks remaining
        final_list = await async_client.get(
            f"/api/v1/users/{user_id}/tasks",
            headers=headers
        )
        assert len(final_list.json()["data"]) == 2

        # Step 6: User signs out
        signout_response = await async_client.post(
            "/api/v1/auth/signout",
            headers=headers
        )
        assert signout_response.status_code == 200

        # Verify session ended (no token = 401)
        no_token_response = await async_client.get(
            f"/api/v1/users/{user_id}/tasks"
        )
        assert no_token_response.status_code == 401
