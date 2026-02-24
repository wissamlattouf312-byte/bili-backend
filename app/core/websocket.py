"""
BILI Master System - WebSocket Manager for Real-time Radar
Implements Silent Decay Logic: Remove offline users with 0 credits
"""
from fastapi import WebSocket
from typing import Dict, List, Set, Optional
import json
import asyncio
from datetime import datetime, timedelta
from app.core.config import settings
from app.models.user import User, UserStatus
from app.core.database import SessionLocal


class WebSocketManager:
    """
    Manages WebSocket connections for real-time radar updates.
    Implements Silent Decay Logic: Users with status="Offline" AND balance=0.00 
    are instantly removed from radar.
    
    Enhanced for Global GPS Location System:
    - Zero-lag location broadcasting [cite: 2026-01-09]
    - Efficient batching for 20,000+ users
    - Immediate radar mapping [cite: 2026-02-03]
    """
    
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.user_sessions: Dict[str, Dict] = {}  # user_id -> {socket_id, last_ping, status}
        self.grace_period_tasks: Dict[str, asyncio.Task] = {}
        # Location update batching for scalability
        self.location_update_queue: List[Dict] = []
        self.batch_task: Optional[asyncio.Task] = None
        
    async def connect(self, websocket: WebSocket, user_id: str = None):
        """Connect a WebSocket client"""
        await websocket.accept()
        socket_id = str(id(websocket))
        self.active_connections[socket_id] = websocket
        
        # Start batch processing task if not already running
        if self.batch_task is None or self.batch_task.done():
            self.batch_task = asyncio.create_task(self.batch_location_updates())
        
        if user_id:
            self.user_sessions[user_id] = {
                "socket_id": socket_id,
                "last_ping": datetime.utcnow(),
                "status": "online"
            }
            # Update user status to online in database
            if SessionLocal is None:
                return
            db = SessionLocal()
            try:
                user = db.query(User).filter(User.id == user_id).first()
                if user:
                    user.status = UserStatus.ONLINE
                    user.last_seen = datetime.utcnow()
                    db.commit()
            finally:
                db.close()
            # Broadcast user online status
            await self.broadcast_user_status(user_id, "online")
    
    async def disconnect(self, websocket: WebSocket):
        """Disconnect a WebSocket client"""
        socket_id = str(id(websocket))
        
        # Find user_id for this socket
        user_id = None
        for uid, session in self.user_sessions.items():
            if session["socket_id"] == socket_id:
                user_id = uid
                break
        
        if socket_id in self.active_connections:
            del self.active_connections[socket_id]
        
        if user_id:
            # Start grace period before marking offline
            await self.start_grace_period(user_id)
    
    async def start_grace_period(self, user_id: str):
        """
        Start 60-second grace period before marking user offline.
        If user reconnects within grace period, cancel the offline status.
        """
        if user_id in self.grace_period_tasks:
            self.grace_period_tasks[user_id].cancel()
        
        async def grace_period_handler():
            await asyncio.sleep(settings.SOCKET_GRACE_PERIOD_SECONDS)
            # Check if user still has no active connection
            if user_id in self.user_sessions:
                session = self.user_sessions[user_id]
                if session["socket_id"] not in self.active_connections:
                    await self.mark_user_offline(user_id)
        
        task = asyncio.create_task(grace_period_handler())
        self.grace_period_tasks[user_id] = task
    
    async def mark_user_offline(self, user_id: str):
        """
        Mark user as offline and apply Silent Decay Logic:
        If user is offline AND has 0.00 credits, remove from radar immediately.
        """
        if SessionLocal is None:
            return
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if user:
                user.status = UserStatus.OFFLINE
                user.last_seen = datetime.utcnow()
                db.commit()
                
                # Silent Decay Logic: Remove if balance is 0.00
                if user.credit_balance == 0.00:
                    await self.remove_from_radar(user_id)
                else:
                    # Broadcast offline status (but keep on radar if credits > 0)
                    await self.broadcast_user_status(user_id, "offline")
        finally:
            db.close()
    
    async def remove_from_radar(self, user_id: str):
        """
        Remove user from radar (Silent Decay Logic).
        Broadcast removal to all connected clients.
        """
        if user_id in self.user_sessions:
            del self.user_sessions[user_id]
        
        # Broadcast removal to all clients
        message = {
            "type": "user_removed",
            "user_id": user_id,
            "reason": "silent_decay",
            "timestamp": datetime.utcnow().isoformat()
        }
        await self.broadcast(message)
    
    async def broadcast_user_status(self, user_id: str, status: str):
        """Broadcast user status change to all connected clients"""
        message = {
            "type": "user_status_update",
            "user_id": user_id,
            "status": status,
            "timestamp": datetime.utcnow().isoformat()
        }
        await self.broadcast(message)
    
    async def broadcast(self, message: dict):
        """
        Broadcast message to all connected WebSocket clients.
        Optimized for 20,000+ concurrent connections [cite: 2026-01-09].
        """
        if not self.active_connections:
            return
        
        disconnected = []
        message_json = json.dumps(message)
        
        # Batch send to all connections (non-blocking)
        tasks = []
        for socket_id, connection in self.active_connections.items():
            try:
                tasks.append(connection.send_text(message_json))
            except Exception:
                disconnected.append(socket_id)
        
        # Send to all connections concurrently
        if tasks:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            # Track failed connections
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    socket_id = list(self.active_connections.keys())[i]
                    disconnected.append(socket_id)
        
        # Clean up disconnected clients
        for socket_id in disconnected:
            if socket_id in self.active_connections:
                del self.active_connections[socket_id]
    
    async def broadcast_location_update(
        self,
        user_id: str,
        latitude: float,
        longitude: float,
        auto_detect: bool = False
    ):
        """
        Broadcast location update with zero lag [cite: 2026-01-09].
        Immediately maps user to global radar view [cite: 2026-02-03].
        """
        message = {
            "type": "location_update",
            "user_id": user_id,
            "latitude": latitude,
            "longitude": longitude,
            "auto_detect": auto_detect,
            "timestamp": datetime.utcnow().isoformat()
        }
        await self.broadcast(message)
        
        # Also send updated radar state to requesting clients
        # This ensures immediate visibility on radar
        await self.broadcast_user_status(user_id, "online")
    
    async def batch_location_updates(self):
        """
        Process batched location updates for scalability.
        Reduces WebSocket message overhead for 20,000+ users.
        """
        while True:
            await asyncio.sleep(0.1)  # 100ms batch window
            if self.location_update_queue:
                updates = self.location_update_queue.copy()
                self.location_update_queue.clear()
                
                # Send batched location updates
                if updates:
                    message = {
                        "type": "batch_location_update",
                        "updates": updates,
                        "timestamp": datetime.utcnow().isoformat()
                    }
                    await self.broadcast(message)
    
    async def handle_message(self, websocket: WebSocket, data: str):
        """Handle incoming WebSocket message"""
        try:
            message = json.loads(data)
            message_type = message.get("type")
            
            if message_type == "ping":
                # Update last ping time
                socket_id = str(id(websocket))
                for user_id, session in self.user_sessions.items():
                    if session["socket_id"] == socket_id:
                        session["last_ping"] = datetime.utcnow()
                        await websocket.send_text(json.dumps({"type": "pong"}))
                        break
            
            elif message_type == "request_radar":
                # Send current radar state
                await self.send_radar_state(websocket)
        
        except json.JSONDecodeError:
            await websocket.send_text(json.dumps({"error": "Invalid JSON"}))
    
    async def send_radar_state(self, websocket: WebSocket):
        """
        Send current radar state (only online users, or offline users with credits > 0).
        Silent Decay: Users with status="offline" AND balance=0.00 are excluded.
        """
        if SessionLocal is None:
            await websocket.send_text(json.dumps({"type": "radar_state", "users": []}))
            return
        db = SessionLocal()
        try:
            # Get all users that should appear on radar:
            # - Status = "online" OR
            # - Status = "offline" AND credit_balance > 0.00
            from sqlalchemy import or_, and_
            radar_users = db.query(User).filter(
                or_(
                    User.status == UserStatus.ONLINE,
                    and_(
                        User.status == UserStatus.OFFLINE,
                        User.credit_balance > 0.00
                    )
                )
            ).filter(
                User.is_invisible == False,
                User.latitude.isnot(None),
                User.longitude.isnot(None)
            ).all()
            
            radar_data = {
                "type": "radar_state",
                "users": [
                    {
                        "user_id": str(user.id),
                        "latitude": user.latitude,
                        "longitude": user.longitude,
                        "status": user.status.value,
                        "credit_balance": float(user.credit_balance),
                        "last_seen": user.last_seen.isoformat() if user.last_seen else None
                    }
                    for user in radar_users
                ],
                "timestamp": datetime.utcnow().isoformat()
            }
            
            await websocket.send_text(json.dumps(radar_data))
        finally:
            db.close()


# Global WebSocket manager instance
websocket_manager = WebSocketManager()
