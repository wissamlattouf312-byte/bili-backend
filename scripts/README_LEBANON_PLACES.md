# Lebanon places fetcher (Google Maps) – Active Opportunities only

**DEPRECATED:** The app now uses **Maps JavaScript API** for the map and static **places.json** for pins; **Places API is not used**. This script is kept for reference only.

---

Fetches places from Google Maps in **Lebanon only** (no Dubai or other countries), with a **$200** hard credit limit.

## Strict filter: Active Opportunities only

The script **only fetches and keeps places that signal active offers, discounts, or promotions**. The BILI map is populated exclusively with these “Active Opportunities.” Any business without such a signal is **skipped entirely**.

- **How we filter:** The public Places API does **not** expose “Live Deal” or “Special Offer” data from Google Business profiles. We apply a **keyword-based heuristic** on each place’s **name** and **vicinity** (address snippet): if either contains words like *offer*, *discount*, *promo*, *deal*, *sale*, *special*, *coupon*, *happy hour*, or Arabic equivalents (عرض, خصم, تخفيض, etc.), the place is kept. We also require **business_status = OPERATIONAL** when present, and **at least one photo**.
- **Implication:** Results are “places that advertise offers in their listing text,” not “places with a verified Live Deal on Google.” For true offer/deal data you would need another source (e.g. business partnerships or a different API).

## What the script does

- Uses **Places API (Legacy)** Nearby Search over a grid of points inside Lebanon’s bounding box.
- Keeps only places that pass the **Active Opportunities** filter (offer/promo keywords in name or vicinity, OPERATIONAL, with at least one photo).
- Tracks estimated cost and **stops before exceeding $200**.
- Writes one JSON file with `meta.filter: "active_opportunities_only"` and `places[]` with `place_id`, `name`, `vicinity`, `lat`, `lng`, `rating`, `types`, `photo_references`, `photo_urls`, and `active_opportunity: true`.

## Setup

1. **API key**  
   In the project root `.env` (or environment), set:
   ```bash
   GOOGLE_MAPS_API_KEY=your_google_maps_api_key
   ```
   Enable **Places API** (and optionally **Places API (New)**) in Google Cloud Console for the same project.

2. **Run from repo root** (so `.env` and `scripts/` are in path):
   ```bash
   cd c:\Users\User\Desktop\jona 2\bili
   python scripts/fetch_lebanon_places.py
   ```
   Or from anywhere:
   ```bash
   python "c:\Users\User\Desktop\jona 2\bili\scripts\fetch_lebanon_places.py"
   ```
   (Ensure the project root has `.env` or that `GOOGLE_MAPS_API_KEY` is set in the environment.)

## Output

- **Directory:** `bili/scripts/output/`
- **File:** `lebanon_places_YYYYMMDD_HHMMSS.json`
- **Contents:** `meta` (total_places, estimated_cost_usd, credit_limit_usd, …) and `places[]` with `place_id`, `name`, `vicinity`, `lat`, `lng`, `rating`, `types`, `photo_references`, `photo_urls` (with `YOUR_API_KEY` placeholder).

## Cost (within $200)

- Only **Nearby Search** is used; no Place Details or Place Photo requests.
- Approximate: **$32 per 1,000** search requests. To stay under $200, the script stops when the estimated cost would exceed $200.
- Grid and pagination are tuned so that reaching 10,000 places with photos should stay well under the limit; if the limit is hit first, the run stops and saves what was collected.

## Notes

- **Lebanon only:** All results are filtered by the Lebanon bounding box; Dubai and other countries are ignored.
- **Active Opportunities only:** Places without offer/promo/deal/sale (or Arabic equivalent) in name or vicinity are skipped; the map is intended to show only active opportunities.
- **API limitation:** “Live Deal” and “Special Offer” from Google Business profiles are **not** available in the public Places API; our filter is a best-effort heuristic.
- **Visual content:** Kept places must have at least one photo in the Nearby Search response.
- To **display or download photos**, use the saved `photo_urls` after replacing `YOUR_API_KEY` with your key; each request counts as a Place Photo call (~$7/1000).
