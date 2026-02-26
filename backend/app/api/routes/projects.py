"""
Projects API routes: CRUD for projects.
"""

from fastapi import APIRouter

from app.core.dependencies import AdminUser, CurrentUser, DbDep
from app.schemas.common import BaseResponse
from app.schemas.project import ProjectCreate, ProjectRead, ProjectUpdate
from app.services.project import ProjectService

router = APIRouter(prefix="/projects", tags=["Projects"])


@router.get("", response_model=BaseResponse[list[ProjectRead]])
def list_projects(db: DbDep, current_user: CurrentUser):
    """List all projects with version counts."""
    service = ProjectService(db)
    projects = service.list_projects(current_user)
    return BaseResponse.ok(projects)


@router.post("", response_model=BaseResponse[ProjectRead], status_code=201)
def create_project(payload: ProjectCreate, db: DbDep, _admin: AdminUser):
    """Create a new project. Admin only."""
    service = ProjectService(db)
    project = service.create_project(payload)
    return BaseResponse.ok(project)


@router.put("/{project_id}", response_model=BaseResponse[ProjectRead])
def update_project(project_id: int, payload: ProjectUpdate, db: DbDep, _admin: AdminUser):
    """Update project name/description. Admin only."""
    service = ProjectService(db)
    project = service.update_project(project_id, payload)
    return BaseResponse.ok(project)


@router.delete("/{project_id}", response_model=BaseResponse[None])
def delete_project(project_id: int, db: DbDep, _admin: AdminUser):
    """Delete a project and all its versions/files. Admin only."""
    service = ProjectService(db)
    service.delete_project(project_id)
    return BaseResponse.ok(None)
