#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DEPRECATED: App now uses Maps JavaScript API + static places.json; Places API not used.
Kept for reference or one-off re-seeds. Do not run in deploy pipelines.

BILI Google Maps Data Strategy – Budgeted seed script.
- Official Places API only (Nearby Search; no scraping).
- Full Lebanon: grid over bounding box (south 33.05, north 34.69, west 35.10, east 36.63).
- Filters: rating >= 4.2, reviews >= 50, popular categories only.
- Minimal data: name, place_id, rating, user_ratings_total, lat, lng, vicinity, one photo.
- Photos: download one photo per place and save under frontend/public/place_photos/.
- Budget: internal request counter; hard stop at $200. Set Google billing alert at $180.
- No re-fetching: skip place_id if already in existing places.json or in this run.

Requires: GOOGLE_MAPS_API_KEY in bili/.env (do not commit; do not use on Netlify).
Output: frontend/public/places.json, frontend/public/place_photos/<place_id>.jpg
"""

from __future__ import annotations

import json
import os
import re
import time
from pathlib import Path
from urllib.parse import urlencode

import requests
from dotenv import load_dotenv

# --- Budget (critical) ---
CREDIT_LIMIT_USD = 200.0
# Approximate per-request costs (USD). Adjust if Google changes pricing.
COST_NEARBY_SEARCH = 32.0 / 1000   # $32 per 1000
COST_PLACE_PHOTO = 7.0 / 1000     # $7 per 1000 (per photo)
REQUEST_DELAY_SEC = 0.05

# --- Full Lebanon bounding box ---
LEBANON_BOUNDS = {
    "south": 33.05,
    "north": 34.69,
    "west": 35.10,
    "east": 36.63,
}

# Grid step in km (smaller = more coverage, more API calls). 4 km covers country within budget.
GRID_STEP_KM = 4.0
# Radius per Nearby Search in metres (overlap slightly so we don't miss places)
SEARCH_RADIUS_M = 5000

# Quality filters (from strategy)
MIN_RATING = 4.2
MIN_REVIEWS = 50

# Popular & active types only (restrict to limit volume)
ALLOWED_TYPES = {
    "restaurant", "cafe", "bar", "meal_delivery", "meal_takeaway",
    "gym", "spa", "beauty_salon", "hair_care", "shopping_mall",
    "store", "supermarket", "bakery", "pharmacy", "gas_station",
    "lodging", "travel_agency", "real_estate_agency", "lawyer",
    "doctor", "dentist", "veterinary_care", "physiotherapist",
    "establishment", "point_of_interest", "food",
}

# Paths
SCRIPT_DIR = Path(__file__).resolve().parent
BILI_ROOT = SCRIPT_DIR.parent
PUBLIC_DIR = BILI_ROOT / "frontend" / "public"
PLACES_JSON = PUBLIC_DIR / "places.json"
PLACE_PHOTOS_DIR = PUBLIC_DIR / "place_photos"


def load_api_key() -> str:
    load_dotenv(BILI_ROOT / ".env")
    key = os.environ.get("GOOGLE_MAPS_API_KEY", "").strip()
    if not key or key == "X":
        raise SystemExit("Set GOOGLE_MAPS_API_KEY in bili/.env (do not commit; do not use on Netlify).")
    return key


def should_skip_photos() -> bool:
    """Set SKIP_PLACE_PHOTOS=1 in .env to avoid 403 on Place Photo (still get all places)."""
    load_dotenv(BILI_ROOT / ".env")
    return os.environ.get("SKIP_PLACE_PHOTOS", "").strip() == "1"


def get_grid_limit() -> int:
    """Max grid points to use (0 = no limit). Set GRID_LIMIT=50 in .env for quick runs."""
    load_dotenv(BILI_ROOT / ".env")
    try:
        return max(0, int(os.environ.get("GRID_LIMIT", "0").strip()))
    except ValueError:
        return 0


def load_existing_place_ids() -> set[str]:
    """Load place_ids from existing places.json so we never re-fetch (no duplicate API calls)."""
    if not PLACES_JSON.exists():
        return set()
    try:
        with open(PLACES_JSON, encoding="utf-8") as f:
            data = json.load(f)
        places = data.get("places", data) if isinstance(data, dict) else data
        return {p.get("place_id") for p in places if p.get("place_id")}
    except Exception:
        return set()


def sanitize_place_id_for_filename(place_id: str) -> str:
    """Safe filename from place_id (no path separators)."""
    return re.sub(r'[/\\:*?"<>|]', "_", place_id)


def in_bounds(lat: float, lng: float, bounds: dict) -> bool:
    """Return True if (lat, lng) is inside the bounding box."""
    return (
        bounds["south"] <= lat <= bounds["north"]
        and bounds["west"] <= lng <= bounds["east"]
    )


def grid_points(bounds: dict, step_km: float) -> list[tuple[float, float]]:
    """Generate (lat, lng) points over the bounding box. ~1 deg lat ≈ 111 km."""
    points: list[tuple[float, float]] = []
    step_deg = step_km / 111.0
    lat = bounds["south"]
    while lat <= bounds["north"]:
        lng = bounds["west"]
        while lng <= bounds["east"]:
            points.append((lat, lng))
            lng += step_deg
        lat += step_deg
    return points


def nearby_search(key: str, lat: float, lng: float, radius_m: int, page_token: str | None = None) -> dict:
    url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    params = {
        "location": f"{lat},{lng}",
        "radius": radius_m,
        "key": key,
    }
    if page_token:
        params["pagetoken"] = page_token
    else:
        params["type"] = "establishment"
    resp = requests.get(url, params=params, timeout=30)
    resp.raise_for_status()
    return resp.json()


def download_photo(key: str, photo_reference: str, save_path: Path, max_width: int = 800) -> bool:
    """Download one Place Photo and save to save_path. Returns True on success."""
    url = "https://maps.googleapis.com/maps/api/place/photo"
    params = {"maxwidth": max_width, "photo_reference": photo_reference, "key": key}
    headers = {"User-Agent": "BILI-Seed/1.0 (Places data)"}
    try:
        resp = requests.get(url, params=params, headers=headers, timeout=15, stream=True)
        resp.raise_for_status()
        save_path.parent.mkdir(parents=True, exist_ok=True)
        with open(save_path, "wb") as f:
            for chunk in resp.iter_content(chunk_size=8192):
                f.write(chunk)
        return True
    except Exception as e:
        print(f"  [WARN] Photo download failed for {save_path.name}: {e}")
        return False


def run(key: str) -> None:
    PUBLIC_DIR.mkdir(parents=True, exist_ok=True)
    PLACE_PHOTOS_DIR.mkdir(parents=True, exist_ok=True)

    # So you can confirm which key is used (last 4 chars only)
    key_suffix = key[-4:] if len(key) >= 4 else "****"
    print(f"Using API key ...{key_suffix} (from bili/.env)")

    skip_photos = should_skip_photos()
    if skip_photos:
        print("SKIP_PLACE_PHOTOS=1: skipping photo downloads (no 403 spam).")

    seen_ids = load_existing_place_ids()
    places: list[dict] = []
    cost_usd = 0.0
    request_count = 0

    def would_exceed(extra_usd: float) -> bool:
        return (cost_usd + extra_usd) > CREDIT_LIMIT_USD

    def add_place(record: dict) -> None:
        places.append(record)
        seen_ids.add(record["place_id"])

    # Load existing places to preserve them (no re-fetch)
    if PLACES_JSON.exists():
        try:
            with open(PLACES_JSON, encoding="utf-8") as f:
                existing = json.load(f)
            places = existing.get("places", existing) if isinstance(existing, dict) else list(existing)
            seen_ids = {p.get("place_id") for p in places if p.get("place_id")}
            print(f"Loaded {len(places)} existing places; will skip these and only add new ones.")
        except Exception as e:
            print(f"Could not load existing places: {e}. Starting fresh.")
            places = []
            seen_ids = set()

    grid = grid_points(LEBANON_BOUNDS, GRID_STEP_KM)
    grid_limit = get_grid_limit()
    if grid_limit > 0:
        grid = grid[:grid_limit]
        print(f"GRID_LIMIT={grid_limit}: using first {len(grid)} grid points.")
    print(f"BILI seed – full Lebanon (grid: {len(grid)} points, step {GRID_STEP_KM} km, radius {SEARCH_RADIUS_M // 1000} km)")
    print(f"Filters: rating >= {MIN_RATING}, reviews >= {MIN_REVIEWS}, popular types only")
    print(f"Budget: hard stop at ${CREDIT_LIMIT_USD}. Request delay: {REQUEST_DELAY_SEC}s")
    print("---")

    for idx, (lat, lng) in enumerate(grid):
        if would_exceed(COST_NEARBY_SEARCH):
            print(f"[STOP] Budget limit reached at grid point {idx + 1}/{len(grid)}. Stopping.")
            break

        time.sleep(REQUEST_DELAY_SEC)
        data = nearby_search(key, lat, lng, SEARCH_RADIUS_M)
        request_count += 1
        cost_usd += COST_NEARBY_SEARCH

        if data.get("status") not in ("OK", "ZERO_RESULTS"):
            err = data.get("error_message", "")
            retry_ok = False  # set True only when first grid retry succeeds
            if idx == 0 and "expired" in (err or "").lower():
                print(f"[Grid 1] API status: {data.get('status')} – {err}")
                print("  Retrying in 90s (key propagation)…")
                time.sleep(90)
                data = nearby_search(key, lat, lng, SEARCH_RADIUS_M)
                request_count += 1
                cost_usd += COST_NEARBY_SEARCH
                if data.get("status") in ("OK", "ZERO_RESULTS"):
                    retry_ok = True
                else:
                    err2 = data.get("error_message", "")
                    print(f"  Still {data.get('status')}: {err2}")
                    print("  In Console: Edit API key → Key expiration → set to 'No expiration' and Save.")
            if not retry_ok:
                if (idx + 1) % 100 == 0 or idx == 0:
                    print(f"[Grid {idx + 1}] API status: {data.get('status')}")
                    if err:
                        print(f"  Google says: {err}")
                continue

        results = data.get("results", [])
        next_page_token = data.get("next_page_token")

        for r in results:
            place_id = r.get("place_id")
            if not place_id or place_id in seen_ids:
                continue
            rating = r.get("rating")
            if rating is None or rating < MIN_RATING:
                continue
            total = r.get("user_ratings_total") or 0
            if total < MIN_REVIEWS:
                continue
            types_list = set(r.get("types") or [])
            if not (types_list & ALLOWED_TYPES):
                continue

            loc = r.get("geometry", {}).get("location", {})
            plat, plng = loc.get("lat"), loc.get("lng")
            if plat is None or plng is None:
                continue
            if not in_bounds(plat, plng, LEBANON_BOUNDS):
                continue

            photos = r.get("photos") or []
            photo_ref = photos[0].get("photo_reference") if photos else None
            photo_path = None

            if photo_ref and not skip_photos:
                if would_exceed(COST_PLACE_PHOTO):
                    print("[STOP] Budget limit reached (photo). Stopping.")
                    break
                time.sleep(REQUEST_DELAY_SEC)
                safe_id = sanitize_place_id_for_filename(place_id)
                photo_file = PLACE_PHOTOS_DIR / f"{safe_id}.jpg"
                if download_photo(key, photo_ref, photo_file):
                    request_count += 1
                    cost_usd += COST_PLACE_PHOTO
                    photo_path = f"/place_photos/{safe_id}.jpg"

            record = {
                "place_id": place_id,
                "name": r.get("name") or "",
                "vicinity": r.get("vicinity") or "",
                "lat": plat,
                "lng": plng,
                "rating": rating,
                "user_ratings_total": total,
                "photo_path": photo_path,
            }
            add_place(record)

        # Pagination for this grid point
        while next_page_token and not would_exceed(COST_NEARBY_SEARCH):
            time.sleep(1.0)
            time.sleep(REQUEST_DELAY_SEC)
            data = nearby_search(key, lat, lng, SEARCH_RADIUS_M, page_token=next_page_token)
            request_count += 1
            cost_usd += COST_NEARBY_SEARCH
            next_page_token = data.get("next_page_token")
            for r in data.get("results", []):
                place_id = r.get("place_id")
                if not place_id or place_id in seen_ids:
                    continue
                if (r.get("rating") or 0) < MIN_RATING or (r.get("user_ratings_total") or 0) < MIN_REVIEWS:
                    continue
                types_list = set(r.get("types") or [])
                if not (types_list & ALLOWED_TYPES):
                    continue
                loc = r.get("geometry", {}).get("location", {})
                plat, plng = loc.get("lat"), loc.get("lng")
                if plat is None or plng is None:
                    continue
                if not in_bounds(plat, plng, LEBANON_BOUNDS):
                    continue
                photos = r.get("photos") or []
                photo_ref = photos[0].get("photo_reference") if photos else None
                photo_path = None
                if photo_ref and not skip_photos and not would_exceed(COST_PLACE_PHOTO):
                    time.sleep(REQUEST_DELAY_SEC)
                    safe_id = sanitize_place_id_for_filename(place_id)
                    photo_file = PLACE_PHOTOS_DIR / f"{safe_id}.jpg"
                    if download_photo(key, photo_ref, photo_file):
                        request_count += 1
                        cost_usd += COST_PLACE_PHOTO
                        photo_path = f"/place_photos/{safe_id}.jpg"
                record = {
                    "place_id": place_id,
                    "name": r.get("name") or "",
                    "vicinity": r.get("vicinity") or "",
                    "lat": plat,
                    "lng": plng,
                    "rating": r.get("rating"),
                    "user_ratings_total": r.get("user_ratings_total") or 0,
                    "photo_path": photo_path,
                }
                add_place(record)

        if (idx + 1) % 50 == 0 or idx == 0 or (idx + 1) == len(grid):
            print(f"[Grid {idx + 1}/{len(grid)}] Places: {len(places)} | Requests: {request_count} | Est. ${cost_usd:.2f}")
        if would_exceed(0):
            print("[STOP] Budget limit reached.")
            break

    payload = {
        "meta": {
            "total_places": len(places),
            "estimated_cost_usd": round(cost_usd, 2),
            "credit_limit_usd": CREDIT_LIMIT_USD,
            "request_count": request_count,
        },
        "places": places,
    }

    with open(PLACES_JSON, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    print("---")
    print(f"Done. Total places: {len(places)} | Requests: {request_count} | Est. cost: ${cost_usd:.2f}")
    print(f"Output: {PLACES_JSON}")
    print(f"Photos: {PLACE_PHOTOS_DIR}")


if __name__ == "__main__":
    run(load_api_key())
