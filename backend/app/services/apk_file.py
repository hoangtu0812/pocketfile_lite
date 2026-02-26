"""
APK file service: upload, list, download, delete.
"""

from pathlib import Path

from fastapi import HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.models.apk_file import APKFile
from app.models.user import User
from app.repositories.apk_file import APKFileRepository
from app.repositories.version import VersionRepository
from app.schemas.apk_file import APKFileDetail, APKFileRead
from app.services.storage import StorageService
from app.utils.file_handler import delete_file
from app.utils.logger import get_logger

logger = get_logger(__name__)


class APKFileService:
    def __init__(self, db: Session):
        self.repo = APKFileRepository(db)
        self.version_repo = VersionRepository(db)
        self.storage = StorageService()

    def _get_version_or_404(self, version_id: int):
        version = self.version_repo.get(version_id)
        if not version:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Version not found")
        return version

    async def upload_apk(
        self, version_id: int, file: UploadFile, current_user: User
    ) -> APKFileRead:
        version = self._get_version_or_404(version_id)
        project = version.project

        dest_path, file_size = await self.storage.save_apk(
            file, project.name, version.version_string
        )

        apk = APKFile(
            filename=dest_path.name,
            file_size=file_size,
            file_path=str(dest_path),
            version_id=version_id,
            uploaded_by=current_user.id,
        )
        apk = self.repo.create(apk)
        logger.info(f"Uploaded APK id={apk.id} by user_id={current_user.id}")
        return APKFileRead.model_validate(apk)

    def list_files(self, version_id: int) -> list[APKFileDetail]:
        self._get_version_or_404(version_id)
        files = self.repo.get_by_version(version_id)
        result = []
        for f in files:
            detail = APKFileDetail.model_validate(f)
            if f.uploader:
                detail.uploader_name = f.uploader.username
            result.append(detail)
        return result

    def download_file(self, file_id: int) -> FileResponse:
        apk = self.repo.get(file_id)
        if not apk:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")
        path = Path(apk.file_path)
        if not path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not found on storage",
            )
        return FileResponse(
            path=str(path),
            filename=apk.filename,
            media_type="application/vnd.android.package-archive",
        )

    def delete_file(self, file_id: int) -> None:
        apk = self.repo.get(file_id)
        if not apk:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")
        delete_file(apk.file_path)
        self.repo.delete(apk)
        logger.info(f"Deleted APK id={file_id}")
