# Authentication API Contracts

**Feature**: 003-frontend-ui | **Date**: 2026-02-10
**Backend Spec**: [002-jwt-auth-api-security](../../002-jwt-auth-api-security/spec.md)

---

## Signup Endpoint

**URL**: `POST /api/v1/auth/signup`

**Purpose**: Create a new user account and issue JWT token

### Request

**Headers**:
```
Content-Type: application/json
```

**Body** (JSON):
```json
{
  "email": "user@example.com",
  "password": "SecurePass123",
  "name": "John Doe"
}
```

**Validation** (Client-side pre-checks):
- Email: Valid RFC 5322 format (e.g., user@example.com)
- Password: 8+ characters, at least one uppercase, one lowercase, one number
- Name: Non-empty, max 255 characters

### Response

**Success (201 Created)**:
```json
{
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "user@example.com",
    "name": "John Doe",
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1NTBlODQwMC1lMjliLTQxZDQtYTcxNi00NDY2NTU0NDAwMDAiLCJlbWFpbCI6InVzZXJAZXhhbXBsZS5jb20iLCJpYXQiOjE3MDc1MjgwMDAsImV4cCI6MTcwNzUyODkwMH0.SIGNATURE",
    "expiresIn": 900
  },
  "meta": {
    "timestamp": "2026-02-10T12:00:00Z",
    "request_id": "req-abc123"
  },
  "error": null
}
```

**Frontend handling**:
- Extract token from response
- Browser automatically stores in httpOnly cookie (Set-Cookie header)
- Redirect to /dashboard
- Set isAuthenticated = true in AuthContext

### Error Responses

**400 Bad Request** (Invalid input):
```json
{
  "data": null,
  "meta": {
    "timestamp": "2026-02-10T12:00:00Z",
    "request_id": "req-abc123"
  },
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Validation error",
    "details": {
      "email": ["Invalid email format"],
      "password": ["Password must be at least 8 characters"]
    }
  }
}
```

**409 Conflict** (Email already registered):
```json
{
  "data": null,
  "meta": { ... },
  "error": {
    "code": "EMAIL_EXISTS",
    "message": "Email already registered",
    "details": null
  }
}
```

**Frontend handling**:
- Extract error message and display in UI
- For field-level errors: show next to form fields
- Do NOT submit form again
- Allow user to correct and retry

---

## Signin Endpoint

**URL**: `POST /api/v1/auth/signin`

**Purpose**: Authenticate user and issue JWT token

### Request

**Headers**:
```
Content-Type: application/json
```

**Body** (JSON):
```json
{
  "email": "user@example.com",
  "password": "SecurePass123"
}
```

**Validation** (Client-side pre-checks):
- Email: Non-empty (basic format check optional)
- Password: Non-empty

### Response

**Success (200 OK)**:
```json
{
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "user@example.com",
    "name": "John Doe",
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "expiresIn": 900
  },
  "meta": { ... },
  "error": null
}
```

**Frontend handling**:
- Extract token and store in cookie
- Redirect to /dashboard
- Set isAuthenticated = true

### Error Responses

**401 Unauthorized** (Invalid credentials):
```json
{
  "data": null,
  "meta": { ... },
  "error": {
    "code": "INVALID_CREDENTIALS",
    "message": "Invalid email or password",
    "details": null
  }
}
```

**Important**: Generic message for both "email not found" and "wrong password" (prevents user enumeration)

**Frontend handling**:
- Display error: "Invalid email or password"
- Do NOT specify which field failed
- Allow user to retry

---

## Signout Endpoint

**URL**: `POST /api/v1/auth/signout`

**Purpose**: Invalidate user session (clear backend state if any)

### Request

