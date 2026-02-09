"""API v1 routers - consolidates all endpoint imports"""
from fastapi import APIRouter

from backend.src.api.v1.auth import router as auth_router
from backend.src.api.v1.tasks import router as tasks_router

# Create main v1 router
router = APIRouter(prefix="/api/v1")

# Include auth router
router.include_router(auth_router)

# Include tasks router
router.include_router(tasks_router)

# Additional routers will be added here as phases progress
# router.include_router(users_router)
