"""
BILI Master System - Live Radar Endpoints
SILENT DECAY LOGIC: Remove offline users with 0 credits from radar [cite: 2026-01-30]

Complete implementation with:
- Real-time radar updates
- Silent Decay Logic (offline + zero balance = removal)
- Background monitoring task
- WebSocket integration
"""
from fastapi import APIRouter, Depends, HTTPException, Query, Body, Request
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from typing import Optional, List
from datetime import datetime, timedelta
import asyncio
import math
from app.core.database import get_db
from app.models.user import User, UserStatus
from app.schemas.radar import RadarUserResponse, RadarResponse
from app.core.websocket import websocket_manager
from app.core.config import settings

router = APIRouter()


def calculate_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate distance between two coordinates using Haversine formula.
    Returns distance in kilometers.
    """
    # Earth radius in kilometers
    R = 6371.0
    
    # Convert to radians
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)
    
    # Haversine formula
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    
    a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    distance = R * c
    return distance


@router.get("/users", response_model=RadarResponse)
async def get_radar_users(
    latitude: Optional[float] = Query(None, description="User latitude"),
    longitude: Optional[float] = Query(None, description="User longitude"),
    radius_km: Optional[float] = Query(15, description="Search radius in kilometers"),
    db: Session = Depends(get_db)
):
    """
    Get users visible on radar.
    
    SILENT DECAY LOGIC [cite: 2026-01-30]:
    - Users appear ONLY if status="online" OR (status="offline" AND credit_balance > 0.00)
    - Users with status="offline" AND credit_balance=0.00 are instantly removed
    - Uses WebSocket for real-time synchronization
    """
    # Apply Silent Decay Logic filter
    # Only show: (status=online) OR (status=offline AND balance > 0)
    query = db.query(User).filter(
        or_(
            User.status == UserStatus.ONLINE,
            and_(
                User.status == UserStatus.OFFLINE,
                User.credit_balance > 0.00
            )
        )
    ).filter(
        User.is_invisible == False,  # Exclude invisible mode users
        User.latitude.isnot(None),
        User.longitude.isnot(None)
    )
    
    users = query.all()
    
    # Filter by radius if location provided
    radar_users = []
    if latitude and longitude:
        for user in users:
            if user.latitude and user.longitude:
                distance = calculate_distance_km(
                    latitude, longitude,
                    user.latitude, user.longitude
                )
                if distance <= radius_km:
                    radar_users.append(user)
    else:
        radar_users = users
    
    # Apply Silent Decay: Double-check and remove any zero-balance offline users
    filtered_users = []
    for user in radar_users:
        if user.status == UserStatus.OFFLINE and user.credit_balance == 0.00:
            # Silent Decay: Skip this user (should not appear)
            continue
        filtered_users.append(user)
    
    return RadarResponse(
        users=[RadarUserResponse.from_orm(u) for u in filtered_users],
        total=len(filtered_users),
        timestamp=datetime.utcnow().isoformat()
    )


@router.post("/update-location")
async def update_user_location(
    user_id: str = Body(..., description="User ID"),
    latitude: float = Body(..., description="Latitude"),
    longitude: float = Body(..., description="Longitude"),
    db: Session = Depends(get_db)
):
    """
    Update user location for radar.
    IMMEDIATELY maps to global radar view with zero lag [cite: 2026-01-09, 2026-02-03].
    Uses location_handler for optimized updates.
    """
    try:
        from app.location_handler import update_location_realtime
        
        result = update_location_realtime(
            db=db,
            user_id=user_id,
            latitude=latitude,
            longitude=longitude
        )
        
        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("error", "Failed to update location"))
        
        return {
            "success": True,
            "message": "Location updated and mapped to radar immediately",
            "user_id": result["user_id"],
            "latitude": result["latitude"],
            "longitude": result["longitude"],
            "status": result["status"],
            "should_appear_on_radar": result["should_appear_on_radar"],
            "timestamp": result["timestamp"]
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to update location: {str(e)}")


@router.post("/update-status")
async def update_user_status(
    user_id: str = Body(..., description="User ID"),
    status: str = Body(..., description="Status: online, offline, or invisible"),
    db: Session = Depends(get_db)
):
    """
    Update user status.
    Triggers Silent Decay Logic if status becomes "offline" and balance is 0.00.
    
    SILENT DECAY LOGIC [cite: 2026-01-30]:
    - If user goes offline AND has 0.00 credits, remove from radar immediately
    - Broadcast removal to all connected WebSocket clients
    """
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Validate status
        try:
            new_status = UserStatus(status.lower())
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid status: {status}. Must be: online, offline, or invisible")
        
        old_status = user.status
        user.status = new_status
        user.last_seen = datetime.utcnow()
        
        # Apply Silent Decay Logic
        if new_status == UserStatus.OFFLINE and user.credit_balance == 0.00:
            # Silent Decay: User should be removed from radar
            db.commit()
            
            # Broadcast removal via WebSocket
            await websocket_manager.remove_from_radar(str(user.id))
            
            return {
                "success": True,
                "status": status,
                "silent_decay_applied": True,
                "message": "User removed from radar (Silent Decay: offline + zero balance)",
                "should_appear_on_radar": False
            }
        else:
            # User stays on radar (either online or offline with credits > 0)
            db.commit()
            db.refresh(user)
            
            # Broadcast status change
            await websocket_manager.broadcast_user_status(str(user.id), status)
            
            return {
                "success": True,
                "status": status,
                "silent_decay_applied": False,
                "should_appear_on_radar": user.should_appear_on_radar(),
                "credit_balance": user.credit_balance
            }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to update status: {str(e)}")


@router.post("/silent-decay-check")
async def trigger_silent_decay_check(
    db: Session = Depends(get_db)
):
    """
    Manual trigger for Silent Decay Logic check.
    Scans all users and removes offline users with 0 credits.
    
    This is also run automatically via background task.
    """
    try:
        # Find all offline users with zero balance
        offline_zero_balance_users = db.query(User).filter(
            User.status == UserStatus.OFFLINE,
            User.credit_balance == 0.00,
            User.is_invisible == False
        ).all()
        
        removed_count = 0
        for user in offline_zero_balance_users:
            # Remove from radar via WebSocket
            await websocket_manager.remove_from_radar(str(user.id))
            removed_count += 1
        
        return {
            "success": True,
            "removed_count": removed_count,
            "message": f"Silent Decay Logic applied: {removed_count} users removed from radar"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to check Silent Decay: {str(e)}")


@router.get("/stats")
async def get_radar_stats(
    db: Session = Depends(get_db)
):
    """
    Get radar statistics including Silent Decay metrics.
    """
    total_users = db.query(User).count()
    online_users = db.query(User).filter(User.status == UserStatus.ONLINE).count()
    offline_with_credits = db.query(User).filter(
        User.status == UserStatus.OFFLINE,
        User.credit_balance > 0.00
    ).count()
    offline_zero_balance = db.query(User).filter(
        User.status == UserStatus.OFFLINE,
        User.credit_balance == 0.00
    ).count()
    
    # Users visible on radar (Silent Decay Logic)
    visible_on_radar = online_users + offline_with_credits
    
    return {
        "total_users": total_users,
        "online_users": online_users,
        "offline_with_credits": offline_with_credits,
        "offline_zero_balance": offline_zero_balance,
        "visible_on_radar": visible_on_radar,
        "silent_decay_removed": offline_zero_balance,
        "silent_decay_logic": "Users with status=offline AND balance=0.00 are removed from radar"
    }
