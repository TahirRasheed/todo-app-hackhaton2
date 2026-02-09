"""Authentication endpoints (signup, signin, signout)"""
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.session import get_session
from src.schemas.user import UserSignup, UserSignin, UserTokenResponse
from src.security.jwt import create_access_token, verify_token
from src.security.password import hash_password, validate_password_strength
from src.services.user_service import UserService


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup", status_code=status.HTTP_201_CREATED, response_model=UserTokenResponse)
async def signup(
    user_data: UserSignup,
    session: AsyncSession = Depends(get_session)
):
    """
    Register a new user with JWT authentication.

    Security:
    - Password hashed with bcrypt (cost 10)
    - JWT token issued with 900 second expiration
    - Token contains user_id (sub) and email claims

    Args:
        user_data: UserSignup schema (email, password, name)
        session: Database session

    Returns:
        UserTokenResponse with user data + JWT token + expiresIn

    Raises:
        HTTPException 400: Invalid email format or weak password
        HTTPException 409: Email already exists
        HTTPException 500: Server error
    """
    # Validate password strength
    is_valid, message = validate_password_strength(user_data.password)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message
        )

    # Create user (will raise ValueError if email exists)
    try:
        user = await UserService.create_user(
            session=session,
            email=user_data.email,
            password=user_data.password,
            name=user_data.name or ""
        )
    except ValueError as e:
        # Email already exists - return 409 Conflict
        error_message = str(e)
        if "already registered" in error_message.lower():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered"
            )
        # Other validation errors - return 400
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_message
        )
    except Exception as e:
        # Unexpected server error
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user account"
        )

    # Generate JWT token (900 seconds = 15 minutes)
    try:
        token, expires_in = create_access_token(
            user_id=str(user.id),
            email=user.email
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate authentication token"
        )

    # Return user data + token
    return UserTokenResponse(
        id=str(user.id),
        email=user.email,
        name=user.name,
        token=token,
        expiresIn=expires_in
    )


@router.post("/signin", status_code=status.HTTP_200_OK, response_model=UserTokenResponse)
async def signin(
    user_data: UserSignin,
    session: AsyncSession = Depends(get_session)
):
    """
    Authenticate user and issue JWT token.

    Security:
    - Returns generic error message for both "email not found" and "wrong password"
      to prevent user enumeration attacks
    - Uses constant-time password comparison via bcrypt to prevent timing attacks
    - JWT token issued with 900 second expiration

    Args:
        user_data: UserSignin schema (email, password)
        session: Database session

    Returns:
        UserTokenResponse with user data + JWT token + expiresIn

    Raises:
        HTTPException 401: Invalid email or password (generic message)
        HTTPException 500: Server error
    """
    try:
        user = await UserService.authenticate(
            session=session,
            email=user_data.email,
            password=user_data.password
        )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication failed"
        )

    # Generate JWT token
    try:
        token, expires_in = create_access_token(
            user_id=str(user.id),
            email=user.email
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate authentication token"
        )

    return UserTokenResponse(
        id=str(user.id),
        email=user.email,
        name=user.name,
        token=token,
        expiresIn=expires_in
    )


@router.post("/signout", status_code=status.HTTP_200_OK)
async def signout(credentials: HTTPAuthCredentials = Depends(HTTPBearer())):
    """
    Sign out user - validates JWT token and returns success.

    Since we use stateless JWT tokens, this endpoint validates the token
    and returns success. Client is responsible for removing the token from storage.

    Security:
    - Requires valid JWT token in Authorization: Bearer <token> header
    - Verifies token signature and expiration
    - Returns 401 if token is invalid or missing

    Args:
        credentials: JWT credentials from Authorization header

    Returns:
        Success message: {"message": "Signed out successfully"}

    Raises:
        HTTPException 401: Invalid or missing token
    """
    if not credentials or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authentication token",
            headers={"WWW-Authenticate": "Bearer"}
        )

    # Verify token is valid
    try:
        verify_token(credentials.credentials)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"}
        )

    return {"message": "Signed out successfully"}
