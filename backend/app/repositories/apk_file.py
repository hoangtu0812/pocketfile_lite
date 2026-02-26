"""
APKFile repository — database access for APK files.
"""

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.apk_file import APKFile
from app.repositories.base import BaseRepository


class APKFileRepository(BaseRepository[APKFile]):
    def __init__(self, db: Session):
        super().__init__(APKFile, db)

    def get_by_version(self, version_id: int) -> list[APKFile]:
        return (
            self.db.query(APKFile)
            .filter(APKFile.version_id == version_id)
            .order_by(APKFile.uploaded_at.desc())
            .all()
        )

    def total_storage_bytes(self) -> int:
        result = self.db.query(func.sum(APKFile.file_size)).scalar()
        return result or 0

    def count_all(self) -> int:
        return self.db.query(APKFile).count()
