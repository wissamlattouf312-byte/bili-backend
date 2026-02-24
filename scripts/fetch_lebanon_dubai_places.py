#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

"""
DEPRECATED: App now uses Maps JavaScript API + static places.json; Places API not used.
Kept for reference only. Do not run in deploy pipelines.

Step 1: Fetch up to 10,000 places from Google Maps API (Lebanon & Dubai).
Includes only places that have visual content (at least one photo).
Hard credit limit: $200 (free tier).

Note: The public Places API does not return business "posts"; only place data
and photo references. Posts would require another data source.

Requires: GOOGLE_MAPS_API_KEY in .env or environment.
Output: scripts/output/lebanon_dubai_places_YYYYMMDD_HHMMSS.json
"""

import json
import os
import time
from pathlib import Path
from urllib.parse import urlencode

import requests
from dotenv import load_dotenv

TARGET_PLACES = 10_000
CREDIT_LIMIT_USD = 200.0

# Lebanon bounding box
LEBANON_BOUNDS = {
    "south": 33.05,
    "north": 34.69,
    "west": 35.10,
    "east": 36.63,
}

# Dubai / UAE (Dubai area) bounding box
DUBAI_BOUNDS = {
    "south": 24.95,
    "north": 25.35,
    "west": 55.10,
    "east": 55.55,
}

COST_NEARBY_SEARCH_PER_1K = 32.0
REQUEST_DELAY_SEC = 0.05
OUTPUT_DIR = Path(__file__).resolve().parent / "output"


def load_api_key():
    load_dotenv(Path(__file__).resolve().parent.parent / ".env")
    key = os.environ.get("GOOGLE_MAPS_API_KEY", "").strip()
    if not key:
        raise SystemExit("Set GOOGLE_MAPS_API_KEY in .env (or environment).")
    return key


def in_bounds(lat: float, lng: float, bounds: dict) -> bool:
    return (
        bounds["south"] <= lat <= bounds["north"]
        and bounds["west"] <= lng <= bounds["east"]
    )


def grid_points(bounds: dict, step_km: float = 4.0) -> list[tuple[float, float, str]]:
    """Generate (lat, lng, region) points for Nearby Search. ~1 deg lat ≈ 111 km."""
    points = []
    step_deg = step_km / 111.0
    lat = bounds["south"]
    while lat <= bounds["north"]:
        lng = bounds["west"]
        while lng <= bounds["east"]:
            points.append((lat, lng, bounds.get("region", "unknown")))
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
        params["type"] = "establishment"
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
    out_file = OUTPUT_DIR / f"lebanon_dubai_places_{time.strftime('%Y%m%d_%H%M%S')}.json"

    LEBANON_BOUNDS["region"] = "Lebanon"
    DUBAI_BOUNDS["region"] = "Dubai"
    all_points = (
        [(lat, lng, "Lebanon") for lat, lng, _ in grid_points(LEBANON_BOUNDS)]
        + [(lat, lng, "Dubai") for lat, lng, _ in grid_points(DUBAI_BOUNDS)]
    )

    seen_ids = set()
    places = []
    cost_usd = 0.0
    search_requests = 0
    photo_count = 0
    bounds_by_region = {"Lebanon": LEBANON_BOUNDS, "Dubai": DUBAI_BOUNDS}

    def would_exceed(extra_usd: float) -> bool:
        return (cost_usd + extra_usd) > CREDIT_LIMIT_USD

    print("Regions: Lebanon, Dubai")
    print(f"Grid points: {len(all_points)}")
    print(f"Filter: visual content only (at least one photo)")
    print(f"Target: {TARGET_PLACES} places | Limit: ${CREDIT_LIMIT_USD}")
    print("---")

    for idx, (lat, lng, region) in enumerate(all_points):
        if len(places) >= TARGET_PLACES:
            break
        if would_exceed(COST_NEARBY_SEARCH_PER_1K / 1000):
            print("Credit limit reached. Stopping.")
            break

        data = nearby_search(key, lat, lng)
        time.sleep(REQUEST_DELAY_SEC)
        search_requests += 1
        cost_usd += COST_NEARBY_SEARCH_PER_1K / 1000

        if data.get("status") not in ("OK", "ZERO_RESULTS"):
            continue

        results = data.get("results", [])
        next_page_token = data.get("next_page_token")

        for r in results:
            if len(places) >= TARGET_PLACES:
                break
            place_id = r.get("place_id")
            if not place_id or place_id in seen_ids:
                continue
            photos = r.get("photos") or []
            if not photos:
                continue
            loc = r.get("geometry", {}).get("location", {})
            plat, plng = loc.get("lat"), loc.get("lng")
            if plat is None or plng is None:
                continue
            b = bounds_by_region.get(region, LEBANON_BOUNDS)
            if not in_bounds(plat, plng, b):
                continue
            seen_ids.add(place_id)
            refs = [p.get("photo_reference") for p in photos[:5] if p.get("photo_reference")]
            place_record = {
                "place_id": place_id,
                "name": r.get("name"),
                "vicinity": r.get("vicinity"),
                "lat": plat,
                "lng": plng,
                "region": region,
                "rating": r.get("rating"),
                "user_ratings_total": r.get("user_ratings_total"),
                "types": r.get("types", []),
                "photo_references": refs,
                "photo_urls": [build_photo_url(key, ref) for ref in refs[:3]],
            }
            places.append(place_record)
            photo_count += len(place_record["photo_urls"])

        while next_page_token and len(places) < TARGET_PLACES:
            if would_exceed(COST_NEARBY_SEARCH_PER_1K / 1000):
                break
            time.sleep(1.0)
            data = nearby_search(key, lat, lng, page_token=next_page_token)
            time.sleep(REQUEST_DELAY_SEC)
            search_requests += 1
            cost_usd += COST_NEARBY_SEARCH_PER_1K / 1000
            next_page_token = data.get("next_page_token")
            for r in data.get("results", []):
                if len(places) >= TARGET_PLACES:
                    break
                place_id = r.get("place_id")
                if not place_id or place_id in seen_ids:
                    continue
                photos = r.get("photos") or []
                if not photos:
                    continue
                loc = r.get("geometry", {}).get("location", {})
                plat, plng = loc.get("lat"), loc.get("lng")
                if plat is None or plng is None:
                    continue
                b = bounds_by_region.get(region, LEBANON_BOUNDS)
                if not in_bounds(plat, plng, b):
                    continue
                seen_ids.add(place_id)
                refs = [p.get("photo_reference") for p in photos[:5] if p.get("photo_reference")]
                place_record = {
                    "place_id": place_id,
                    "name": r.get("name"),
                    "vicinity": r.get("vicinity"),
                    "lat": plat,
                    "lng": plng,
                    "region": region,
                    "rating": r.get("rating"),
                    "user_ratings_total": r.get("user_ratings_total"),
                    "types": r.get("types", []),
                    "photo_references": refs,
                    "photo_urls": [build_photo_url(key, ref) for ref in refs[:3]],
                }
                places.append(place_record)
                photo_count += len(place_record["photo_urls"])

        if (idx + 1) % 30 == 0 or (len(places) > 0 and len(places) % 500 == 0):
            print(f"Places: {len(places)} | Requests: {search_requests} | Est. cost: ${cost_usd:.2f}")

    for p in places:
        p["photo_urls"] = [u.replace(key, "YOUR_API_KEY") for u in p["photo_urls"]]

    payload = {
        "meta": {
            "regions": ["Lebanon", "Dubai"],
            "filter": "visual_content_only",
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
    run(load_api_key())
