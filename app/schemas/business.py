"""
BILI Master System - Business Schemas
"""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class BusinessResponse(BaseModel):
    id: str
    google_place_id: str
    google_name: str
    display_name: str
    status: str
    is_claimed: bool
    latitude: float
    longitude: float
    google_category: Optional[str] = None
    google_rating: Optional[float] = None
    
    class Config:
        from_attributes = True


class BusinessListResponse(BaseModel):
    businesses: List[BusinessResponse]
    total: int
