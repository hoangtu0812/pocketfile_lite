"""
Models package — import all models to ensure they are registered with SQLAlchemy.
"""

from app.models.apk_file import APKFile
from app.models.download_log import FileDownloadLog
from app.models.project import Project
from app.models.user import User, UserRole
from app.models.version import Version

__all__ = ["User", "UserRole", "Project", "Version", "APKFile", "FileDownloadLog"]
