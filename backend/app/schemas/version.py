"""
Version Pydantic schemas.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class VersionCreate(BaseModel):
    version_string: str


class VersionRead(BaseModel):
    id: int
    version_string: str
    project_id: int
    created_at: datetime
    file_count: int = 0

    model_config = {"from_attributes": True}
