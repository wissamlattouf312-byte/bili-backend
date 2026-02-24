"""
BILI Master System - Post Model
Supports personal slots (free) and commercial ads (cost credits)
"""
from sqlalchemy import Column, String, Float, Boolean, DateTime, Text, ForeignKey, Enum, Integer
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime, timedelta
from app.core.database import Base, GUID
from app.core.config import settings
import enum


class PostType(str, enum.Enum):
    PERSONAL = "personal"  # Free slot, no credits
    COMMERCIAL = "commercial"  # Costs credits, triggers notifications


class MediaType(str, enum.Enum):
    IMAGE = "image"
    VIDEO = "video"
    TEXT = "text"


class Post(Base):
    __tablename__ = "posts"
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    owner_id = Column(GUID(), ForeignKey("users.id"), nullable=False)
    
    # Post Type
    post_type = Column(Enum(PostType), nullable=False)
    media_type = Column(Enum(MediaType), nullable=False)
    
    # Content
    title = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    media_url = Column(String(500), nullable=True)  # Video or image URL
    thumbnail_url = Column(String(500), nullable=True)  # Auto-generated or manual
    
    # Video Specific
    video_duration_seconds = Column(Integer, nullable=True)
    video_original_resolution = Column(String(20), nullable=True)  # e.g., "1080p"
    video_light_version_url = Column(String(500), nullable=True)  # Compressed version
    video_has_watermark = Column(Boolean, default=True, nullable=False)
    
    # Geolocation
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    radius_km = Column(Float, default=settings.DEFAULT_NOTIFICATION_RADIUS_KM, nullable=False)
    
    # Commercial Ad Settings
    is_commercial = Column(Boolean, default=False, nullable=False)
    credit_cost = Column(Float, default=0.0, nullable=False)  # 0.5 credits for commercial
    
    # Expiration
    expires_at = Column(DateTime, nullable=True)  # 48 hours for commercial posts
    is_expired = Column(Boolean, default=False, nullable=False)
    
    # Notification Settings
    notification_sent = Column(Boolean, default=False, nullable=False)
    last_notification_sent_at = Column(DateTime, nullable=True)
    
    # Visibility
    is_active = Column(Boolean, default=True, nullable=False)
    is_visible = Column(Boolean, default=True, nullable=False)
    
    # Category
    category = Column(String(100), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    owner = relationship("User", back_populates="posts")
    
    def __repr__(self):
        return f"<Post(id={self.id}, type={self.post_type}, owner={self.owner_id})>"
    
    def is_expired_now(self) -> bool:
        """Check if post has expired"""
        if not self.expires_at:
            return False
        return datetime.utcnow() > self.expires_at
    
    def should_send_notification(self) -> bool:
        """
        Check if notification can be sent (12-hour cooldown rule).
        Only applies to commercial posts.
        """
        if not self.is_commercial:
            return False
        
        if not self.last_notification_sent_at:
            return True
        
        time_since_last = datetime.utcnow() - self.last_notification_sent_at
        return time_since_last >= timedelta(hours=settings.NOTIFICATION_COOLDOWN_HOURS)
