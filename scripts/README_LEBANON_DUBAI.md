# Step 1: Fetch 10,000 places (Lebanon & Dubai)

Script: **`fetch_lebanon_dubai_places.py`**

- Fetches from **Lebanon** and **Dubai** bounding boxes.
- Keeps only places with **visual content** (at least one photo).
- **$200** hard credit limit (Nearby Search only).
- **Note:** The public Places API does not return business “posts”; only place data and photo references.

## Run

```bash
cd c:\Users\User\Desktop\jona 2\bili
python scripts/fetch_lebanon_dubai_places.py
```

Output: `scripts/output/lebanon_dubai_places_YYYYMMDD_HHMMSS.json`

## Use in app

Load that JSON in the Map tab (or via an API) to show places on the map. BILI-registered (VIP) businesses from the database always appear on top with a VIP icon and override any duplicate by `google_place_id`.
