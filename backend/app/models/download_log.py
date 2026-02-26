"""
Download Log model — tracking APK file downloads.
"""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class FileDownloadLog(Base):
    """Tracks a single download event of an APK file."""

    __tablename__ = "file_download_logs"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    file_id: Mapped[int] = mapped_column(
        ForeignKey("apk_files.id", ondelete="CASCADE"), nullable=False, index=True
    )
    ip_address: Mapped[str] = mapped_column(String(45), nullable=False)
    downloaded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False, index=True
    )

    # Relationship back to the APK file
    apk_file: Mapped["APKFile"] = relationship("APKFile", back_populates="download_logs")

    def __repr__(self) -> str:
        return f"<FileDownloadLog id={self.id} file_id={self.file_id} ip={self.ip_address}>"
