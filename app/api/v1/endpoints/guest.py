"""
BILI Master System - Guest Access Endpoints
Permanent Guest Access: Users can browse all content without login/signup
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from app.core.database import get_db
from app.models.business import Business, BusinessStatus
from app.models.post import Post
from app.schemas.business import BusinessResponse, BusinessListResponse
from app.schemas.post import PostResponse

router = APIRouter()


@router.get("/businesses", response_model=BusinessListResponse)
async def browse_businesses(
    latitude: Optional[float] = Query(None, description="User latitude"),
    longitude: Optional[float] = Query(None, description="User longitude"),
    radius_km: Optional[float] = Query(10, description="Search radius in kilometers"),
    category: Optional[str] = Query(None, description="Filter by category"),
    db: Session = Depends(get_db)
):
    """
    Browse all businesses as a guest.
    No authentication required - permanent guest access.
    Shows both claimed and unclaimed businesses.
    """
    query = db.query(Business)
    
    # Filter by category if provided
    if category:
        query = query.filter(Business.google_category == category)
    
    # If location provided, filter by radius
    if latitude and longitude:
        # Simple radius filter (for production, use PostGIS for accurate distance)
        businesses = query.all()
        # Filter by approximate radius
        filtered_businesses = []
        for business in businesses:
            if business.latitude and business.longitude:
                # Calculate approximate distance (Haversine would be better)
                distance = ((business.latitude - latitude) ** 2 + 
                           (business.longitude - longitude) ** 2) ** 0.5 * 111  # Rough km conversion
                if distance <= radius_km:
                    filtered_businesses.append(business)
        businesses = filtered_businesses
    else:
        businesses = query.limit(100).all()
    
    return BusinessListResponse(
        businesses=[BusinessResponse.from_orm(b) for b in businesses],
        total=len(businesses)
    )


@router.get("/businesses/{business_id}", response_model=BusinessResponse)
async def get_business_details(
    business_id: str,
    db: Session = Depends(get_db)
):
    """
    Get business details as a guest.
    Shows Google Mirror data (read-only) and claim status.
    """
    business = db.query(Business).filter(Business.id == business_id).first()
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")
    
    return BusinessResponse.from_orm(business)


@router.get("/posts", response_model=List[PostResponse])
async def browse_posts(
    latitude: Optional[float] = Query(None),
    longitude: Optional[float] = Query(None),
    radius_km: Optional[float] = Query(15),
    media_type: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """
    Browse all active posts as a guest.
    No authentication required.
    """
    query = db.query(Post).filter(
        Post.is_active == True,
        Post.is_expired == False,
        Post.is_visible == True
    )
    
    if media_type:
        query = query.filter(Post.media_type == media_type)
    
    posts = query.order_by(Post.created_at.desc()).limit(100).all()
    
    # Filter by radius if location provided
    if latitude and longitude:
        filtered_posts = []
        for post in posts:
            if post.latitude and post.longitude:
                distance = ((post.latitude - latitude) ** 2 + 
                           (post.longitude - longitude) ** 2) ** 0.5 * 111
                if distance <= radius_km:
                    filtered_posts.append(post)
        posts = filtered_posts
    
    return [PostResponse.from_orm(p) for p in posts]


@router.get("/posts/{post_id}", response_model=PostResponse)
async def get_post_details(
    post_id: str,
    db: Session = Depends(get_db)
):
    """Get post details as a guest"""
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    return PostResponse.from_orm(post)
