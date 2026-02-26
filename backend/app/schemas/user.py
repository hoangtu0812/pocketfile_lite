"""
User Pydantic schemas for request validation and response serialization.
"""

from datetime import datetime

from pydantic import BaseModel, EmailStr, field_validator

from app.models.user import UserRole


class UserCreate(BaseModel):
    """Schema for creating a new user (admin only)."""

    username: str
    email: EmailStr
    password: str
    role: UserRole = UserRole.USER

    @field_validator("username")
    @classmethod
    def username_alphanumeric(cls, v: str) -> str:
        if not v.replace("_", "").replace("-", "").isalnum():
            raise ValueError("Username must be alphanumeric (underscores/hyphens allowed)")
        return v.lower()

    @field_validator("password")
    @classmethod
    def password_min_length(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        return v


class UserUpdatePassword(BaseModel):
    """Schema for updating a user's password (admin only)."""

    password: str

    @field_validator("password")
    @classmethod
    def password_min_length(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        return v

class UserProjectAssign(BaseModel):
    """Schema for assigning projects to a user."""
    project_ids: list[int]


class UserRead(BaseModel):
    """Schema for reading user data (no password)."""

    id: int
    username: str
    email: str
    role: UserRole
    created_at: datetime

    model_config = {"from_attributes": True}


class LoginRequest(BaseModel):
    """Login credentials."""

    username: str
    password: str


class TokenResponse(BaseModel):
    """JWT token response."""

    access_token: str
    token_type: str = "bearer"
    user: UserRead
