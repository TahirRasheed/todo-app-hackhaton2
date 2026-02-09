"""Authentication endpoints (signup, signin, signout)"""
import re
from datetime import timedelta

from fastapi import APIRouter, HTTPException, Depends, Response
from sqlalchemy.ext.asyncio import AsyncSession

from backend.src.config import settings
from backend.src.db.session import get_session
from backend.src.schemas.user import UserCreate, UserResponse
from backend.src.security.jwt import create_access_token, create_refresh_token
from backend.src.services.user_service import UserService
from backend.src.utils.response import APIResponse


router = APIRouter(prefix="/auth", tags=["auth"])


def validate_email(email: str) -> bool:
    """Simple email validation"""
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return re.match(pattern, email) is not None


@router.post("/signup", status_code=201, response_model=APIResponse)
async def signup(
    user_data: UserCreate, response: Response, session: AsyncSession = Depends(get_session)
):
    """
    Register a new user

    Args:
        user_data: Email, password, and name
        response: FastAPI response object for setting cookies
        session: Database session

    Returns:
        APIResponse with UserResponse data and JWT token in Set-Cookie

    Raises:
        HTTPException 400: If email invalid, password weak, or email already exists
    """
    # Validate email format
    if not validate_email(user_data.email):
        raise HTTPException(
            status_code=400,
            detail=APIResponse.error("INVALID_EMAIL", "Email format is invalid").dict(),
        )

    # Validate password (min 8 chars)
    if len(user_data.password) < 8:
        raise HTTPException(
            status_code=400,
            detail=APIResponse.error(
                "WEAK_PASSWORD", "Password must be at least 8 characters"
            ).dict(),
        )

    # Create user
    try:
        user = await UserService.create_user(
            session, user_data.email, user_data.password, user_data.name
        )
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=APIResponse.error("EMAIL_EXISTS", str(e)).dict(),
        )

    # Create JWT tokens
    access_token = create_access_token(
        {"sub": str(user.id)}, expires_delta=timedelta(minutes=15)
    )
    refresh_token = create_refresh_token({"sub": str(user.id)})

    # Set JWT in httpOnly, Secure cookie
    response.set_cookie(
        key="jwt",
        value=access_token,
        httponly=True,
        secure=True,
        samesite="strict",
        max_age=900,  # 15 minutes
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite="strict",
        max_age=604800,  # 7 days
    )

    user_response = UserResponse.from_attributes(user)
    return APIResponse.success(user_response.dict())


@router.post("/signin", response_model=APIResponse)
async def signin(
    email: str, password: str, response: Response, session: AsyncSession = Depends(get_session)
):
    """
    Authenticate and sign in user

    Args:
        email: User email
        password: User password
        response: FastAPI response object for setting cookies
        session: Database session

    Returns:
        APIResponse with UserResponse data and JWT token in Set-Cookie

    Raises:
        HTTPException 401: If credentials are invalid
    """
    try:
        user = await UserService.authenticate(session, email, password)
    except ValueError:
        raise HTTPException(
            status_code=401,
            detail=APIResponse.error("INVALID_CREDENTIALS", "Invalid credentials").dict(),
        )

    # Create JWT tokens
    access_token = create_access_token(
        {"sub": str(user.id)}, expires_delta=timedelta(minutes=15)
    )
    refresh_token = create_refresh_token({"sub": str(user.id)})

    # Set JWT in httpOnly, Secure cookie
    response.set_cookie(
        key="jwt",
        value=access_token,
        httponly=True,
        secure=True,
        samesite="strict",
        max_age=900,  # 15 minutes
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite="strict",
        max_age=604800,  # 7 days
    )

    user_response = UserResponse.from_attributes(user)
    return APIResponse.success(user_response.dict())


@router.post("/signout", response_model=APIResponse)
async def signout(response: Response):
    """
    Sign out user by clearing JWT cookie

    Args:
        response: FastAPI response object for clearing cookies

    Returns:
        APIResponse with empty data
    """
    # Clear JWT cookies
    response.delete_cookie(key="jwt", httponly=True, secure=True, samesite="strict")
    response.delete_cookie(
        key="refresh_token", httponly=True, secure=True, samesite="strict"
    )

    return APIResponse.success(None)
