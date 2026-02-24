#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

"""
DEPRECATED: App now uses Maps JavaScript API + static places.json; Places API not used.
Kept for reference only. Do not run in deploy pipelines.

Fetch places from Google Maps Places API (Legacy) in LEBANON only.
STRICT FILTER: Only fetch and keep places that look like they have active offers,
discounts, or promotional content (Active Opportunities). Others are skipped.

Limitation: The public Places API does NOT expose "Live Deal" or "Special Offer"
data that businesses post on their Google profile. We apply a keyword-based
heuristic on name/vicinity and require OPERATIONAL status + photos so the BILI
map is populated exclusively with places that advertise offers in their listing.
For true offer data you would need another source (e.g. business partnerships).

Requires: GOOGLE_MAPS_API_KEY in .env or environment.
Output: scripts/output/lebanon_places_YYYYMMDD_HHMMSS.json
"""

import json
import os
import time
from pathlib import Path
from urllib.parse import urlencode

import requests
from dotenv import load_dotenv

# --- Configuration (Lebanon only; no Dubai or other countries) ---
TARGET_PLACES = 10_000
CREDIT_LIMIT_USD = 200.0

# Strict Active Opportunities filter: only keep places that suggest offers/promos.
# (Places API does not return actual "Live Deal" or "Special Offer" fields.)
ACTIVE_OPPORTUNITY_KEYWORDS = (
    "offer", "offers", "discount", "discounts", "promo", "promotion", "promotions",
    "deal", "deals", "sale", "sales", "special", "specials", "% off", "off %",
    "coupon", "coupons", "happy hour", "happy hours", "reduction", "reductions",
    "عرض", "عروض", "خصم", "خصومات", "تخفيض", "تخفيضات", "برومو", "عرض خاص",
)

# Lebanon bounding box (approximate): entire country, no other regions
LEBANON_BOUNDS = {
    "south": 33.05,
    "north": 34.69,
    "west": 35.10,
    "east": 36.63,
}

# Pricing per 1,000 requests (USD) – Places API Legacy
# https://developers.google.com/maps/billing-and-pricing
# (Only Nearby Search is used here to stay under $200.)
COST_NEARBY_SEARCH_PER_1K = 32.0

# Rate limit: stay under Places API quotas (e.g. 1000/min for nearby)
REQUEST_DELAY_SEC = 0.05
OUTPUT_DIR = Path(__file__).resolve().parent / "output"


def load_api_key():
    load_dotenv(Path(__file__).resolve().parent.parent / ".env")
    key = os.environ.get("GOOGLE_MAPS_API_KEY", "").strip()
    if not key:
        raise SystemExit("Set GOOGLE_MAPS_API_KEY in .env (or environment).")
    return key


def in_lebanon_bounds(lat: float, lng: float) -> bool:
    return (
        LEBANON_BOUNDS["south"] <= lat <= LEBANON_BOUNDS["north"]
        and LEBANON_BOUNDS["west"] <= lng <= LEBANON_BOUNDS["east"]
    )


def has_active_opportunity_signal(place: dict) -> bool:
    """
    Strict filter: only True if the place appears to have active offers/promos.
    Uses name and vicinity only (Places API does not expose Live Deal / Special Offer).
    Also requires business_status OPERATIONAL when present.
    """
    status = (place.get("business_status") or "").strip().upper()
    if status and status != "OPERATIONAL":
        return False
    name = (place.get("name") or "").lower()
    vicinity = (place.get("vicinity") or "").lower()
    combined = f"{name} {vicinity}"
    for kw in ACTIVE_OPPORTUNITY_KEYWORDS:
        if kw.lower() in combined:
            return True
    return False


def grid_points_lebanon(step_km: float = 4.0) -> list[tuple[float, float]]:
    """Generate (lat, lng) points inside Lebanon for Nearby Search. ~1 deg lat ≈ 111 km."""
    points = []
    step_deg = step_km / 111.0
    lat = LEBANON_BOUNDS["south"]
    while lat <= LEBANON_BOUNDS["north"]:
        lng = LEBANON_BOUNDS["west"]
        while lng <= LEBANON_BOUNDS["east"]:
            points.append((lat, lng))
            lng += step_deg
        lat += step_deg
    return points


def nearby_search(key: str, lat: float, lng: float, page_token=None) -> dict:
    url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    params = {
        "location": f"{lat},{lng}",
        "radius": 5000,
        "key": key,
    }
    if page_token:
        params["pagetoken"] = page_token
    else:
        params["type"] = "establishment"  # broad type to get variety
    resp = requests.get(url, params=params, timeout=30)
    resp.raise_for_status()
    return resp.json()


def build_photo_url(key: str, photo_reference: str, max_width: int = 800) -> str:
    return (
        "https://maps.googleapis.com/maps/api/place/photo?"
        + urlencode({"maxwidth": max_width, "photo_reference": photo_reference, "key": key})
    )


