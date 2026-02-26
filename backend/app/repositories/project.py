"""
Project repository — database access for projects.
"""

from typing import Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.project import Project
from app.models.version import Version
from app.repositories.base import BaseRepository


class ProjectRepository(BaseRepository[Project]):
    def __init__(self, db: Session):
        super().__init__(Project, db)

    def get_by_name(self, name: str) -> Optional[Project]:
        return self.db.query(Project).filter(Project.name == name).first()

    def get_all_with_version_count(self) -> list[tuple[Project, int]]:
        return (
            self.db.query(Project, func.count(Version.id).label("version_count"))
            .outerjoin(Version, Version.project_id == Project.id)
            .group_by(Project.id)
            .order_by(Project.name)
            .all()
        )

    def get_all_with_version_count_by_user(self, user_id: int) -> list[tuple[Project, int]]:
        from app.models.user import user_project_access
        return (
            self.db.query(Project, func.count(Version.id).label("version_count"))
            .join(user_project_access, user_project_access.c.project_id == Project.id)
            .filter(user_project_access.c.user_id == user_id)
            .outerjoin(Version, Version.project_id == Project.id)
            .group_by(Project.id)
            .order_by(Project.name)
            .all()
        )
