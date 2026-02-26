"""
Version repository — database access for versions.
"""

from typing import Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.apk_file import APKFile
from app.models.version import Version
from app.repositories.base import BaseRepository


class VersionRepository(BaseRepository[Version]):
    def __init__(self, db: Session):
        super().__init__(Version, db)

    def get_by_project(self, project_id: int) -> list[Version]:
        return (
            self.db.query(Version)
            .filter(Version.project_id == project_id)
            .order_by(Version.created_at.desc())
            .all()
        )

    def get_by_project_and_string(
        self, project_id: int, version_string: str
    ) -> Optional[Version]:
        return (
            self.db.query(Version)
            .filter(
                Version.project_id == project_id,
                Version.version_string == version_string,
            )
            .first()
        )

    def get_with_file_counts(self, project_id: int) -> list[tuple[Version, int]]:
        return (
            self.db.query(Version, func.count(APKFile.id).label("file_count"))
            .outerjoin(APKFile, APKFile.version_id == Version.id)
            .filter(Version.project_id == project_id)
            .group_by(Version.id)
            .order_by(Version.created_at.desc())
            .all()
        )
