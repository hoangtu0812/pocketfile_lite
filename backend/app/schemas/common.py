"""
Common Pydantic schemas: standardized API response wrapper.
"""

from typing import Generic, Optional, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class BaseResponse(BaseModel, Generic[T]):
    """Standardized API response envelope."""

    success: bool = True
    data: Optional[T] = None
    error: Optional[str] = None

    @classmethod
    def ok(cls, data: T) -> "BaseResponse[T]":
        return cls(success=True, data=data, error=None)

    @classmethod
    def fail(cls, error: str) -> "BaseResponse[None]":
        return cls(success=False, data=None, error=error)


class PaginatedData(BaseModel, Generic[T]):
    """Wrapper for paginated list responses."""

    items: list[T]
    total: int
