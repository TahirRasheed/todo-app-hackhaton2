"""FastAPI Application"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from config import settings
from backend.src.api.v1.routers import router as v1_router
from backend.src.db.session import init_db, engine

# Configure logging
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """FastAPI lifespan context manager for startup and shutdown"""
    # Startup
    logger.info("🚀 Starting Todo API...")
    logger.info(f"📊 Environment: {settings.ENVIRONMENT}")
    logger.info(f"🔧 Debug mode: {settings.DEBUG}")

    # Initialize database schema
    try:
        logger.info("📦 Initializing database schema...")
        await init_db()
        logger.info("✅ Database schema initialized successfully")
    except Exception as e:
        logger.error(f"❌ Failed to initialize database: {str(e)}")
        raise

    yield

    # Shutdown
    logger.info("🛑 Shutting down Todo API...")
    await engine.dispose()
    logger.info("✅ Cleanup complete")


# Create FastAPI app with lifespan
app = FastAPI(
    title="Todo API",
    version="0.1.0",
    description="Phase II Todo Full-Stack Web Application",
    debug=settings.DEBUG,
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(v1_router)


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok", "environment": settings.ENVIRONMENT}


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Todo API - Phase II",
        "version": "0.1.0",
        "docs": "/docs"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
    )
