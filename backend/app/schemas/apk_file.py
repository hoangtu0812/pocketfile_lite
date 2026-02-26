"""
APK File Pydantic schemas.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class APKFileRead(BaseModel):
    id: int
    filename: str
    file_size: int
    version_id: int
    uploaded_by: Optional[int]
    uploaded_at: datetime

    model_config = {"from_attributes": True}


class APKFileDetail(APKFileRead):
    """Extended read with uploader username."""
    uploader_name: Optional[str] = None
