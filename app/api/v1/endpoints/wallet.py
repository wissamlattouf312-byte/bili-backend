"""
BILI Master System - Wallet Finance Endpoints
[cite: 2026-02-09]

Endpoints for:
1. Credit to USDT conversion
2. Automatic withdrawal processing
3. Wallet balance queries
"""
from fastapi import APIRouter, Depends, HTTPException, Body, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.core.database import get_db
from app.wallet_finance import (
    WalletFinanceHandler,
    process_automatic_withdrawal_if_eligible,
    get_user_usdt_balance,
    credits_to_usdt_value
)
from app.models.user import User
import uuid

router = APIRouter()


@router.get("/balance/{user_id}")
async def get_wallet_balance(
    user_id: str,
    db: Session = Depends(get_db)
):
    """
    Get user's wallet balance in both credits and USDT.
    Automatically checks and processes withdrawal if threshold reached [cite: 2026-02-03].
    """
    try:
        handler = WalletFinanceHandler(db)
        
        # Get USDT balance
        usdt_balance = handler.get_user_usdt_balance(user_id)
        if usdt_balance is None:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Get user for credits
        user_uuid = uuid.UUID(user_id)
        user = db.query(User).filter(User.id == user_uuid).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Check withdrawal threshold
        threshold_check = handler.check_withdrawal_threshold(user_id)
        
        # Auto-process withdrawal if eligible
        withdrawal_result = None
        if threshold_check.get("eligible_for_withdrawal"):
            withdrawal_result = await handler.process_automatic_withdrawal(user_id)
        
        return {
            "user_id": user_id,
            "credits_balance": float(user.credit_balance),
            "usdt_balance": usdt_balance,
            "credit_to_usdt_rate": handler.CREDIT_TO_USDT_RATE,
            "withdrawal_threshold_usd": handler.WITHDRAWAL_THRESHOLD_USD,
            "eligible_for_withdrawal": threshold_check.get("eligible_for_withdrawal", False),
            "withdrawal_processed": withdrawal_result.get("success") if withdrawal_result else False,
            "withdrawal_message": withdrawal_result.get("message") if withdrawal_result else None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get wallet balance: {str(e)}")


@router.post("/withdraw")
async def manual_withdraw(
    user_id: str = Body(..., description="User ID"),
    amount_usdt: float = Body(..., description="Amount to withdraw in USDT"),
    force: bool = Body(False, description="Force withdrawal even if below threshold"),
    db: Session = Depends(get_db)
):
    """
    Manual withdrawal request to Bybit wallet.
    For automatic withdrawals, use the balance endpoint which auto-processes at $50.
    """
    try:
        handler = WalletFinanceHandler(db)
        result = await handler.withdraw_to_bybit(
            user_id=user_id,
            amount_usdt=amount_usdt,
            force=force
        )
        
        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("error", "Withdrawal failed"))
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to process withdrawal: {str(e)}")


@router.get("/withdrawal-history/{user_id}")
async def get_withdrawal_history(
    user_id: str,
    limit: int = Query(50, description="Maximum number of records"),
    db: Session = Depends(get_db)
):
    """Get user's withdrawal history"""
    try:
        handler = WalletFinanceHandler(db)
        history = handler.get_withdrawal_history(user_id, limit)
        
        return {
            "user_id": user_id,
            "total_withdrawals": len(history),
            "withdrawals": history
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get withdrawal history: {str(e)}")


@router.get("/convert/credits-to-usdt")
async def convert_credits_to_usdt(
    credits: float = Query(..., description="Number of credits (Habbet)"),
    db: Session = Depends(get_db)
):
    """Convert credits (Habbet) to USDT value"""
    try:
        handler = WalletFinanceHandler(db)
        usdt_value = handler.credits_to_usdt(credits)
        
        return {
            "credits": credits,
            "usdt_value": usdt_value,
            "exchange_rate": handler.CREDIT_TO_USDT_RATE
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to convert credits: {str(e)}")


@router.get("/convert/usdt-to-credits")
async def convert_usdt_to_credits(
    usdt: float = Query(..., description="USDT amount"),
    db: Session = Depends(get_db)
):
    """Convert USDT value to credits (Habbet)"""
    try:
        handler = WalletFinanceHandler(db)
        credits_value = handler.usdt_to_credits(usdt)
        
        return {
            "usdt": usdt,
            "credits_value": credits_value,
            "exchange_rate": handler.CREDIT_TO_USDT_RATE
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to convert USDT: {str(e)}")


@router.post("/check-threshold/{user_id}")
async def check_withdrawal_threshold(
    user_id: str,
    db: Session = Depends(get_db)
):
    """
    Check if user's balance has reached the $50 withdrawal threshold.
    Does not process withdrawal, only checks eligibility.
    """
    try:
        handler = WalletFinanceHandler(db)
        result = handler.check_withdrawal_threshold(user_id)
        
        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("error", "Check failed"))
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to check threshold: {str(e)}")
