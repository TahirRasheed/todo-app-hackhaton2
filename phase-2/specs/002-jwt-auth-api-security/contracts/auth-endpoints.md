# API Contracts: Authentication Endpoints

**Feature**: 002-jwt-auth-api-security
**Date**: 2026-02-09
**Base URL**: `http://localhost:8000/api/v1` (development)

---

## POST /auth/signup

**Purpose**: Create a new user account with email and password

**Method**: POST

**Path**: `/auth/signup`

**Authentication**: None (public endpoint)

### Request

**Headers**:
```
Content-Type: application/json
```

**Body** (application/json):
```json
{
  "email": "john@example.com",
  "password": "SecurePass123",
  "name": "John Doe"
}
```

**Field Descriptions**:
- `email` (string, required): User's email address. Must be valid email format, unique across all users.
- `password` (string, required): Plain text password. Will be hashed with bcrypt before storage. Min 8 chars, must include uppercase, lowercase, digit.
- `name` (string, optional): User's display name. Max 255 characters.

### Response

**Success (201 Created)**:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "john@example.com",
  "name": "John Doe",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1NTBlODQwMC1lMjliLTQxZDQtYTcxNi00NDY2NTU0NDAwMDAiLCJlbWFpbCI6ImpvaG5AZXhhbXBsZS5jb20iLCJpYXQiOjE3MDc1MjgwMDAsImV4cCI6MTcwNzUyODkwMH0...",
  "expiresIn": 900
}
```

**Field Descriptions**:
- `id` (string): Unique user identifier (UUID)
- `email` (string): Confirmed user email
- `name` (string): User display name
- `token` (string): JWT Bearer token for authentication
- `expiresIn` (integer): Token expiration time in seconds (900 = 15 minutes)

**Frontend Action**:
- Store token in httpOnly cookie (handled by Better Auth)
- Redirect to dashboard (`/dashboard`)
- Subsequent API requests automatically include token

### Errors

**400 Bad Request** - Invalid input:
```json
{
  "detail": "Invalid email format"
}
```
**Possible messages**:
- "Invalid email format"
- "Email is required"
- "Password is required"
- "Password must be at least 8 characters"
- "Password must contain uppercase letter"
- "Password must contain lowercase letter"
- "Password must contain digit"

**409 Conflict** - Email already exists:
```json
{
  "detail": "Email already registered"
}
```

**500 Internal Server Error**:
```json
{
  "detail": "An error occurred during signup"
}
```

### Example Usage

```bash
curl -X POST http://localhost:8000/api/v1/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "password": "SecurePass123",
    "name": "John Doe"
  }'
```

### Frontend Integration (TypeScript with Better Auth)

```typescript
const handleSignup = async (formData: SignupForm) => {
  try {
    const response = await fetch('http://localhost:8000/api/v1/auth/signup', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(formData),
      credentials: 'include', // Send cookies
    });

    if (response.ok) {
      const data = await response.json();
      // Token automatically stored in cookie by backend
      // Redirect to dashboard
      router.push('/dashboard');
    } else {
      const error = await response.json();
      setError(error.detail);
    }
  } catch (err) {
    setError('Network error');
  }
};
```

---

## POST /auth/signin

**Purpose**: Authenticate user with email and password, receive JWT token

**Method**: POST

**Path**: `/auth/signin`

**Authentication**: None (public endpoint)

### Request

**Headers**:
```
Content-Type: application/json
```

**Body** (application/json):
```json
{
  "email": "john@example.com",
  "password": "SecurePass123"
}
```

**Field Descriptions**:
- `email` (string, required): User's registered email address
- `password` (string, required): Plain text password (will be compared to bcrypt hash)

### Response

**Success (200 OK)**:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "john@example.com",
  "name": "John Doe",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "expiresIn": 900
}
```

Same structure as signup response.

**Frontend Action**:
- Store token in httpOnly cookie
- Redirect to dashboard (`/dashboard`)
- Subsequent API requests include token

### Errors

**401 Unauthorized** - Invalid credentials:
```json
{
  "detail": "Invalid email or password"
}
```

**Note**: Same message for both "email not found" and "wrong password" to prevent user enumeration attacks.

**500 Internal Server Error**:
```json
{
  "detail": "An error occurred during signin"
}
```

### Example Usage

```bash
curl -X POST http://localhost:8000/api/v1/auth/signin \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "password": "SecurePass123"
  }'
```

### Security Notes

- Password comparison uses constant-time comparison (prevents timing attacks)
- Error message is generic (prevents user enumeration)
- Failed attempts are not rate-limited at API level (rate limiting is infrastructure responsibility)

---

## POST /auth/signout

**Purpose**: Invalidate user session (clear token on frontend)

**Method**: POST

**Path**: `/auth/signout`

**Authentication**: Required (Bearer token in Authorization header)

### Request

**Headers**:
```
Authorization: Bearer <token>
```

**Body**: Empty

### Response

**Success (200 OK)**:
```json
{
  "message": "Signed out successfully"
}
```

**Frontend Action**:
- Remove token from httpOnly cookie (handled by Better Auth)
- Redirect to signin page (`/auth/signin`)
- Subsequent API requests will have no token (return 401)

### Errors

**401 Unauthorized** - Missing or invalid token:
```json
{
  "detail": "Missing authentication"
}
```

**500 Internal Server Error**:
```json
{
  "detail": "An error occurred during signout"
}
```

### Example Usage

```bash
curl -X POST http://localhost:8000/api/v1/auth/signout \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

### Implementation Notes

- Backend does NOT need to store signout tokens (stateless)
- Token becomes invalid when expired (15 minutes)
- Frontend removes cookie immediately
- If user tries to use old token after signout, backend returns 401

---

## Token Format

### Bearer Token Structure

All authenticated endpoints require:
```
Authorization: Bearer <jwt-token>
```

**JWT Structure**:
```
Header.Payload.Signature

Header: {
  "alg": "HS256",
  "typ": "JWT"
}

Payload: {
  "sub": "550e8400-e29b-41d4-a716-446655440000",    // user_id
  "email": "john@example.com",
  "iat": 1707528000,                                 // issued at
  "exp": 1707528900,                                 // expires at
  "iss": "todo-app",                                 // issuer
  "aud": "todo-app-users"                            // audience
}

Signature: HMAC-SHA256(Header + Payload, JWT_SECRET)
```

---

## Common Response Codes

| Code | Meaning | When |
|------|---------|------|
| 200 | OK | Signin successful, signout successful |
| 201 | Created | Signup successful |
| 400 | Bad Request | Invalid email format, weak password |
| 401 | Unauthorized | Invalid credentials, missing token, expired token |
| 409 | Conflict | Email already exists |
| 500 | Server Error | Database error, unexpected exception |

---

## CORS Configuration

**Frontend Origin**: `http://localhost:3000` (development)

**Credentials**: Required
```javascript
fetch('http://localhost:8000/api/v1/auth/signin', {
  credentials: 'include', // Send/receive cookies
})
```

---

**Status**: ✅ Ready for implementation
