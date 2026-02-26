"""
Project Pydantic schemas.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = None


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


class ProjectRead(BaseModel):
    id: int
    name: str
    description: Optional[str]
    created_at: datetime
    version_count: int = 0

    model_config = {"from_attributes": True}
