"""
BILI Master System - Post Schemas
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class PostResponse(BaseModel):
    id: str
    owner_id: str
    post_type: str
    media_type: str
    title: Optional[str] = None
    description: Optional[str] = None
    media_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    latitude: float
    longitude: float
    radius_km: float
    is_commercial: bool
    category: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True
