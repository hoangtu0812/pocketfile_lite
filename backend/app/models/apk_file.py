"""
APKFile model — represents an uploaded APK file tied to a version.
"""

from datetime import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class APKFile(Base):
    __tablename__ = "apk_files"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    file_size: Mapped[int] = mapped_column(BigInteger, nullable=False)
    file_path: Mapped[str] = mapped_column(String(512), nullable=False)
    version_id: Mapped[int] = mapped_column(
        ForeignKey("versions.id", ondelete="CASCADE"), nullable=False, index=True
    )
    uploaded_by: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    uploaded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    version: Mapped["Version"] = relationship("Version", back_populates="apk_files")
    uploader: Mapped["User"] = relationship(
        "User", back_populates="uploaded_files", foreign_keys=[uploaded_by]
    )
    download_logs: Mapped[list["FileDownloadLog"]] = relationship(
        "FileDownloadLog", back_populates="apk_file", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<APKFile id={self.id} filename={self.filename}>"
