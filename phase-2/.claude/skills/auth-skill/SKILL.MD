---
name: auth-skill
description: Implement authentication systems including signup, signin, password hashing, JWT tokens, and Better Auth integration.
---

# Authentication Skill

## Instructions

1. **User Registration (Signup)**
   - Collect user name, email, password
   - Validate input fields
   - Ensure email uniqueness
   - Hash password before storing
   - Save user in database

2. **User Login (Signin)**
   - Accept email + password
   - Verify user exists
   - Compare hashed password
   - Generate authentication token
   - Return secure session / JWT

3. **Password Hashing**
   - Never store plain passwords
   - Use bcrypt / argon2 hashing
   - Apply salting automatically
   - Store only hashed value
   - Validate using hash comparison

4. **JWT Token Handling**
   - Generate JWT on login
   - Include user_id + email claims
   - Sign with secret key
   - Set expiration (e.g., 7 days)
   - Verify token on protected routes

5. **Better Auth Integration**
   - Configure Better Auth in frontend
   - Enable JWT plugin
   - Issue JWT on successful login
   - Share secret with backend
   - Attach token in API headers

---

## Authentication Flow

1. User signs up → password hashed → stored in DB  
2. User signs in → password verified  
3. Backend generates JWT  
4. Frontend stores session/token  
5. Token sent in `Authorization: Bearer <token>`  
6. Backend verifies token → allows access  

---

## Best Practices

- Hash passwords using bcrypt/argon2 only
- Never expose JWT secret
- Use HTTPS for all auth routes
- Set token expiry
- Implement refresh tokens if needed
- Validate all inputs
- Protect against brute force attacks
- Use role-based access if required

---

## Example API Structure

```http
POST /api/auth/signup
POST /api/auth/signin
GET  /api/auth/me
POST /api/auth/logout
