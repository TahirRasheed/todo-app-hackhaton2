"""Database session management"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlmodel import SQLModel

from config import settings

# Convert PostgreSQL URL to async format (psycopg required)
DATABASE_URL = settings.DATABASE_URL.replace("postgresql://", "postgresql+psycopg://")

# Create async engine
engine = create_async_engine(
    DATABASE_URL,
    echo=settings.DEBUG,
    future=True,
)

# Create async session factory
async_session = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_session():
    """Dependency to get database session"""
    async with async_session() as session:
        yield session


async def init_db():
    """Initialize database (create tables)"""
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
