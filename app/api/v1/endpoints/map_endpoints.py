"""
BILI Map: VIP businesses and manual store pins for map display.
No Google Places API: store locations are manual (admin-added) or from registered businesses.
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.models.business import Business, BusinessStatus
from app.models.manual_map_pin import ManualMapPin
from pydantic import BaseModel

router = APIRouter()


class MapBusinessMarker(BaseModel):
    id: str
    google_place_id: str
    name: str
    latitude: float
    longitude: float
    is_vip: bool = True  # Always true for registered BILI businesses
    display_name: str
    category: Optional[str] = None
    rating: Optional[float] = None

    class Config:
        from_attributes = True


class MapBusinessesResponse(BaseModel):
    businesses: List[MapBusinessMarker]
    total: int


@router.get("/vip-businesses", response_model=MapBusinessesResponse)
async def get_vip_businesses_for_map(
    latitude: Optional[float] = Query(None),
    longitude: Optional[float] = Query(None),
    radius_km: Optional[float] = Query(50, description="Radius to include businesses"),
    db: Session = Depends(get_db),
):
    """
    Returns only BILI-registered (claimed) businesses for the map.
    These must appear at the top with a VIP icon; any duplicate from Google
    should be overridden by this record (match by google_place_id).
    """
    query = db.query(Business).filter(
        Business.status != BusinessStatus.UNCLAIMED,
        Business.latitude.isnot(None),
        Business.longitude.isnot(None),
    )
    businesses = query.all()

    if latitude is not None and longitude is not None and radius_km is not None:
        filtered = []
        for b in businesses:
            # Approximate distance in km (simplified)
            d = ((b.latitude - latitude) ** 2 + (b.longitude - longitude) ** 2) ** 0.5 * 111
            if d <= radius_km:
                filtered.append(b)
        businesses = filtered

    markers = [
        MapBusinessMarker(
            id=str(b.id),
            google_place_id=b.google_place_id,
            name=b.google_name,
            latitude=b.latitude,
            longitude=b.longitude,
            is_vip=True,
            display_name=b.display_name,
            category=b.google_category,
            rating=b.google_rating,
        )
        for b in businesses
    ]
    return MapBusinessesResponse(businesses=markers, total=len(markers))


class MapPinOut(BaseModel):
    id: str
    name: str
    latitude: float
    longitude: float
    address: Optional[str] = None
    profile_url: Optional[str] = None
    latest_content_url: Optional[str] = None
    latest_content_thumbnail: Optional[str] = None
    latest_content_title: Optional[str] = None
    content_fetched_at: Optional[str] = None

    class Config:
        from_attributes = True


@router.get("/pins", response_model=List[MapPinOut])
async def get_map_pins(db: Session = Depends(get_db)):
    """
    Returns all admin-added store pins for the map. No Places API.
    All users see the same pins; add pins via Admin Panel (paste coordinates/URL).
    """
    pins = db.query(ManualMapPin).order_by(ManualMapPin.created_at.desc()).all()
    return [
        MapPinOut(
            id=str(p.id),
            name=p.name,
            latitude=p.latitude,
            longitude=p.longitude,
            address=p.address,
            profile_url=p.profile_url,
            latest_content_url=p.latest_content_url,
            latest_content_thumbnail=p.latest_content_thumbnail,
            latest_content_title=p.latest_content_title,
            content_fetched_at=p.content_fetched_at.isoformat() if p.content_fetched_at else None,
        )
        for p in pins
    ]
