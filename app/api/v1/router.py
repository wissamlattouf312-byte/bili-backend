"""
BILI Master System - API Router
"""
from fastapi import APIRouter
from app.api.v1.endpoints import guest, claim, radar, admin, credits, location, wallet, map_endpoints, flash_deal

api_router = APIRouter()

# Guest Access Routes (No authentication required)
api_router.include_router(guest.router, prefix="/guest", tags=["Guest Access"])

# Claim Routes
api_router.include_router(claim.router, prefix="/claim", tags=["Claim Business"])

# Location Routes (Global GPS System) [cite: 2026-02-03, 2026-01-09]
api_router.include_router(location.router, prefix="/location", tags=["GPS Location"])

# Radar Routes
api_router.include_router(radar.router, prefix="/radar", tags=["Live Radar"])

# Credits Routes
api_router.include_router(credits.router, prefix="/credits", tags=["Credits"])

# Wallet Finance Routes [cite: 2026-02-09]
api_router.include_router(wallet.router, prefix="/wallet", tags=["Wallet Finance"])

# Admin Routes (Protected)
api_router.include_router(admin.router, prefix="/admin", tags=["Admin"])
api_router.include_router(map_endpoints.router, prefix="/map", tags=["Map"])
api_router.include_router(flash_deal.router, prefix="/flash-deals", tags=["Flash Deals"])
