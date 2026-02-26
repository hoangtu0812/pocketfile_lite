"""
Dashboard service: aggregate statistics.
"""

from sqlalchemy.orm import Session

from app.repositories.apk_file import APKFileRepository
from app.repositories.download_log import DownloadLogRepository
from app.repositories.project import ProjectRepository
from app.repositories.version import VersionRepository
from app.schemas.dashboard import DashboardDownloadTrend, DashboardRecentDownload, DashboardStats


class DashboardService:
    def __init__(self, db: Session):
        self.project_repo = ProjectRepository(db)
        self.version_repo = VersionRepository(db)
        self.file_repo = APKFileRepository(db)
        self.log_repo = DownloadLogRepository(db)

    def get_stats(self) -> DashboardStats:
        total_projects = self.project_repo.count()
        total_versions = self.version_repo.count()
        total_files = self.file_repo.count_all()
        total_storage_bytes = self.file_repo.total_storage_bytes()
        
        recent_log_rows = self.log_repo.get_recent_downloads(limit=10)
        recent_downloads = [
            DashboardRecentDownload(
                ip_address=log.ip_address,
                filename=filename,
                downloaded_at=log.downloaded_at
            ) for log, filename in recent_log_rows
        ]
        
        trend_rows = self.log_repo.get_download_trends(days=30)
        download_trends = [
            DashboardDownloadTrend(date=date_str, count=count)
            for date_str, count in trend_rows
        ]

        return DashboardStats(
            total_projects=total_projects,
            total_versions=total_versions,
            total_files=total_files,
            total_storage_bytes=total_storage_bytes,
            total_storage_mb=round(total_storage_bytes / (1024 * 1024), 2),
            recent_downloads=recent_downloads,
            download_trends=download_trends,
        )
