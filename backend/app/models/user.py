"""
User model with role-based access control.
"""

import enum
from datetime import datetime

from sqlalchemy import DateTime, Enum, String, func, Table, ForeignKey, Column, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class UserRole(str, enum.Enum):
    ADMIN = "ADMIN"
    USER = "USER"


# Intermediate table for many-to-many relationship mapping Users and Projects.
user_project_access = Table(
    "user_project_access",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column("project_id", Integer, ForeignKey("projects.id", ondelete="CASCADE"), primary_key=True),
)


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole), default=UserRole.USER, nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    uploaded_files: Mapped[list["APKFile"]] = relationship(
        "APKFile", back_populates="uploader", foreign_keys="APKFile.uploaded_by"
    )
    projects: Mapped[list["Project"]] = relationship(
        "Project", secondary=user_project_access, back_populates="authorized_users"
    )

    def __repr__(self) -> str:
        return f"<User id={self.id} username={self.username} role={self.role}>"
