"""
BILI Master System - Flash Deal Model
Step 5: Merchants post Flash Deals that auto-expire and disappear after 24 hours.
"""
from sqlalchemy import Column, String, Float, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime, timedelta
from app.core.database import Base, GUID


class FlashDeal(Base):
    __tablename__ = "flash_deals"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    business_id = Column(GUID(), ForeignKey("businesses.id"), nullable=False)
    owner_id = Column(GUID(), ForeignKey("users.id"), nullable=False)

    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    image_url = Column(String(500), nullable=True)

    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)

    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    @property
    def is_expired(self) -> bool:
        return datetime.utcnow() > self.expires_at

    @staticmethod
    def default_expiry():
        return datetime.utcnow() + timedelta(hours=24)
