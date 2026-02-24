"""
Step 5: Flash Deals - merchants post deals that auto-expire after 24 hours.
"""
from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List, Optional
from pydantic import BaseModel
from app.core.database import get_db
from app.models.flash_deal import FlashDeal
from app.models.business import Business, BusinessStatus

router = APIRouter()


class FlashDealCreate(BaseModel):
    business_id: str
    owner_id: str
    title: str
    description: Optional[str] = None
    image_url: Optional[str] = None
    latitude: float
    longitude: float


class FlashDealResponse(BaseModel):
    id: str
    business_id: str
    title: str
    description: Optional[str]
    image_url: Optional[str]
    latitude: float
    longitude: float
    expires_at: datetime
    created_at: datetime
    is_expired: bool

    class Config:
        from_attributes = True


@router.post("/", response_model=FlashDealResponse)
async def create_flash_deal(
    payload: FlashDealCreate,
    db: Session = Depends(get_db),
):
    """Merchant creates a Flash Deal; it auto-expires after 24 hours."""
    business = db.query(Business).filter(Business.id == payload.business_id).first()
    if not business or business.status == BusinessStatus.UNCLAIMED:
        raise HTTPException(status_code=404, detail="Business not found or not claimed")
    if str(business.owner_id) != str(payload.owner_id):
        raise HTTPException(status_code=403, detail="Not the business owner")

    expires_at = datetime.utcnow() + timedelta(hours=24)
    deal = FlashDeal(
        business_id=payload.business_id,
        owner_id=payload.owner_id,
        title=payload.title,
        description=payload.description,
        image_url=payload.image_url,
        latitude=payload.latitude,
        longitude=payload.longitude,
        expires_at=expires_at,
    )
    db.add(deal)
    db.commit()
    db.refresh(deal)
    return FlashDealResponse(
        id=str(deal.id),
        business_id=str(deal.business_id),
        title=deal.title,
        description=deal.description,
        image_url=deal.image_url,
        latitude=deal.latitude,
        longitude=deal.longitude,
        expires_at=deal.expires_at,
        created_at=deal.created_at,
        is_expired=deal.is_expired,
    )


@router.get("/active", response_model=List[FlashDealResponse])
async def list_active_flash_deals(
    db: Session = Depends(get_db),
):
    """List Flash Deals that have not yet expired (for map and feed)."""
    now = datetime.utcnow()
    deals = db.query(FlashDeal).filter(FlashDeal.expires_at > now).order_by(FlashDeal.created_at.desc()).all()
    return [
        FlashDealResponse(
            id=str(d.id),
            business_id=str(d.business_id),
            title=d.title,
            description=d.description,
            image_url=d.image_url,
            latitude=d.latitude,
            longitude=d.longitude,
            expires_at=d.expires_at,
            created_at=d.created_at,
            is_expired=d.is_expired,
        )
        for d in deals
    ]
