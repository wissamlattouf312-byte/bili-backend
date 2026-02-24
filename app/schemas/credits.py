"""
BILI Master System - Credit Schemas
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class CreditBalanceResponse(BaseModel):
    user_id: str
    balance: float
    is_in_royal_hospitality: bool
    royal_hospitality_end_date: Optional[str] = None


class CreditLedgerResponse(BaseModel):
    id: str
    entry_type: str
    amount: float
    balance_before: float
    balance_after: float
    description: str
    category: Optional[str] = None
    timestamp: datetime
    
    class Config:
        from_attributes = True
