"""
BILI Master System - Chat Models
Chat Retention Policy: Auto-delete after 30 days
"""
from sqlalchemy import Column, String, Boolean, DateTime, Text, ForeignKey, Enum
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime, timedelta
from app.core.database import Base, GUID
from app.core.config import settings
import enum


class ChatStatus(str, enum.Enum):
    ACTIVE = "active"
    ARCHIVED = "archived"
    DELETED = "deleted"


class MessageType(str, enum.Enum):
    TEXT = "text"
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    LOCATION = "location"


class Chat(Base):
    __tablename__ = "chats"
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    initiator_id = Column(GUID(), ForeignKey("users.id"), nullable=False)
    recipient_id = Column(GUID(), ForeignKey("users.id"), nullable=False)
    
    # Chat initiated from ad click
    post_id = Column(GUID(), ForeignKey("posts.id"), nullable=True)
    
    status = Column(Enum(ChatStatus), default=ChatStatus.ACTIVE, nullable=False)
    
    # Retention Policy
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    expires_at = Column(DateTime, nullable=False)  # Auto-set to created_at + 30 days
    deleted_at = Column(DateTime, nullable=True)
    
    # Relationships
    initiator = relationship("User", foreign_keys=[initiator_id], back_populates="chats_initiated")
    recipient = relationship("User", foreign_keys=[recipient_id], back_populates="chats_received")
    messages = relationship("ChatMessage", back_populates="chat", cascade="all, delete-orphan")
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.expires_at:
            self.expires_at = datetime.utcnow() + timedelta(days=settings.CHAT_RETENTION_DAYS)
    
    def __repr__(self):
        return f"<Chat(id={self.id}, initiator={self.initiator_id}, recipient={self.recipient_id})>"
    
    def should_be_deleted(self) -> bool:
        """Check if chat should be auto-deleted (30-day retention)"""
        return datetime.utcnow() > self.expires_at


class ChatMessage(Base):
    __tablename__ = "chat_messages"
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    chat_id = Column(GUID(), ForeignKey("chats.id"), nullable=False)
    sender_id = Column(GUID(), ForeignKey("users.id"), nullable=False)
    
    message_type = Column(Enum(MessageType), default=MessageType.TEXT, nullable=False)
    content = Column(Text, nullable=True)  # Text content or media URL
    media_url = Column(String(500), nullable=True)
    
    is_read = Column(Boolean, default=False, nullable=False)
    read_at = Column(DateTime, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    chat = relationship("Chat", back_populates="messages")
    sender = relationship("User")
    
    def __repr__(self):
        return f"<ChatMessage(id={self.id}, type={self.message_type}, chat={self.chat_id})>"
