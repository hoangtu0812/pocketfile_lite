"""
Versions API routes.
"""

from fastapi import APIRouter

from app.core.dependencies import AdminUser, CurrentUser, DbDep
from app.schemas.common import BaseResponse
from app.schemas.version import VersionCreate, VersionRead
from app.services.version import VersionService

router = APIRouter(prefix="/projects", tags=["Versions"])


@router.get("/{project_id}/versions", response_model=BaseResponse[list[VersionRead]])
def list_versions(project_id: int, db: DbDep, _user: CurrentUser):
    """List all versions for a project."""
    service = VersionService(db)
    versions = service.list_versions(project_id)
    return BaseResponse.ok(versions)


@router.post("/{project_id}/versions", response_model=BaseResponse[VersionRead], status_code=201)
def create_version(project_id: int, payload: VersionCreate, db: DbDep, _admin: AdminUser):
    """Create a new version for a project. Admin only."""
    service = VersionService(db)
    version = service.create_version(project_id, payload)
    return BaseResponse.ok(version)
