"""
Storage service: handle file I/O on disk.
"""

from pathlib import Path

from fastapi import HTTPException, UploadFile, status

from app.core.config import get_settings
from app.utils.file_handler import build_storage_path, ensure_directory, validate_apk_file
from app.utils.logger import get_logger

settings = get_settings()
logger = get_logger(__name__)

CHUNK_SIZE = 1024 * 1024  # 1 MB


class StorageService:
    async def save_apk(
        self,
        file: UploadFile,
        project_name: str,
        version_string: str,
    ) -> tuple[Path, int]:
        """
        Validate and save an APK file to disk.

        Returns:
            Tuple of (absolute_path, file_size_bytes).

        Raises:
            HTTPException 400 for invalid file type.
            HTTPException 413 if file exceeds MAX_UPLOAD_SIZE.
        """
        validate_apk_file(file)

        dest_path = build_storage_path(project_name, version_string, file.filename)
        ensure_directory(dest_path.parent)

        total_bytes = 0

        try:
            with open(dest_path, "wb") as out_file:
                while chunk := await file.read(CHUNK_SIZE):
                    total_bytes += len(chunk)
                    if total_bytes > settings.MAX_UPLOAD_SIZE:
                        out_file.close()
                        dest_path.unlink(missing_ok=True)
                        raise HTTPException(
                            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                            detail=f"File exceeds maximum upload size of {settings.MAX_UPLOAD_SIZE // (1024*1024)} MB",
                        )
                    out_file.write(chunk)
        except HTTPException:
            raise
        except Exception as e:
            dest_path.unlink(missing_ok=True)
            logger.error(f"Failed to save file: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to save file",
            )

        logger.info(f"Saved APK: {dest_path} ({total_bytes} bytes)")
        return dest_path, total_bytes
