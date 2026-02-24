"""
BILI Master System - Business Model
Google Mirror: Read-only until claimed
"""
from sqlalchemy import Column, String, Float, Boolean, DateTime, Text, ForeignKey, Enum
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime
from app.core.database import Base, GUID
import enum


class BusinessStatus(str, enum.Enum):
    UNCLAIMED = "unclaimed"
    CLAIMED = "claimed"
    VERIFIED = "verified"


class Business(Base):
    __tablename__ = "businesses"
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    
    # Google Mirror Data (Read-only until claimed)
    google_place_id = Column(String(255), unique=True, nullable=False)
    google_name = Column(String(255), nullable=False)
    google_address = Column(Text, nullable=True)
    google_phone = Column(String(50), nullable=True)
    google_website = Column(String(500), nullable=True)
    google_category = Column(String(100), nullable=True)
    google_rating = Column(Float, nullable=True)
    google_photos = Column(Text, nullable=True)  # JSON array of photo URLs
    
    # Geolocation
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    
    # Claim Status
    status = Column(Enum(BusinessStatus), default=BusinessStatus.UNCLAIMED, nullable=False)
    owner_id = Column(GUID(), ForeignKey("users.id"), nullable=True)
    claimed_at = Column(DateTime, nullable=True)
    
    # Custom Business Data (Editable after claim)
    custom_name = Column(String(255), nullable=True)
    custom_description = Column(Text, nullable=True)
    custom_logo_url = Column(String(500), nullable=True)
    custom_category = Column(String(100), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    owner = relationship("User", back_populates="businesses")
    
    def __repr__(self):
        return f"<Business(id={self.id}, name={self.google_name}, status={self.status})>"
    
    @property
    def display_name(self) -> str:
        """Return custom name if claimed, otherwise Google name"""
        return self.custom_name or self.google_name
    
    def is_claimed(self) -> bool:
        """Check if business has been claimed"""
        return self.status != BusinessStatus.UNCLAIMED
