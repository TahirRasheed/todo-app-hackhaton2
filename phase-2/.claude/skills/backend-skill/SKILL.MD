---
name: backend-skill
description: Generate backend routes, handle HTTP requests/responses, and connect APIs with databases. Use for server-side feature development.
---

# Backend Routes & Database Skill

## Instructions

1. **Route Generation**
   - Create RESTful API routes
   - Follow standard HTTP methods:
     - GET → Fetch data
     - POST → Create data
     - PUT/PATCH → Update data
     - DELETE → Remove data
   - Use clean route naming (`/api/tasks`, `/api/users`)

2. **Request Handling**
   - Validate incoming request data
   - Parse params, query, and body
   - Handle authentication/authorization if required
   - Sanitize inputs before processing

3. **Response Handling**
   - Return structured JSON responses
   - Use proper status codes:
     - 200 → Success
     - 201 → Created
     - 400 → Bad request
     - 401 → Unauthorized
     - 404 → Not found
     - 500 → Server error
   - Include message + data payload

4. **Database Connection**
   - Configure DB connection (SQL/NoSQL)
   - Use ORM/Query builder where possible
   - Create models/schemas
   - Perform CRUD operations
   - Handle DB errors gracefully

---

## Best Practices

- Keep controllers thin, move logic to services
- Use environment variables for DB credentials
- Implement input validation (e.g., schemas)
- Use async/await for DB operations
- Add proper error handling middleware
- Follow MVC or layered architecture

---

## Example Structure

```js
// routes/taskRoutes.js
router.post("/tasks", createTask);
router.get("/tasks", getTasks);
router.put("/tasks/:id", updateTask);
router.delete("/tasks/:id", deleteTask);