**Headers**:
```
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

**Body**: Empty or `{}`

### Response

**Success (200 OK)**:
```json
{
  "data": { "message": "Signed out successfully" },
  "meta": { ... },
  "error": null
}
```

**Frontend handling**:
- Clear JWT token from cookie: `document.cookie = 'token=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;'`
- Clear user from AuthContext
- Redirect to /signin
- Set isAuthenticated = false

### Error Responses

**401 Unauthorized** (Missing or invalid token):
```json
{
  "data": null,
  "meta": { ... },
  "error": {
    "code": "UNAUTHORIZED",
    "message": "Missing or invalid authentication token",
    "details": null
  }
}
```

**Frontend handling**:
- Token already invalid (expired)
- Clear local state anyway
- Redirect to /signin

---

## Frontend API Wrapper Implementation

**File**: `src/lib/api.ts`

```typescript
export async function signup(
  email: string,
  password: string,
  name: string
): Promise<{ id: string; email: string; name: string; token: string; expiresIn: number }> {
  const response = await apiCall<SignupResponse>(
    '/api/v1/auth/signup',
    {
      method: 'POST',
      body: JSON.stringify({ email, password, name }),
    }
  );
  return response.data;
}

export async function signin(
  email: string,
  password: string
): Promise<{ id: string; email: string; name: string; token: string; expiresIn: number }> {
  const response = await apiCall<SigninResponse>(
    '/api/v1/auth/signin',
    {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    }
  );
  return response.data;
}

export async function signout(): Promise<void> {
  await apiCall<SignoutResponse>(
    '/api/v1/auth/signout',
    {
      method: 'POST',
      requiresAuth: true,
    }
  );
}
```

---

## Error Code Reference

| Code | HTTP Status | Meaning | Frontend Action |
|------|-------------|---------|-----------------|
| VALIDATION_ERROR | 400 | Invalid input format | Show field-level errors |
| EMAIL_EXISTS | 409 | Email already registered | Show "Email already registered" |
| INVALID_CREDENTIALS | 401 | Wrong email or password | Show "Invalid email or password" |
| UNAUTHORIZED | 401 | Missing or invalid token | Redirect to signin |
| SERVER_ERROR | 500 | Backend error | Show "Something went wrong" |

---

## Token Lifecycle

1. **Issuance**: User signs up or signs in → Backend generates JWT → Sent in Set-Cookie header
2. **Storage**: Browser stores in httpOnly cookie automatically
3. **Attachment**: All API requests include Authorization: Bearer <token> (automatic)
4. **Validation**: Backend verifies JWT signature using shared secret
5. **Expiration**: Token valid for 15 minutes from issuance
6. **Refresh**: User signs in again to get new token
7. **Revocation**: User signs out → Cookie cleared → Token no longer sent

---

## Security Considerations

- **No password echoed**: Responses never include plaintext passwords
- **Generic errors**: No distinction between "email not found" vs "wrong password"
- **HTTPS only**: Cookies with Secure flag require HTTPS in production
- **HttpOnly flag**: JavaScript cannot access cookie (XSS protection)
- **SameSite**: Cookie sent only to same-site requests (CSRF protection)
- **Expiration**: Short-lived tokens (15 min) limit damage from token theft

---

## Testing Scenarios

### Signup Flow
- [ ] Valid signup: Create account, receive token, redirect to dashboard
- [ ] Duplicate email: 409 error, show message "Email already registered"
- [ ] Invalid email: 400 error, show "Invalid email format"
- [ ] Weak password: 400 error, show "Password must be 8+ characters..."
- [ ] Empty fields: Client-side validation prevents submission

### Signin Flow
- [ ] Valid signin: Authenticate, receive token, redirect to dashboard
- [ ] Wrong password: 401 error, show "Invalid email or password"
- [ ] Email not found: 401 error, show "Invalid email or password"
- [ ] Empty fields: Client-side validation prevents submission

### Signout Flow
- [ ] Valid signout: Clear token, redirect to signin
- [ ] Already signed out: Cookie empty, redirect to signin anyway

### Token Management
- [ ] Token persists after page refresh
- [ ] Token expires after 15 minutes → subsequent request returns 401 → redirect to signin
- [ ] Multiple requests: All include Authorization header automatically
