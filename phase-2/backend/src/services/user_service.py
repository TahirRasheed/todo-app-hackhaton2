"""User service for account management"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.src.models.user import User
from backend.src.schemas.user import UserCreate
from backend.src.security.password import hash_password, verify_password


class UserService:
    """Service for user operations (signup, signin, profile management)"""

    @staticmethod
    async def create_user(
        session: AsyncSession, email: str, password: str, name: str
    ) -> User:
        """
        Create a new user with hashed password

        Args:
            session: Database session
            email: User email (will be validated for uniqueness)
            password: Plaintext password (will be hashed)
            name: User display name

        Returns:
            Created User object

        Raises:
            ValueError: If email already exists
        """
        # Check if email already exists
        existing_user = await UserService.get_user_by_email(session, email)
        if existing_user:
            raise ValueError(f"Email {email} already registered")

        # Hash password and create user
        password_hash = hash_password(password)
        user = User(email=email, password_hash=password_hash, name=name)
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user

    @staticmethod
    async def get_user_by_email(session: AsyncSession, email: str) -> User | None:
        """
        Retrieve user by email address

        Args:
            session: Database session
            email: Email to search for

        Returns:
            User object if found, None otherwise
        """
        result = await session.execute(select(User).where(User.email == email))
        return result.scalars().first()

    @staticmethod
    async def get_user_by_id(session: AsyncSession, user_id: str) -> User | None:
        """
        Retrieve user by ID

        Args:
            session: Database session
            user_id: UUID of user

        Returns:
            User object if found, None otherwise
        """
        result = await session.execute(select(User).where(User.id == user_id))
        return result.scalars().first()

    @staticmethod
    async def authenticate(
        session: AsyncSession, email: str, password: str
    ) -> User:
        """
        Authenticate user with email and password.

        Security:
        - Always performs password verification to prevent timing attacks
        - Returns same error for both "email not found" and "wrong password"
        - Uses constant-time password comparison via bcrypt

        Args:
            session: Database session
            email: User email
            password: Plaintext password to verify

        Returns:
            Authenticated User object

        Raises:
            ValueError: If authentication fails (invalid email or password)
        """
        user = await UserService.get_user_by_email(session, email)

        # Security: Always verify password even if user doesn't exist
        # This prevents timing attacks that could reveal if email exists
        if user:
            password_valid = verify_password(password, user.password_hash)
        else:
            # Run password verification against dummy hash to maintain constant time
            # Use a known bcrypt hash to ensure timing is consistent
            dummy_hash = "$2b$10$dummyhashfortimingatttackpreventionxxx1234567890abcdefghij"
            verify_password(password, dummy_hash)
            password_valid = False

        if not user or not password_valid:
            raise ValueError("Invalid credentials")

        return user
