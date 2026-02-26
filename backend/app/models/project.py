"""
Project model — top-level grouping for APK versions.
"""

from datetime import datetime

from sqlalchemy import DateTime, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(128), unique=True, nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    versions: Mapped[list["Version"]] = relationship(
        "Version", back_populates="project", cascade="all, delete-orphan"
    )
    authorized_users: Mapped[list["User"]] = relationship(
        "User", secondary="user_project_access", back_populates="projects"
    )

    def __repr__(self) -> str:
        return f"<Project id={self.id} name={self.name}>"
