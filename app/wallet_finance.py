"""
BILI Master System - Wallet Finance Handler
[cite: 2026-02-09]

This module handles:
1. Connection between user credits (20 Habbet) and USDT payout logic [cite: 2026-02-03]
2. Automatic withdrawal to Bybit when balance hits $50 [cite: 2026-02-03]

Architecture:
- Credit to USDT conversion
- Automatic withdrawal processing
- Bybit API integration
- Transaction logging and tracking
"""

from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
from datetime import datetime
import uuid
import asyncio
from decimal import Decimal, ROUND_DOWN
from app.models.user import User
from app.models.credit import CreditTransaction, CreditTransactionType, CreditLedger
from app.core.config import settings
from app.core.database import SessionLocal
import requests
import hmac
import hashlib
import time
import json
import os
from typing import List, Optional, Dict, Any


class WalletFinanceHandler:
    """
    Centralized wallet and finance handler for BILI App.
    Handles credit-to-USDT conversion and automatic withdrawals to Bybit.
    """
    
    # Exchange rate: 1 Habbet (credit) = 0.10 USDT (configurable)
    CREDIT_TO_USDT_RATE = float(os.getenv("CREDIT_TO_USDT_RATE", "0.10"))
    
    # Withdrawal threshold: $50 USDT [cite: 2026-02-03]
    WITHDRAWAL_THRESHOLD_USD = settings.AUTO_SWEEP_THRESHOLD_USD  # $50.0
    
    # Minimum withdrawal amount (Bybit requirement)
    MIN_WITHDRAWAL_USDT = 10.0
    
    def __init__(self, db: Session):
        self.db = db
        self.bybit_api_key = settings.BYBIT_API_KEY
        self.bybit_api_secret = settings.BYBIT_API_SECRET
        self.bybit_wallet_address = settings.BYBIT_WALLET_ADDRESS
        self.bybit_testnet = settings.BYBIT_TESTNET
        self.bybit_base_url = "https://api-testnet.bybit.com" if self.bybit_testnet else "https://api.bybit.com"
    
    def credits_to_usdt(self, credits: float) -> float:
        """
        Convert credits (Habbet) to USDT value.
        
        Args:
            credits: Number of credits (Habbet)
            
        Returns:
            USDT equivalent value
        """
        return round(credits * self.CREDIT_TO_USDT_RATE, 2)
    
    def usdt_to_credits(self, usdt: float) -> float:
        """
        Convert USDT value to credits (Habbet).
        
        Args:
            usdt: USDT amount
            
        Returns:
            Equivalent credits (Habbet)
        """
        return round(usdt / self.CREDIT_TO_USDT_RATE, 2)
    
    def get_user_usdt_balance(self, user_id: str) -> Optional[float]:
        """
        Get user's USDT balance based on their credits.
        
        Args:
            user_id: User UUID
            
        Returns:
            USDT balance or None if user not found
        """
        try:
            user_uuid = uuid.UUID(user_id)
        except ValueError:
            return None
        
        user = self.db.query(User).filter(User.id == user_uuid).first()
        if not user:
            return None
        
        return self.credits_to_usdt(user.credit_balance)
    
    def check_withdrawal_threshold(self, user_id: str) -> Dict[str, Any]:
        """
        Check if user's balance has reached the $50 withdrawal threshold [cite: 2026-02-03].
        
        Args:
            user_id: User UUID
            
        Returns:
            Dictionary with threshold check result
        """
        usdt_balance = self.get_user_usdt_balance(user_id)
        
        if usdt_balance is None:
            return {
                "success": False,
                "error": "User not found"
            }
        
        eligible = usdt_balance >= self.WITHDRAWAL_THRESHOLD_USD
        withdrawable_amount = usdt_balance if eligible else 0.0
        
        return {
            "success": True,
            "usdt_balance": usdt_balance,
            "threshold": self.WITHDRAWAL_THRESHOLD_USD,
            "eligible_for_withdrawal": eligible,
            "withdrawable_amount": withdrawable_amount,
            "remaining_balance": max(0.0, usdt_balance - withdrawable_amount) if eligible else usdt_balance
        }
    
    def _generate_bybit_signature(self, params: dict, timestamp: str) -> str:
        """
        Generate Bybit API signature for authentication.
        
        Args:
            params: Request parameters
            timestamp: Request timestamp
            
        Returns:
            HMAC-SHA256 signature
        """
        param_str = "&".join([f"{k}={v}" for k, v in sorted(params.items())])
        payload = f"{timestamp}{self.bybit_api_key}{param_str}"
        signature = hmac.new(
            self.bybit_api_secret.encode('utf-8'),
            payload.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        return signature
    
    async def withdraw_to_bybit(
        self,
        user_id: str,
        amount_usdt: float,
        force: bool = False
    ) -> Dict[str, Any]:
        """
        Withdraw USDT to Bybit wallet address.
        
        Args:
            user_id: User UUID
            amount_usdt: Amount to withdraw in USDT
            force: Force withdrawal even if below threshold (admin use)
            
        Returns:
            Dictionary with withdrawal result
        """
        try:
            user_uuid = uuid.UUID(user_id)
        except ValueError:
            return {
                "success": False,
                "error": "Invalid user ID format"
            }
        
        user = self.db.query(User).filter(User.id == user_uuid).first()
        if not user:
            return {
                "success": False,
                "error": "User not found"
            }
        
        # Validate amount
        if amount_usdt < self.MIN_WITHDRAWAL_USDT:
            return {
                "success": False,
                "error": f"Minimum withdrawal amount is {self.MIN_WITHDRAWAL_USDT} USDT"
            }
        
        # Check balance
        current_usdt = self.credits_to_usdt(user.credit_balance)
        if current_usdt < amount_usdt:
            return {
                "success": False,
                "error": f"Insufficient balance. Available: {current_usdt} USDT, Requested: {amount_usdt} USDT"
            }
        
        # Check threshold (unless forced)
        if not force and current_usdt < self.WITHDRAWAL_THRESHOLD_USD:
            return {
                "success": False,
                "error": f"Balance must reach ${self.WITHDRAWAL_THRESHOLD_USD} for automatic withdrawal"
            }
        
        # 30-day Royal Hospitality: no credit deduction during grace period
        if getattr(user, "is_in_royal_hospitality_period", None) and user.is_in_royal_hospitality_period():
            return {
                "success": False,
                "error": "Cannot withdraw during Royal Hospitality period (30 days)."
            }
        
        # Calculate credits to deduct
        credits_to_deduct = self.usdt_to_credits(amount_usdt)
        
        # Validate Bybit credentials
        if self.bybit_api_key == "X" or self.bybit_api_secret == "X" or self.bybit_wallet_address == "X":
            return {
                "success": False,
                "error": "Bybit API credentials not configured. Please set BYBIT_API_KEY, BYBIT_API_SECRET, and BYBIT_WALLET_ADDRESS in .env"
            }
        
        # Prepare withdrawal request to Bybit
        timestamp = str(int(time.time() * 1000))
        params = {
            "coin": "USDT",
            "chain": "TRC20",  # TRC20 network for USDT
            "address": self.bybit_wallet_address,
            "amount": str(amount_usdt),
            "timestamp": timestamp,
            "api_key": self.bybit_api_key
        }
        
        signature = self._generate_bybit_signature(params, timestamp)
        params["sign"] = signature
        
        try:
            # Make withdrawal request to Bybit API
            response = requests.post(
                f"{self.bybit_base_url}/v5/asset/withdraw/create",
                json=params,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            result = response.json()
            
            # Check if withdrawal was successful
            if result.get("retCode") == 0:
                # Deduct credits from user account
                balance_before = user.credit_balance
                user.credit_balance -= credits_to_deduct
                balance_after = user.credit_balance
                
                # Create withdrawal transaction
                withdrawal_transaction = CreditTransaction(
                    user_id=user.id,
                    transaction_type=CreditTransactionType.ADMIN_ADJUSTMENT,  # Using admin adjustment for withdrawals
                    amount=-credits_to_deduct,  # Negative for deduction
                    description=f"Automatic withdrawal: {amount_usdt} USDT to Bybit wallet",
                    balance_after=balance_after
                )
                self.db.add(withdrawal_transaction)
                self.db.flush()
                
                # Create ledger entry
                ledger_entry = CreditLedger(
                    user_id=user.id,
                    transaction_id=withdrawal_transaction.id,
                    entry_type="debit",
                    amount=credits_to_deduct,
                    balance_before=balance_before,
                    balance_after=balance_after,
                    description=f"💰 Automatic Withdrawal: {amount_usdt} USDT sent to Bybit wallet (Address: {self.bybit_wallet_address[:10]}...)",
                    category="withdrawal"
                )
                self.db.add(ledger_entry)
                
                self.db.commit()
                self.db.refresh(user)
                self.db.refresh(withdrawal_transaction)
                self.db.refresh(ledger_entry)
                
                return {
                    "success": True,
                    "message": f"Successfully withdrew {amount_usdt} USDT to Bybit wallet",
                    "user_id": user_id,
                    "amount_usdt": amount_usdt,
                    "credits_deducted": credits_to_deduct,
                    "balance_before_usdt": self.credits_to_usdt(balance_before),
                    "balance_after_usdt": self.credits_to_usdt(balance_after),
                    "bybit_transaction_id": result.get("result", {}).get("id"),
                    "bybit_wallet_address": self.bybit_wallet_address,
                    "timestamp": datetime.utcnow().isoformat()
                }
            else:
                error_msg = result.get("retMsg", "Unknown error")
                return {
                    "success": False,
                    "error": f"Bybit withdrawal failed: {error_msg}",
                    "bybit_response": result
                }
                
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": f"Failed to connect to Bybit API: {str(e)}"
            }
        except Exception as e:
            self.db.rollback()
            return {
                "success": False,
                "error": f"Withdrawal processing failed: {str(e)}"
            }
    
    async def process_automatic_withdrawal(self, user_id: str) -> Dict[str, Any]:
        """
        AUTOMATIC WITHDRAWAL FUNCTION [cite: 2026-02-03]
        
        Automatically triggers withdrawal to Bybit when user's balance hits $50.
        This function should be called when checking user balances.
        
        Args:
            user_id: User UUID
            
        Returns:
            Dictionary with withdrawal processing result
        """
        # Check if user is eligible for withdrawal
        threshold_check = self.check_withdrawal_threshold(user_id)
        
        if not threshold_check.get("success"):
            return threshold_check
        
        if not threshold_check.get("eligible_for_withdrawal"):
            return {
                "success": False,
                "message": "Balance has not reached withdrawal threshold",
                "current_balance_usdt": threshold_check.get("usdt_balance"),
                "threshold_usdt": threshold_check.get("threshold")
            }
        
        # Get withdrawable amount
        withdrawable_amount = threshold_check.get("withdrawable_amount", 0.0)
        
        # Process automatic withdrawal
        withdrawal_result = await self.withdraw_to_bybit(
            user_id=user_id,
            amount_usdt=withdrawable_amount,
            force=False
        )
        
        return withdrawal_result
    
    def get_withdrawal_history(self, user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get user's withdrawal history.
        
        Args:
            user_id: User UUID
            limit: Maximum number of records to return
            
        Returns:
            List of withdrawal transactions
        """
        try:
            user_uuid = uuid.UUID(user_id)
        except ValueError:
            return []
        
        # Get withdrawal transactions from ledger
        withdrawals = self.db.query(CreditLedger).filter(
            CreditLedger.user_id == user_uuid,
            CreditLedger.category == "withdrawal"
        ).order_by(CreditLedger.timestamp.desc()).limit(limit).all()
        
        return [
            {
                "transaction_id": str(w.transaction_id),
                "amount_usdt": self.credits_to_usdt(w.amount),
                "credits_deducted": w.amount,
                "balance_before_usdt": self.credits_to_usdt(w.balance_before),
                "balance_after_usdt": self.credits_to_usdt(w.balance_after),
                "description": w.description,
                "timestamp": w.timestamp.isoformat()
            }
            for w in withdrawals
        ]


# Global helper functions
def create_wallet_finance_handler(db: Session) -> WalletFinanceHandler:
    """
    Factory function to create WalletFinanceHandler instance.
    
    Args:
        db: SQLAlchemy database session
        
    Returns:
        WalletFinanceHandler instance
    """
    return WalletFinanceHandler(db)


async def process_automatic_withdrawal_if_eligible(
    db: Session,
    user_id: str
) -> Dict[str, Any]:
    """
    Convenience function to process automatic withdrawal if user is eligible.
    [cite: 2026-02-03]
    
    Args:
        db: SQLAlchemy database session
        user_id: User UUID
        
    Returns:
        Dictionary with withdrawal processing result
    """
    handler = WalletFinanceHandler(db)
    return await handler.process_automatic_withdrawal(user_id)


def get_user_usdt_balance(
    db: Session,
    user_id: str
) -> Optional[float]:
    """
    Get user's USDT balance from their credits.
    
    Args:
        db: SQLAlchemy database session
        user_id: User UUID
        
    Returns:
        USDT balance or None
    """
    handler = WalletFinanceHandler(db)
    return handler.get_user_usdt_balance(user_id)


def credits_to_usdt_value(credits: float) -> float:
    """
    Convert credits (Habbet) to USDT value.
    
    Args:
        credits: Number of credits
        
    Returns:
        USDT equivalent value
    """
    handler = WalletFinanceHandler(SessionLocal())
    return handler.credits_to_usdt(credits)
