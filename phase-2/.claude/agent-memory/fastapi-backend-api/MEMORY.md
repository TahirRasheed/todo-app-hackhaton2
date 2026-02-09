# FastAPI Backend API Agent Memory

**Last Updated:** 2026-02-09
**Project:** Phase II Todo Full-Stack Web Application

---

## Project Architecture Patterns

### JWT Authentication Implementation
- **Token Structure:** HS256 algorithm, 900 second expiration (15 minutes)
- **Required Claims:** sub (user_id), email, iat, exp, iss ("todo-app"), aud ("todo-app-users")
- **Storage:** Client stores in localStorage or httpOnly cookie
- **Verification:** Middleware dependency (`get_current_user`) in `src/api/deps.py`

### 5-Layer Security Architecture
1. **JWT Middleware:** Token extraction and signature verification
2. **URL Parameter Validation:** Compare URL user_id with JWT user_id
3. **Database Query Filtering:** WHERE user_id = ? in all queries
4. **Service Layer Ownership:** Double-check task.user_id matches authenticated user
5. **API Response Formatting:** Sanitize responses, generic error messages

### Database Design
- **Users Table:** id (UUID), email (unique, indexed), password_hash, name, created_at
- **Tasks Table:** id (UUID), user_id (FK), title, description, completed, created_at, updated_at
- **Critical Index:** `(user_id, created_at DESC)` for list queries

### FastAPI Dependency Injection
- `get_session()`: Async database session
- `get_current_user()`: JWT verification, returns user_id
- `verify_user_access()`: URL ownership validation

---

## Security Best Practices

### Password Security
- **Hashing:** Bcrypt with cost factor 10 (`$2b$10$...`)
- **Strength Requirements:** 8+ chars, uppercase, lowercase, digit
- **Constant-Time Comparison:** Bcrypt prevents timing attacks
- **User Enumeration Prevention:** Identical error messages for "email not found" and "wrong password"

### JWT Security
- **Secret Management:** JWT_SECRET in environment variable (never hardcoded)
- **Expiration Enforcement:** Verify exp claim on every request
- **Signature Verification:** HMAC-SHA256 prevents tampering
- **Bearer Format:** Require "Bearer {token}" in Authorization header

### Authorization Patterns
- **Ownership Checks:** Verify user_id in URL matches JWT user_id
- **Cross-User Prevention:** Return 403 Forbidden for user mismatch
- **Generic Errors:** Same 403 response for "not found" and "forbidden" (prevents resource enumeration)
- **Immutable user_id:** Exclude from update schemas

### Error Handling Conventions
- **401 Unauthorized:** Missing/invalid/expired token
- **403 Forbidden:** Valid token, wrong user_id (ownership failure)
- **404 Not Found:** Resource doesn't exist (after ownership check)
- **409 Conflict:** Duplicate email on signup
- **422 Unprocessable Entity:** Pydantic validation failure

---

## Testing Patterns

### Test Structure
```
tests/
├── conftest.py           # Shared fixtures (database, client)
├── unit/                 # Security utilities, helpers
│   └── test_security.py
└── integration/          # API endpoint tests
    ├── test_auth_flow.py     # Authentication (signup, signin, signout)
    ├── test_task_crud.py     # Task CRUD operations
    ├── test_isolation.py     # Data isolation
    └── test_e2e_flow.py      # End-to-end user journeys
```

### Test Fixtures (conftest.py)
- **In-memory SQLite:** Fast tests, no cleanup needed
- **Async client:** FastAPI TestClient with dependency overrides
- **Session fixture:** Database session with automatic rollback

### E2E Test Pattern
1. Create user (signup)
2. Get JWT token
3. Perform operations with token in headers
4. Verify results
5. Test cleanup (automatic via fixture)

### Security Test Coverage
- Authentication (signup, signin, signout)
- JWT validation (signature, expiration, claims)
- Ownership enforcement (cross-user access blocked)
- Attack prevention (enumeration, timing, injection)

---

## Performance Optimizations

### Database Indexes
```sql
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_tasks_user_created ON tasks(user_id, created_at DESC);
```

### Query Optimization
- Use `SELECT ... WHERE user_id = ? LIMIT ?` for pagination
- Avoid `SELECT *` in production (specify columns)
- Use SQLModel ORM for parameterized queries (prevents SQL injection)

### Connection Pooling
- Pool size: 20 connections
- Max overflow: 10 connections
- Pool timeout: 30 seconds
- Recycle connections every hour

