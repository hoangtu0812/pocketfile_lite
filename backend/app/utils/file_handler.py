"""
File handling utilities: validation, sanitization, storage path management.
"""

import os
import re
import uuid
from pathlib import Path

from fastapi import HTTPException, UploadFile, status

from app.core.config import get_settings
from app.utils.logger import get_logger

settings = get_settings()
logger = get_logger(__name__)

ALLOWED_EXTENSION = ".apk"


def validate_apk_file(file: UploadFile) -> None:
    """
    Validate that the uploaded file is an APK.

    Raises:
        HTTPException 400 if file extension is invalid.
    """
    if not file.filename or not file.filename.lower().endswith(ALLOWED_EXTENSION):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only .apk files are allowed",
        )


def sanitize_filename(filename: str) -> str:
    """Remove unsafe characters from a filename."""
    name = Path(filename).stem
    ext = Path(filename).suffix
    safe_name = re.sub(r"[^\w\-.]", "_", name)
    return f"{safe_name}{ext}"


def build_storage_path(project_name: str, version_string: str, filename: str) -> Path:
    """
    Construct the storage path for an APK file.

    Path structure: STORAGE_PATH / project_name / version_string / filename
    """
    safe_project = re.sub(r"[^\w\-]", "_", project_name)
    safe_version = re.sub(r"[^\w\-.]", "_", version_string)
    safe_filename = sanitize_filename(filename)
    return Path(settings.STORAGE_PATH) / safe_project / safe_version / safe_filename


def ensure_directory(path: Path) -> None:
    """Create directory and all parents if they don't exist."""
    path.mkdir(parents=True, exist_ok=True)


def get_file_size(path: Path) -> int:
    """Return file size in bytes."""
    return path.stat().st_size


def delete_file(file_path: str) -> None:
    """Delete a file from the filesystem, ignoring missing files."""
    try:
        path = Path(file_path)
        if path.exists():
            path.unlink()
            logger.info(f"Deleted file: {file_path}")
    except OSError as e:
        logger.error(f"Failed to delete file {file_path}: {e}")