def run(key: str) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    out_file = OUTPUT_DIR / f"lebanon_places_{time.strftime('%Y%m%d_%H%M%S')}.json"

    seen_ids: set[str] = set()
    places: list[dict] = []
    cost_usd = 0.0
    search_requests = 0
    photo_count = 0
    grid = grid_points_lebanon(step_km=4.0)

    def would_exceed_limit(extra_usd: float) -> bool:
        return (cost_usd + extra_usd) > CREDIT_LIMIT_USD

    print(f"Lebanon bounds: {LEBANON_BOUNDS}")
    print(f"Grid points: {len(grid)}")
    print(f"Strict filter: Active Opportunities only (offer/discount/promo/deal/sale in name or address)")
    print(f"Target: {TARGET_PLACES} places | Limit: ${CREDIT_LIMIT_USD}")
    print("---")

    for idx, (lat, lng) in enumerate(grid):
        if len(places) >= TARGET_PLACES:
            break
        if would_exceed_limit(COST_NEARBY_SEARCH_PER_1K / 1000):
            print("Credit limit reached (search). Stopping.")
            break

        data = nearby_search(key, lat, lng)
        time.sleep(REQUEST_DELAY_SEC)
        search_requests += 1
        cost_usd += COST_NEARBY_SEARCH_PER_1K / 1000

        if data.get("status") not in ("OK", "ZERO_RESULTS"):
            print(f"Nearby search status: {data.get('status')}")
            continue

        results = data.get("results", [])
        next_page_token = data.get("next_page_token")

        for r in results:
            if len(places) >= TARGET_PLACES:
                break
            place_id = r.get("place_id")
            if not place_id or place_id in seen_ids:
                continue
            # Only include places with visual content (at least one photo)
            photos = r.get("photos") or []
            if not photos:
                continue
            # Strict: only places that signal active offers / promos (name or vicinity)
            if not has_active_opportunity_signal(r):
                continue
            loc = r.get("geometry", {}).get("location", {})
            plat, plng = loc.get("lat"), loc.get("lng")
            if plat is None or plng is None:
                continue
            if not in_lebanon_bounds(plat, plng):
                continue
            seen_ids.add(place_id)
            refs = [p.get("photo_reference") for p in photos[:5] if p.get("photo_reference")]
            place_record = {
                "place_id": place_id,
                "name": r.get("name"),
                "vicinity": r.get("vicinity"),
                "lat": plat,
                "lng": plng,
                "rating": r.get("rating"),
                "user_ratings_total": r.get("user_ratings_total"),
                "types": r.get("types", []),
                "photo_references": refs,
                "photo_urls": [build_photo_url(key, ref) for ref in refs[:3]],
                "active_opportunity": True,
            }
            places.append(place_record)
            photo_count += len(place_record["photo_urls"])

        # Next page for this location (same cost as one search)
        while next_page_token and len(places) < TARGET_PLACES:
            if would_exceed_limit(COST_NEARBY_SEARCH_PER_1K / 1000):
                break
            time.sleep(1.0)  # token not valid immediately
            data = nearby_search(key, lat, lng, page_token=next_page_token)
            time.sleep(REQUEST_DELAY_SEC)
            search_requests += 1
            cost_usd += COST_NEARBY_SEARCH_PER_1K / 1000
            next_page_token = data.get("next_page_token")
            for r in data.get("results", []):
                place_id = r.get("place_id")
                if not place_id or place_id in seen_ids:
                    continue
                photos = r.get("photos") or []
                if not photos:
                    continue
                if not has_active_opportunity_signal(r):
                    continue
                loc = r.get("geometry", {}).get("location", {})
                plat, plng = loc.get("lat"), loc.get("lng")
                if plat is None or plng is None or not in_lebanon_bounds(plat, plng):
                    continue
                seen_ids.add(place_id)
                refs = [p.get("photo_reference") for p in photos[:5] if p.get("photo_reference")]
                place_record = {
                    "place_id": place_id,
                    "name": r.get("name"),
                    "vicinity": r.get("vicinity"),
                    "lat": plat,
                    "lng": plng,
                    "rating": r.get("rating"),
                    "user_ratings_total": r.get("user_ratings_total"),
                    "types": r.get("types", []),
                    "photo_references": refs,
                    "photo_urls": [build_photo_url(key, ref) for ref in refs[:3]],
                    "active_opportunity": True,
                }
                places.append(place_record)
                photo_count += len(place_record["photo_urls"])

        if (idx + 1) % 20 == 0 or (len(places) > 0 and len(places) % 500 == 0):
            print(f"Places: {len(places)} | Search requests: {search_requests} | Est. cost: ${cost_usd:.2f}")

    # Redact API key from saved photo_urls (user can add key when using)
    for p in places:
        p["photo_urls"] = [u.replace(key, "YOUR_API_KEY") for u in p["photo_urls"]]
        if "photo_references" in p:
            pass  # keep references for re-building URLs with key

    payload = {
        "meta": {
            "country": "Lebanon",
            "filter": "active_opportunities_only",
            "description": "Places with offer/discount/promo/deal/sale signals in name or address; OPERATIONAL only",
            "total_places": len(places),
            "estimated_cost_usd": round(cost_usd, 2),
            "credit_limit_usd": CREDIT_LIMIT_USD,
            "search_requests": search_requests,
            "photo_urls_count": photo_count,
        },
        "places": places,
    }

    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    print("---")
    print(f"Done. Places: {len(places)} | Est. cost: ${cost_usd:.2f}")
    print(f"Output: {out_file}")


if __name__ == "__main__":
    api_key = load_api_key()
    run(api_key)
