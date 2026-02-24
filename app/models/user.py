"""
BILI Master System - User Model
Supports Guest Access and Member Registration

Optimized for scalability (20,000+ users) with proper indexing [cite: 2026-01-09]
"""
from sqlalchemy import Column, String, Float, Boolean, DateTime, Integer, Text, Enum, Index, ForeignKey
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime
from app.core.database import Base, GUID
import enum


class UserStatus(str, enum.Enum):
    ONLINE = "online"
    OFFLINE = "offline"
    INVISIBLE = "invisible"  # Online but hidden


class UserRole(str, enum.Enum):
    GUEST = "guest"
    MEMBER = "member"
    MASTER = "master"
    ADMIN = "admin"


class User(Base):
    __tablename__ = "users"
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    phone_number = Column(String(20), unique=True, nullable=True)  # Nullable for guests
    email = Column(String(255), unique=True, nullable=True)
    
    # Guest/Member Status
    role = Column(Enum(UserRole), default=UserRole.GUEST, nullable=False)
    is_guest = Column(Boolean, default=True, nullable=False)
    
    # Profile
    display_name = Column(String(100), nullable=True)
    avatar_url = Column(String(500), nullable=True)
    
    # Geolocation
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    last_location_update = Column(DateTime, nullable=True)
    
    # Status & Visibility
    status = Column(Enum(UserStatus), default=UserStatus.OFFLINE, nullable=False)
    last_seen = Column(DateTime, nullable=True)
    is_invisible = Column(Boolean, default=False, nullable=False)  # Invisible mode
    
    # Credit System
    credit_balance = Column(Float, default=0.00, nullable=False)
    
    # Royal Hospitality Period
    claim_date = Column(DateTime, nullable=True)  # Date when user claimed business
    royal_hospitality_end_date = Column(DateTime, nullable=True)  # 30 days from claim_date
    
    # Viral Gateway: referral code (share link) and who referred this user
    referral_code = Column(String(20), unique=True, nullable=True, index=True)  # e.g. R1A2B3C4
    referred_by_id = Column(GUID(), ForeignKey("users.id"), nullable=True)
    
    # Master Status
    is_master = Column(Boolean, default=False, nullable=False)
    master_cv_url = Column(String(500), nullable=True)  # CV/Portfolio URL
    master_verified = Column(Boolean, default=False, nullable=False)
    master_badge_url = Column(String(500), nullable=True)
    
    # Settings
    notification_enabled = Column(Boolean, default=True, nullable=False)
    golden_bell_enabled = Column(Boolean, default=True, nullable=False)  # Golden = Sound, Grey = Silent
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    businesses = relationship("Business", back_populates="owner", cascade="all, delete-orphan")
    credit_transactions = relationship("CreditTransaction", back_populates="user")
    credit_ledger = relationship("CreditLedger", back_populates="user")
    posts = relationship("Post", back_populates="owner")
    chats_initiated = relationship("Chat", foreign_keys="Chat.initiator_id", back_populates="initiator")
    chats_received = relationship("Chat", foreign_keys="Chat.recipient_id", back_populates="recipient")
    
    # Database indexes for scalability (20,000+ users) [cite: 2026-01-09]
    __table_args__ = (
        Index('idx_users_phone_number', 'phone_number'),  # Fast phone lookup
        Index('idx_users_role_status', 'role', 'status'),  # Fast role/status filtering
        Index('idx_users_status_balance', 'status', 'credit_balance'),  # Radar queries (Silent Decay Logic)
        Index('idx_users_last_seen', 'last_seen'),  # Activity tracking
        Index('idx_users_location', 'latitude', 'longitude'),  # Geolocation queries
        Index('idx_users_created_at', 'created_at'),  # User growth analytics
    )
    
    def __repr__(self):
        return f"<User(id={self.id}, role={self.role}, status={self.status}, credits={self.credit_balance})>"
    
    def is_in_royal_hospitality_period(self) -> bool:
        """Check if user is within 30-day free service period"""
        if not self.royal_hospitality_end_date:
            return False
        return datetime.utcnow() < self.royal_hospitality_end_date
    
    def should_appear_on_radar(self) -> bool:
        """
        Silent Decay Logic: User appears on radar ONLY if:
        - Status is "online" OR
        - Status is "offline" AND credit_balance > 0.00
        """
        if self.status == UserStatus.ONLINE:
            return True
        if self.status == UserStatus.OFFLINE and self.credit_balance > 0.00:
            return True
        return False
