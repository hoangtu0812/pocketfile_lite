"""
Central API router: includes all route modules.
"""

from fastapi import APIRouter

from app.api.routes import auth, dashboard, files, projects, users, versions

api_router = APIRouter()

api_router.include_router(auth.router)
api_router.include_router(projects.router)
api_router.include_router(versions.router)
api_router.include_router(files.router)
api_router.include_router(dashboard.router)
api_router.include_router(users.router)
