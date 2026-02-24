"""
BILI Master System - Radar Schemas
"""
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class RadarUserResponse(BaseModel):
    user_id: str
    latitude: float
    longitude: float
    status: str
    credit_balance: float
    last_seen: Optional[str] = None
    display_name: Optional[str] = None
    
    class Config:
        from_attributes = True


class RadarResponse(BaseModel):
    users: List[RadarUserResponse]
    total: int
    timestamp: str
