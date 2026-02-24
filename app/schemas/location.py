"""
BILI Master System - Location Schemas
"""
from pydantic import BaseModel, Field
from typing import Optional


class LocationRequest(BaseModel):
    """Request for location detection/update"""
    user_id: str = Field(..., description="User ID")
    latitude: float = Field(..., ge=-90, le=90, description="GPS Latitude")
    longitude: float = Field(..., ge=-180, le=180, description="GPS Longitude")
    accuracy: Optional[float] = Field(None, description="GPS accuracy in meters")
    auto_detect: bool = Field(True, description="True if automatic detection on app entry")


class LocationResponse(BaseModel):
    """Response for location operations"""
    success: bool
    message: str
    user_id: str
    latitude: float
    longitude: float
    status: str
    should_appear_on_radar: bool
    distance_moved_km: Optional[float] = None
    timestamp: str


class BatchLocationUpdate(BaseModel):
    """Batch location update for multiple users"""
    updates: list[LocationRequest]


class NearbyUsersResponse(BaseModel):
    """Response for nearby users query"""
    users: list[dict]
    total: int
    center_latitude: float
    center_longitude: float
    radius_km: float
    timestamp: str