### Latency Targets
- JWT verification: < 10ms
- Authentication (signup/signin): < 500ms
- Task CRUD operations: < 100ms
- List tasks (10K tasks with index): < 50ms

---

## Common Issues & Solutions

### Issue: Rust Build Failure (Windows)
**Symptom:** `uv sync` fails with pydantic-core build error (link.exe issues)
**Solution:** Use pre-built wheels or install Visual Studio Build Tools with MSVC

### Issue: Token Expiration Too Short
**Symptom:** Users frequently re-authenticate
**Solution:** Balance security vs UX (current: 15 min access token, consider 7-day refresh token)

### Issue: Cross-User Access Not Blocked
**Symptom:** User A can access User B's data
**Solution:** Verify all 5 security layers are implemented (JWT, URL, DB filter, service, response)

### Issue: User Enumeration Vulnerability
**Symptom:** Different error messages reveal if email exists
**Solution:** Return identical "Invalid email or password" for both wrong email and wrong password

---

## API Design Conventions

### Response Format
```json
{
  "success": true,
  "data": { ... },
  "error": null,
  "meta": { "total": 10, "skip": 0, "limit": 20 }
}
```

### Error Format
```json
{
  "success": false,
  "data": null,
  "error": {
    "code": "FORBIDDEN",
    "message": "Not authorized to access this resource"
  }
}
```

### Authentication Response
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "name": "User Name",
  "token": "jwt-token-string",
  "expiresIn": 900
}
```

---

## Documentation Standards

### Security Documentation
- **SECURITY_CHECKLIST.md:** 24 security items with test evidence
- **SECURITY_GATES.md:** 5-layer architecture with attack scenarios
- **PERFORMANCE_BENCHMARKS.md:** Latency targets and scalability projections

### Test Documentation
- **TEST_SUMMARY.md:** Test coverage by category and acceptance criteria
- Docstrings: Explain what is tested, why it matters, and security impact

### Code Comments
- Security decisions: Explain why (e.g., "constant-time comparison prevents timing attacks")
- Performance trade-offs: Document when optimization matters
- Edge cases: Note unusual scenarios handled

---

## Production Deployment Checklist

### Environment Variables
- `DATABASE_URL`: Neon PostgreSQL connection string
- `JWT_SECRET`: Random 32+ character string (rotate periodically)
- `FRONTEND_URL`: For CORS configuration
- `ENVIRONMENT`: "production" (disables debug mode)

### Security Headers (Add via middleware)
- `Strict-Transport-Security: max-age=31536000`
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `Content-Security-Policy: default-src 'self'`

### Monitoring Metrics
- **Latency:** p50, p95, p99 for all endpoints
- **Error Rate:** 401, 403, 5xx counts
- **Throughput:** Requests per second
- **Database:** Connection pool utilization, query latency

### Alerting Thresholds
- p95 latency > 500ms for 5 minutes
- Error rate > 1% for 5 minutes
- Database connection pool > 90% for 2 minutes

---

## Lessons Learned

### Phase 8: E2E Testing & Security Validation

**What Worked Well:**
- 5-layer security architecture caught all attack vectors in testing
- E2E tests simulating real user journeys revealed integration issues early
- Defense-in-depth approach: Even if one layer fails, others still protect

**Challenges:**
- Windows Rust build issues with pydantic-core (use pre-built wheels)
- Balancing security (short token expiration) vs UX (frequent re-auth)
- Generic error messages for security sometimes less helpful for debugging

**Key Insights:**
- Security is not a feature, it's a layered architecture (5 independent validations)
- E2E tests are critical for validating full user journeys (not just individual endpoints)
- Performance and security are compatible (JWT verification < 10ms, minimal overhead)

**Future Improvements:**
- Implement token blacklist (Redis) for logout before expiration
- Add rate limiting to prevent brute-force attacks
- Implement refresh token rotation for better UX

---

## Quick Reference

### Run Tests
```bash
cd backend
uv run pytest tests/ -v                      # All tests
uv run pytest tests/integration/test_e2e_flow.py -v  # E2E tests only
```

### Create JWT Token Manually (for testing)
```python
from src.security.jwt import create_access_token
token, expires_in = create_access_token("user-id-123", "test@example.com")
```

### Verify Token Manually (for debugging)
```python
from src.security.jwt import verify_token
payload = verify_token(token)
print(payload["sub"])  # user_id
```

### Test Authentication Endpoint
```bash
curl -X POST http://localhost:8000/api/v1/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"SecurePass123","name":"Test User"}'
```

---

**Note:** This memory is project-specific and shared with the team via version control. Update after significant learnings or pattern changes.
