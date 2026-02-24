"""
BILI Master System - Credit System Models
Credit Ledger for tracking all credit transactions

Optimized for scalability (20,000+ users) with proper indexing [cite: 2026-01-09]
"""
from sqlalchemy import Column, String, Float, DateTime, Text, ForeignKey, Enum, Integer, Index
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime
from app.core.database import Base, GUID
import enum


class CreditTransactionType(str, enum.Enum):
    CLAIM_REWARD = "claim_reward"  # 20 credits from claiming business
    REFERRAL_REWARD = "referral_reward"  # 5 credits from referral
    PURCHASE = "purchase"  # Credit purchase
    AD_POST = "ad_post"  # Deduction for commercial ad
    REFUND = "refund"  # Refund for expired/removed content
    ADMIN_ADJUSTMENT = "admin_adjustment"  # Admin manual adjustment


class CreditTransaction(Base):
    __tablename__ = "credit_transactions"
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    user_id = Column(GUID(), ForeignKey("users.id"), nullable=False)
    
    transaction_type = Column(Enum(CreditTransactionType), nullable=False)
    amount = Column(Float, nullable=False)  # Positive for credits added, negative for deducted
    
    # Reference to related entity
    reference_id = Column(GUID(), nullable=True)  # Post ID, Business ID, etc.
    reference_type = Column(String(50), nullable=True)  # "post", "business", "referral", etc.
    
    description = Column(Text, nullable=True)
    
    # Balance after transaction
    balance_after = Column(Float, nullable=False)
    
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="credit_transactions")
    
    # Database indexes for scalability [cite: 2026-01-09]
    __table_args__ = (
        Index('idx_credit_transactions_user_id', 'user_id'),
        Index('idx_credit_transactions_type', 'transaction_type'),
        Index('idx_credit_transactions_user_type', 'user_id', 'transaction_type'),
        Index('idx_credit_transactions_timestamp', 'timestamp'),
        Index('idx_credit_transactions_reference', 'reference_id', 'reference_type'),
    )
    
    def __repr__(self):
        return f"<CreditTransaction(id={self.id}, type={self.transaction_type}, amount={self.amount})>"


class CreditLedger(Base):
    """
    Comprehensive ledger for all credit movements.
    Provides clear history log for users.
    """
    __tablename__ = "credit_ledger"
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    user_id = Column(GUID(), ForeignKey("users.id"), nullable=False)
    
    transaction_id = Column(GUID(), ForeignKey("credit_transactions.id"), nullable=False)
    
    # Ledger Details
    entry_type = Column(String(50), nullable=False)  # "credit", "debit"
    amount = Column(Float, nullable=False)
    balance_before = Column(Float, nullable=False)
    balance_after = Column(Float, nullable=False)
    
    description = Column(Text, nullable=False)
    category = Column(String(100), nullable=True)  # "reward", "purchase", "ad", etc.
    
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="credit_ledger")
    transaction = relationship("CreditTransaction")
    
    # Database indexes for scalability [cite: 2026-01-09]
    __table_args__ = (
        Index('idx_credit_ledger_user_id', 'user_id'),
        Index('idx_credit_ledger_user_timestamp', 'user_id', 'timestamp'),
        Index('idx_credit_ledger_category', 'category'),
        Index('idx_credit_ledger_timestamp', 'timestamp'),
    )
    
    def __repr__(self):
        return f"<CreditLedger(id={self.id}, type={self.entry_type}, amount={self.amount})>"
