"""
Version model — belongs to a Project, holds APK files.
"""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Version(Base):
    __tablename__ = "versions"
    __table_args__ = (
        UniqueConstraint("project_id", "version_string", name="uq_version_per_project"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    version_string: Mapped[str] = mapped_column(String(64), nullable=False)
    project_id: Mapped[int] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    project: Mapped["Project"] = relationship("Project", back_populates="versions")
    apk_files: Mapped[list["APKFile"]] = relationship(
        "APKFile", back_populates="version", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Version id={self.id} version={self.version_string} project_id={self.project_id}>"
