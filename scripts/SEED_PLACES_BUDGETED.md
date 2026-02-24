# BILI Seed Places (Budgeted) – Google Maps Data Strategy

**DEPRECATED:** The app now uses **Maps JavaScript API** for the map and static **places.json** for pins; **Places API is no longer used**. This script is kept for reference or one-off re-seeds only. Do not run it in deploy pipelines. See project README for current setup.

---

This script implemented the **BILI Google Maps Data Strategy** (Places API): official API only, **full Lebanon** (grid over the country bounding box), quality filters, one photo per place, **hard budget cap at $200**, and no re-fetching of existing places.

## API key: local/backend only (never Netlify)

- **Where to set the key:** In `bili/.env` (project root), set:
  ```bash
  GOOGLE_MAPS_API_KEY=your_actual_key_here
  ```
- **Do not commit `.env`** (it should be in `.gitignore`). Do not put this key in Netlify environment variables or in any frontend code.
- **Netlify** serves only the **static export**: `frontend/public/places.json` and `frontend/public/place_photos/`. The React app loads that JSON; no Google API key is used in the browser.

## What the script does

- **Coverage:** Full Lebanon via a grid of Nearby Search points over the country bounding box (south 33.05, north 34.69, west 35.10, east 36.63). Grid step 4 km; radius 5 km per search so the whole country is covered.
- **Filters:** Rating ≥ 4.2, reviews ≥ 50, popular categories only (restaurant, cafe, gym, store, etc.).
- **Data per place:** `place_id`, `name`, `vicinity`, `lat`, `lng`, `rating`, `user_ratings_total`, one photo (downloaded and saved under `frontend/public/place_photos/`).
- **Budget:** Internal request counter; **automatic stop when estimated cost would exceed $200**. Set a **billing alert at $180** in Google Cloud Console.
- **No re-fetching:** If `frontend/public/places.json` already exists, its `place_id`s are loaded and skipped; only new places are requested from the API.

## How to run

1. Ensure `GOOGLE_MAPS_API_KEY` is set in `bili/.env`.
2. From the **bili** project root:
   ```bash
   python scripts/seed_places_budgeted.py
   ```
   Or from anywhere (with `bili` as current dir for `.env`):
   ```bash
   cd path/to/bili
   python scripts/seed_places_budgeted.py
   ```
3. Output is written to:
   - `frontend/public/places.json` (array of places + meta)
   - `frontend/public/place_photos/<place_id>.jpg` (one image per place)

## After running

- Commit **only** `frontend/public/places.json` and `frontend/public/place_photos/` (do not commit `.env`).
- Deploy the frontend to Netlify as usual (`npm run build` in `frontend/`). The build includes `public/`, so `places.json` and `place_photos/` are deployed and the app will load them with no API key.

## Google Cloud

- Enable **Places API** (and **Place Photos** if needed) for your project.
- Set a **billing alert at $180** so you are warned before hitting the $200 cap.
- Restrict the API key (e.g. by IP if you only run the script from one machine) if desired; do not use the key in the frontend.
