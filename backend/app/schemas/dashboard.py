"""
Dashboard statistics schema.
"""

from datetime import datetime
from pydantic import BaseModel


class DashboardRecentDownload(BaseModel):
    ip_address: str
    filename: str
    downloaded_at: datetime


class DashboardDownloadTrend(BaseModel):
    date: str
    count: int


class DashboardStats(BaseModel):
    total_projects: int
    total_versions: int
    total_files: int
    total_storage_bytes: int
    total_storage_mb: float
    recent_downloads: list[DashboardRecentDownload]
    download_trends: list[DashboardDownloadTrend]
