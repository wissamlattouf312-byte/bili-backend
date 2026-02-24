"""
BILI Master System - Claim Endpoint
THE FLASHING "CLAIM" BUTTON: Awards 20 Credits (حبّات) and Instantly Registers User [cite: 2026-02-03]

Complete implementation:
- Instant user registration (guest → member)
- Awards 20 BILI Credits (حبّات) - Available at any time
- Sets 30-Day Royal Hospitality Period
- Supports both general claim and business claim
- Creates credit transaction and ledger entry

Uses auth_handler.py for clean, centralized logic [cite: 2026-02-09]
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from app.core.database import get_db, try_get_db
from app.core.config import settings
from app.models.business import Business, BusinessStatus
from app.models.user import User
from app.models.credit import CreditTransaction, CreditTransactionType
from app.schemas.claim import ClaimRequest, ClaimResponse
from app.auth_handler import AuthHandler, process_claim_reward
from app.core.websocket import websocket_manager
import uuid

router = APIRouter()


@router.post("/reward", response_model=ClaimResponse)
async def claim_reward(
    request: ClaimRequest,
    db: Session | None = Depends(try_get_db),
):
    """
    THE FLASHING CLAIM BUTTON ENDPOINT - Available at any time [cite: 2026-02-03]
    
    Prominent, flashing 'Claim' button that offers 20 'Habbet' (rewards/tokens)
    to the user at any time. No business_id required.
    
    When user clicks "CLAIM 20 CREDITS" button:
    1. Instantly register user as member (if guest)
    2. Award 20 BILI Credits (حبّات)
    3. Set 30-Day Royal Hospitality Period
    4. Convert Guest → Active Member
    
    No login/signup barriers - instant onboarding.
    Uses auth_handler.py for clean logic structure [cite: 2026-02-09]
    """
    # If database is not available, return a graceful demo response
    if db is None:
        demo_user_id = str(uuid.uuid4())
        now = datetime.utcnow()
        demo_end_date = now.replace(microsecond=0)

        return ClaimResponse(
            success=True,
            message="Demo mode: 20 Habbet credited (database offline).",
            user_id=demo_user_id,
            credit_balance=20.0,
            royal_hospitality_end_date=demo_end_date,
            business_id=None,
            is_new_user=True,
            is_new_member=True,
            transaction_id=str(uuid.uuid4()),
        )

    try:
        # Use auth_handler for centralized logic when DB is available
        result = process_claim_reward(
            db=db,
            phone_number=request.phone_number,
            device_id=request.device_id,
            display_name=request.display_name,
            latitude=request.latitude,
            longitude=request.longitude,
            business_id=None,  # General claim, no business
            referral_code=request.referral_code,
        )
        
        # Broadcast user status update via WebSocket
        try:
            await websocket_manager.broadcast_user_status(result["user_id"], "online")
        except Exception:
            pass  # Don't fail if WebSocket is unavailable
        
        return ClaimResponse(
            success=result["success"],
            message=result["message"],
            user_id=result["user_id"],
            credit_balance=result["credit_balance"],
            royal_hospitality_end_date=result["royal_hospitality_end_date"],
            business_id=None,
            is_new_user=False,  # Will be set by handler if needed
            is_new_member=result.get("is_new_member", False),
            transaction_id=result["transaction_id"],
            referral_code=result.get("referral_code"),
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to claim reward: {str(e)}")


@router.post("/business", response_model=ClaimResponse)
async def claim_business(
    request: ClaimRequest,
    db: Session = Depends(get_db)
):
    """
    CLAIM BUSINESS ENDPOINT - Awards 20 Credits and Claims Business [cite: 2026-02-03]
    
    When user clicks "CLAIM 20 CREDITS" button with a business:
    1. Instantly register user as member (if guest)
    2. Award 20 BILI Credits (حبّات)
    3. Set 30-Day Royal Hospitality Period
    4. Claim the business profile
    
    Requires business_id in request.
    Uses auth_handler.py for clean logic structure [cite: 2026-02-09]
    """
    if not request.business_id:
        raise HTTPException(status_code=400, detail="business_id is required for business claim")
    
    try:
        # Step 1: Validate business exists and is unclaimed
        try:
            business_id_uuid = uuid.UUID(request.business_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid business ID format")
        
        business = db.query(Business).filter(Business.id == business_id_uuid).first()
        if not business:
            raise HTTPException(status_code=404, detail="Business not found")
        
        if business.status != BusinessStatus.CLAIMED:
            # Business is unclaimed, proceed with claim
            pass
        else:
            # Check if user already claimed this business
            handler = AuthHandler(db)
            user = None
            if request.phone_number:
                user = handler.get_user_by_phone(request.phone_number)
            
            if user and business.owner_id == user.id:
                raise HTTPException(status_code=400, detail="You have already claimed this business")
            else:
                raise HTTPException(
                    status_code=400, 
                    detail="Business already claimed by another user"
                )
        
        # Step 2: Use auth_handler to process claim reward
        result = process_claim_reward(
            db=db,
            phone_number=request.phone_number,
            device_id=request.device_id,
            display_name=request.display_name,
            latitude=request.latitude,
            longitude=request.longitude,
            business_id=request.business_id
        )
        
        # Step 3: Claim the business
        claim_date = datetime.utcnow()
        business.status = BusinessStatus.CLAIMED
        business.owner_id = uuid.UUID(result["user_id"])
        business.claimed_at = claim_date
        
        db.commit()
        db.refresh(business)
        
        # Broadcast user status update via WebSocket
        try:
            await websocket_manager.broadcast_user_status(result["user_id"], "online")
        except Exception:
            pass  # Don't fail if WebSocket is unavailable
        
        return ClaimResponse(
            success=result["success"],
            message=f"🎉 Business claimed successfully! {result['message']}",
            user_id=result["user_id"],
            credit_balance=result["credit_balance"],
            royal_hospitality_end_date=result["royal_hospitality_end_date"],
            business_id=request.business_id,
            is_new_user=False,
            is_new_member=result.get("is_new_member", False),
            transaction_id=result["transaction_id"]
        )
        
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to claim business: {str(e)}")


@router.get("/claim-history/{user_id}")
async def get_user_claim_history(
    user_id: str,
    db: Session = Depends(get_db)
):
    """
    Get claim history for a user (all businesses they've claimed).
    """
    try:
        user_uuid = uuid.UUID(user_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid user ID format")
    
    user = db.query(User).filter(User.id == user_uuid).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get all claimed businesses by this user
    claimed_businesses = db.query(Business).filter(
        Business.owner_id == user.id,
        Business.status == BusinessStatus.CLAIMED
    ).order_by(Business.claimed_at.desc()).all()
    
    # Get claim transactions
    claim_transactions = db.query(CreditTransaction).filter(
        CreditTransaction.user_id == user.id,
        CreditTransaction.transaction_type == CreditTransactionType.CLAIM_REWARD
    ).order_by(CreditTransaction.timestamp.desc()).all()
    
    return {
        "user_id": str(user.id),
        "total_claims": len(claimed_businesses),
        "total_credits_earned": sum(t.amount for t in claim_transactions),
        "royal_hospitality_end_date": user.royal_hospitality_end_date.isoformat() if user.royal_hospitality_end_date else None,
        "is_in_royal_hospitality": user.is_in_royal_hospitality_period(),
        "claimed_businesses": [
            {
                "business_id": str(b.id),
                "business_name": b.display_name,
                "claimed_at": b.claimed_at.isoformat() if b.claimed_at else None
            }
            for b in claimed_businesses
        ],
        "claim_transactions": [
            {
                "transaction_id": str(t.id),
                "amount": float(t.amount),
                "business_id": str(t.reference_id) if t.reference_id else None,
                "timestamp": t.timestamp.isoformat(),
                "description": t.description
            }
            for t in claim_transactions
        ]
    }
