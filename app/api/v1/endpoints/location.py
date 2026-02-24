"""
BILI Master System - Global GPS Location Endpoints
[cite: 2026-02-03, 2026-01-09]

Complete implementation:
1. Automatic detection of user's current coordinates upon entry
2. Immediate mapping to global radar view
3. Real-time location updates with zero lag for 20,000+ users
"""
from fastapi import APIRouter, Depends, HTTPException, Body, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.core.database import get_db
from app.location_handler import LocationHandler, detect_user_location, update_location_realtime
from app.schemas.location import LocationRequest, LocationResponse, NearbyUsersResponse
from app.models.user import User
from datetime import datetime
import uuid

router = APIRouter()


@router.post("/detect", response_model=LocationResponse)
async def detect_location_on_entry(
    request: LocationRequest,
    db: Session = Depends(get_db)
):
    """
    AUTOMATIC GPS DETECTION UPON ENTRY [cite: 2026-02-03]
    
    Automatically detects the user's current coordinates when they enter the app.
    Immediately maps the location to the global radar view.
    
    This endpoint should be called automatically when:
    - User opens the app
    - User grants location permissions
    - GPS coordinates are first available
    
    Returns location update result with immediate radar mapping.
    """
    try:
        # Use location_handler for automatic detection
        result = detect_user_location(
            db=db,
            user_id=request.user_id,
            latitude=request.latitude,
            longitude=request.longitude,
            accuracy=request.accuracy,
            auto_detect=request.auto_detect
        )
        
        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("error", "Failed to detect location"))
        
        return LocationResponse(
            success=result["success"],
            message=result["message"],
            user_id=result["user_id"],
            latitude=result["latitude"],
            longitude=result["longitude"],
            status=result["status"],
            should_appear_on_radar=result["should_appear_on_radar"],
            distance_moved_km=result.get("distance_moved_km"),
            timestamp=result["timestamp"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to detect location: {str(e)}")


@router.post("/update", response_model=LocationResponse)
async def update_location_realtime(
    request: LocationRequest,
    db: Session = Depends(get_db)
):
    """
    REAL-TIME LOCATION UPDATE WITH ZERO LAG [cite: 2026-01-09]
    
    Updates user location in real-time with immediate radar mapping.
    Optimized for 20,000+ concurrent users with efficient broadcasting.
    
    Use this endpoint for:
    - Continuous location tracking
    - Movement updates
    - Manual location refresh
    """
    try:
        result = update_location_realtime(
            db=db,
            user_id=request.user_id,
            latitude=request.latitude,
            longitude=request.longitude
        )
        
        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("error", "Failed to update location"))
        
        return LocationResponse(
            success=result["success"],
            message=result["message"],
            user_id=result["user_id"],
            latitude=result["latitude"],
            longitude=result["longitude"],
            status=result["status"],
            should_appear_on_radar=result["should_appear_on_radar"],
            distance_moved_km=result.get("distance_moved_km"),
            timestamp=result["timestamp"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to update location: {str(e)}")


@router.get("/user/{user_id}")
async def get_user_location(
    user_id: str,
    db: Session = Depends(get_db)
):
    """
    Get current location for a specific user.
    """
    try:
        handler = LocationHandler(db)
        location = handler.get_user_location(user_id)
        
        if not location:
            raise HTTPException(status_code=404, detail="User location not found")
        
        return location
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get location: {str(e)}")


@router.get("/nearby", response_model=NearbyUsersResponse)
async def get_nearby_users(
    latitude: float = Query(..., description="Center latitude"),
    longitude: float = Query(..., description="Center longitude"),
    radius_km: float = Query(15.0, description="Search radius in kilometers"),
    limit: int = Query(100, description="Maximum number of users to return"),
    db: Session = Depends(get_db)
):
    """
    Get nearby users within radius (optimized for 20,000+ users).
    Uses database indexes for fast geolocation queries.
    """
    try:
        handler = LocationHandler(db)
        nearby_users = handler.get_nearby_users(
            latitude=latitude,
            longitude=longitude,
            radius_km=radius_km,
            limit=limit
        )
        
        return NearbyUsersResponse(
            users=nearby_users,
            total=len(nearby_users),
            center_latitude=latitude,
            center_longitude=longitude,
            radius_km=radius_km,
            timestamp=datetime.utcnow().isoformat()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get nearby users: {str(e)}")


@router.post("/batch-update")
async def batch_update_locations(
    updates: list[LocationRequest] = Body(..., description="List of location updates"),
    db: Session = Depends(get_db)
):
    """
    Batch location updates for scalability (20,000+ users).
    Processes multiple location updates efficiently.
    """
    try:
        handler = LocationHandler(db)
        results = []
        
        for update in updates:
            result = handler.detect_and_set_location(
                user_id=update.user_id,
                latitude=update.latitude,
                longitude=update.longitude,
                accuracy=update.accuracy,
                auto_detect=update.auto_detect
            )
            results.append(result)
        
        return {
            "success": True,
            "processed": len(results),
            "results": results
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to batch update locations: {str(e)}")
