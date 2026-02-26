"""
Version service: business logic for version management.
"""

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.version import Version
from app.repositories.project import ProjectRepository
from app.repositories.version import VersionRepository
from app.schemas.version import VersionCreate, VersionRead
from app.utils.logger import get_logger

logger = get_logger(__name__)


class VersionService:
    def __init__(self, db: Session):
        self.repo = VersionRepository(db)
        self.project_repo = ProjectRepository(db)

    def list_versions(self, project_id: int) -> list[VersionRead]:
        if not self.project_repo.get(project_id):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
        rows = self.repo.get_with_file_counts(project_id)
        result = []
        for version, file_count in rows:
            r = VersionRead.model_validate(version)
            r.file_count = file_count
            result.append(r)
        return result

    def create_version(self, project_id: int, payload: VersionCreate) -> VersionRead:
        if not self.project_repo.get(project_id):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
        if self.repo.get_by_project_and_string(project_id, payload.version_string):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Version '{payload.version_string}' already exists for this project",
            )
        version = Version(version_string=payload.version_string, project_id=project_id)
        version = self.repo.create(version)
        logger.info(f"Created version '{version.version_string}' for project_id={project_id}")
        return VersionRead.model_validate(version)
