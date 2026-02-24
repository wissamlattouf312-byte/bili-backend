"""
BILI Master System - Claim Schemas
"""
from pydantic import BaseModel
from typing import Optional


class ClaimRequest(BaseModel):
    """
    Claim Request Schema - Supports both general claim and business claim.
    
    For general claim (available at any time): business_id is optional
    For business claim: business_id is required
    """
    business_id: Optional[str] = None  # Optional - allows claim without business
    phone_number: Optional[str] = None
    display_name: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    device_id: Optional[str] = None  # For guest session tracking
    referral_code: Optional[str] = None  # From ?ref= in share link (Viral Gateway)


class ClaimResponse(BaseModel):
    success: bool
    message: str
    user_id: str
    credit_balance: float
    royal_hospitality_end_date: Optional[str] = None
    business_id: Optional[str] = None  # Optional - only present if business was claimed
    is_new_user: Optional[bool] = False
    is_new_member: Optional[bool] = False  # True if converted from guest to member
    transaction_id: Optional[str] = None
    referral_code: Optional[str] = None  # User's code to share (?ref=)
