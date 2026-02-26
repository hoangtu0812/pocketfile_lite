"""
Project service: business logic for project management.
"""

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.project import Project
from app.models.user import User
from app.repositories.project import ProjectRepository
from app.schemas.project import ProjectCreate, ProjectRead, ProjectUpdate
from app.utils.logger import get_logger

logger = get_logger(__name__)


class ProjectService:
    def __init__(self, db: Session):
        self.repo = ProjectRepository(db)

    def list_projects(self, current_user: User) -> list[ProjectRead]:
        from app.models.user import UserRole

        if current_user.role == UserRole.ADMIN:
            rows = self.repo.get_all_with_version_count()
        else:
            rows = self.repo.get_all_with_version_count_by_user(current_user.id)
            
        result = []
        for project, version_count in rows:
            r = ProjectRead.model_validate(project)
            r.version_count = version_count
            result.append(r)
        return result

    def get_project(self, project_id: int) -> ProjectRead:
        project = self.repo.get(project_id)
        if not project:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
        return ProjectRead.model_validate(project)

    def create_project(self, payload: ProjectCreate) -> ProjectRead:
        if self.repo.get_by_name(payload.name):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Project '{payload.name}' already exists",
            )
        project = Project(name=payload.name, description=payload.description)
        project = self.repo.create(project)
        logger.info(f"Created project '{project.name}'")
        return ProjectRead.model_validate(project)

    def update_project(self, project_id: int, payload: ProjectUpdate) -> ProjectRead:
        project = self.repo.get(project_id)
        if not project:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
        if payload.name is not None:
            existing = self.repo.get_by_name(payload.name)
            if existing and existing.id != project_id:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Project name '{payload.name}' is already taken",
                )
            project.name = payload.name
        if payload.description is not None:
            project.description = payload.description
        project = self.repo.update(project)
        logger.info(f"Updated project id={project_id}")
        return ProjectRead.model_validate(project)

    def delete_project(self, project_id: int) -> None:
        project = self.repo.get(project_id)
        if not project:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
        self.repo.delete(project)
        logger.info(f"Deleted project id={project_id}")
