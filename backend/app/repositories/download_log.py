"""
Repository for FileDownloadLog operations.
"""

from datetime import datetime, timedelta

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.apk_file import APKFile
from app.models.download_log import FileDownloadLog
from app.repositories.base import BaseRepository


class DownloadLogRepository(BaseRepository[FileDownloadLog]):
    def __init__(self, db: Session):
        super().__init__(FileDownloadLog, db)

    def log_download(self, file_id: int, ip_address: str) -> FileDownloadLog:
        """Create a new download record."""
        log_entry = FileDownloadLog(file_id=file_id, ip_address=ip_address)
        return self.create(log_entry)

    def get_recent_downloads(self, limit: int = 10) -> list[tuple[FileDownloadLog, str]]:
        """Get the most recent downloads along with their filename."""
        return (
            self.db.query(FileDownloadLog, APKFile.filename)
            .join(APKFile, APKFile.id == FileDownloadLog.file_id)
            .order_by(FileDownloadLog.downloaded_at.desc())
            .limit(limit)
            .all()
        )

    def get_download_trends(self, days: int = 30) -> list[tuple[str, int]]:
        """
        Get daily download counts for the last `days` days.
        Returns a list of (date_string, count).
        """
        # Calculate the threshold date
        threshold = datetime.now() - timedelta(days=days)
        
        # We need to truncate the datetime to just the date part.
        # In PostgreSQL, `func.date_trunc('day', column)` works well,
        # but pure SQLAlchemy can use `func.cast(column, Date)` depending on dialect.
        # Since we use Postgres, `func.date()` is also available in standard SQL.
        date_expr = func.date(FileDownloadLog.downloaded_at)

        results = (
            self.db.query(date_expr.label('day'), func.count(FileDownloadLog.id).label('count'))
            .filter(FileDownloadLog.downloaded_at >= threshold)
            .group_by(date_expr)
            .order_by(date_expr)
            .all()
        )
        
        # Convert date to string YYYY-MM-DD
        return [(str(row[0]), row[1]) for row in results]
