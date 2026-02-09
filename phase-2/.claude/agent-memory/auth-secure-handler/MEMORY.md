# Auth Security Handler Memory

## Project Context
- **Framework**: FastAPI (backend) + Next.js 16+ (frontend)
- **Database**: Neon PostgreSQL via SQLModel ORM
- **Authentication**: JWT tokens (HS256, 900s expiration)
- **Password Hashing**: Bcrypt with cost factor 10

## Implementation Patterns

### Password Security
- **Hashing**: Use `passlib.context.CryptContext` with bcrypt scheme
- **Validation**: Minimum 8 chars + uppercase + lowercase + digit
- **Storage**: Never store plaintext; always verify using `pwd_context.verify()`
- **Pattern**: `validate_password_strength(password)` returns `(bool, str)` tuple

### JWT Token Management
- **Creation**: `create_access_token(user_id, email)` returns `(token, expires_in)`
- **Claims**: Required claims are `sub` (user_id), `email`, `iat`, `exp`, `iss`, `aud`
- **Expiration**: 900 seconds (15 minutes) for access tokens
- **Signature**: HS256 algorithm with `settings.JWT_SECRET`
- **Verification**: Always check signature, expiration, and required claims

### Error Handling Standards
- **400 Bad Request**: Invalid input (weak password, invalid email format)
- **401 Unauthorized**: Authentication failed (invalid credentials)
- **409 Conflict**: Resource conflict (duplicate email)
- **500 Internal Server Error**: Unexpected server errors
- **User Enumeration Prevention**: Generic messages ("Email already registered" not "User exists")

### Response Format
- **Signup/Signin Success**: Return `UserTokenResponse` with `id`, `email`, `name`, `token`, `expiresIn`
- **Never Expose**: Passwords, password hashes, or internal error details
- **Token Delivery**: Token in response body (frontend stores in localStorage or httpOnly cookie)

## Testing Strategies

### Unit Test Coverage
- **Password Hashing**: Test hash generation, verification, salt uniqueness
- **Password Validation**: Test all requirements (length, uppercase, lowercase, digit, empty)
- **JWT Creation**: Test token format, claims, expiration calculation
- **JWT Verification**: Test valid tokens, tampered tokens, malformed tokens, expiration

### Integration Test Coverage
- **Signup Flow**: Valid signup, invalid email, weak password, duplicate email, token verification
- **Signin Flow**: Valid signin, invalid email, wrong password, token issuance, enumeration prevention
- **Token Security**: Token in response, password not exposed, claims match user data
- **Enumeration Prevention**: Verify identical error messages for wrong email vs wrong password

### Test Fixtures
- Use in-memory SQLite (`sqlite+aiosqlite:///:memory:`) for fast test database
- Override `get_session` dependency in FastAPI app for test isolation
- Create async fixtures with `pytest_asyncio.fixture` decorator

## Common Issues and Solutions

### Issue: Import Errors in Tests
**Solution**: Use relative imports (`from src.module`) instead of absolute imports in backend code

### Issue: Database Session Not Available in Tests
**Solution**: Create test session fixture and override `get_session` dependency:
```python
app.dependency_overrides[get_session] = override_get_session
```

### Issue: Token Not Persisting Across Requests
**Solution**: Frontend should store token in localStorage or httpOnly cookie and send in `Authorization: Bearer <token>` header

### Issue: Password Validation Inconsistent Between Frontend/Backend
**Solution**: Use identical regex patterns:
- Frontend: `/[A-Z]/`, `/[a-z]/`, `/\d/`, `password.length >= 8`
- Backend: `re.search(r"[A-Z]", password)`, etc.

### Timing Attack Prevention
- **Pattern**: Always verify password (even if user doesn't exist)
- **Implementation**: Use dummy hash when user not found to maintain constant-time behavior
- **Code Location**: `UserService.authenticate()` in `user_service.py`
- **Dummy Hash**: `$2b$10$dummyhashfortimingatttackpreventionxxx1234567890abcdefghij`

### User Enumeration Prevention
- **Pattern**: Return identical error message for "email not found" and "wrong password"
- **Error Message**: "Invalid email or password" (generic, no field-specific info)
- **Status Code**: 401 Unauthorized for both cases
- **Test**: `test_signin_prevents_user_enumeration()` verifies messages are identical

## Security Decisions

### Why JWT in Response Body (Not httpOnly Cookie)?
- **Flexibility**: Allows mobile apps and native clients to authenticate
- **Simplicity**: Frontend has full control over token storage
- **Trade-off**: More vulnerable to XSS (client must sanitize inputs)
- **Production Fix**: Next.js middleware can set httpOnly cookie after receiving token

### Why Bcrypt Cost Factor 10?
- **Balance**: Secure enough for most applications while maintaining performance
- **Standard**: OWASP recommends cost 10-12 for web applications
- **Upgrade Path**: Can increase cost factor as hardware improves

### Why 900 Second Token Expiration?
- **Security**: Short expiration reduces risk of token theft
- **UX**: 15 minutes is long enough for typical user sessions
- **Refresh Strategy**: Implement refresh tokens for longer sessions (Phase 4)

## File Locations

### Backend
- Auth endpoint: `backend/src/api/v1/auth.py`
- JWT module: `backend/src/security/jwt.py`
- Password module: `backend/src/security/password.py`
- User service: `backend/src/services/user_service.py`
- Schemas: `backend/src/schemas/user.py`
- Unit tests: `backend/tests/unit/test_security.py`
- Integration tests: `backend/tests/integration/test_auth_flow.py`

### Frontend
- Auth form: `frontend/src/components/AuthForm.tsx`
- API client: `frontend/src/lib/api.ts`
- Signup page: `frontend/src/app/auth/signup/page.tsx`
- Signin page: `frontend/src/app/auth/signin/page.tsx`

## Implementation History

### Phase 4 - Signin Feature (US2) - COMPLETED
- **Backend**: Signin endpoint with UserSignin schema
- **Security**: Enumeration prevention + timing attack prevention
- **Frontend**: Signin form (already implemented in Phase 3)
- **Tests**: Added enumeration prevention test, constant-time verification test
- **Files Modified**: `auth.py`, `user_service.py`, `test_auth_flow.py`, `test_security.py`

## Next Phase Checklist
- [x] Implement signin endpoint (COMPLETED - Phase 4)
- [ ] Add authentication middleware for protected routes
- [ ] Implement password reset flow with email verification
- [ ] Add rate limiting on auth endpoints (5 attempts per 15 min)
- [ ] Implement refresh token rotation
- [ ] Add account lockout after failed attempts (10 failures = 30 min lockout)
- [ ] Log authentication events for security monitoring
- [ ] Upgrade token storage to httpOnly cookies (via Next.js middleware)
