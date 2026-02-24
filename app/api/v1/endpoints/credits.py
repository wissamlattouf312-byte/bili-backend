"""
BILI Master System - Credits Endpoints
Credit Ledger: Clear history log of all credit movements
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.models.user import User
from app.models.credit import CreditLedger
from app.schemas.credits import CreditLedgerResponse, CreditBalanceResponse

router = APIRouter()


@router.get("/balance/{user_id}", response_model=CreditBalanceResponse)
async def get_credit_balance(
    user_id: str,
    db: Session = Depends(get_db)
):
    """Get user credit balance"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return CreditBalanceResponse(
        user_id=str(user.id),
        balance=user.credit_balance,
        is_in_royal_hospitality=user.is_in_royal_hospitality_period(),
        royal_hospitality_end_date=user.royal_hospitality_end_date.isoformat() if user.royal_hospitality_end_date else None
    )


@router.get("/ledger/{user_id}", response_model=list[CreditLedgerResponse])
async def get_credit_ledger(
    user_id: str,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """
    Get credit ledger for user.
    Provides clear history log of all credit deductions and additions.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    ledger_entries = db.query(CreditLedger).filter(
        CreditLedger.user_id == user.id
    ).order_by(
        CreditLedger.timestamp.desc()
    ).limit(limit).all()
    
    return [CreditLedgerResponse.from_orm(entry) for entry in ledger_entries]
