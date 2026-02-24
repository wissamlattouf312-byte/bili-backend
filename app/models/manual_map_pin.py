"""
BILI Master System - Manual Map Pin Model
Admin-added store locations (no Google Places API). Pins appear on the map for all users.
Dynamic Refresh: optional profile_url; system fetches and displays latest video/post.
"""
from sqlalchemy import Column, String, Float, DateTime, Text
import uuid
from datetime import datetime
from app.core.database import Base, GUID


class ManualMapPin(Base):
    __tablename__ = "manual_map_pins"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, default="Store")
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    address = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Dynamic Refresh: store profile URL; backend fetches latest content periodically
    profile_url = Column(String(1024), nullable=True)
    latest_content_url = Column(String(1024), nullable=True)
    latest_content_thumbnail = Column(String(1024), nullable=True)
    latest_content_title = Column(String(512), nullable=True)
    content_fetched_at = Column(DateTime, nullable=True)

    def __repr__(self):
        return f"<ManualMapPin(id={self.id}, name={self.name}, lat={self.latitude}, lng={self.longitude})>"
