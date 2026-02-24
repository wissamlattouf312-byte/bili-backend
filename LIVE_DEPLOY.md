# BILI – Live deployment checklist

Use this so the **live** (production) frontend and backend work together, including the Map tab, VIP businesses, and Flash Deals.

---

## 1. Backend (API)

### 1.1 Environment (.env on the server)

- Set **production** values for at least:
  - `DATABASE_URL` – production Postgres
  - `APP_DEBUG=false`
  - `APP_ENV=production`
- **CORS:** set your **live frontend URL** so the browser can call the API:
  ```env
  CORS_ORIGINS=https://your-app.netlify.app
  ```
  Use a comma-separated list if you have several (e.g. custom domain + Netlify).

### 1.2 Database tables

- Run migrations so `flash_deals` and other tables exist:
  ```bash
  cd c:\Users\User\Desktop\jona 2\bili
  alembic upgrade head
  ```
- If you use `Base.metadata.create_all()` on startup (e.g. in `main.py`), the `flash_deals` table is also created when the app starts, as long as the `FlashDeal` model is imported.

### 1.3 Deploy the backend

- Deploy the FastAPI app (e.g. Heroku, Railway, Render, your VPS).
- Note the **live API base URL** (e.g. `https://bili-api.herokuapp.com`).

---

## 2. Frontend (React app)

### 2.1 Environment for **production build**

- Create a **production** env file or set env vars **at build time** (e.g. in Netlify “Build environment variables”):
  ```env
  REACT_APP_API_URL=https://your-bili-api.herokuapp.com
  ```
  Use your real backend URL, **no trailing slash**.

- So:
  - **Development:** `npm start` can keep using `proxy` in `package.json` (e.g. `http://localhost:8000`); `REACT_APP_API_URL` can be empty.
  - **Production:** set `REACT_APP_API_URL` to the live API URL and **rebuild** the frontend so it’s baked into the build.

### 2.2 Build and deploy

```bash
cd c:\Users\User\Desktop\jona 2\bili\frontend
npm install
npm run build
```

- Deploy the contents of the **`build`** folder (e.g. drag-and-drop to Netlify, or connect the repo and set build command to `npm run build` and publish directory to `build`).
- Ensure the same `REACT_APP_API_URL` is set in the build environment of your host (Netlify, Vercel, etc.).

---

## 3. After deploy

- Open the **live frontend** URL.
- **Map tab:** should load; VIP businesses and Flash Deals come from the live API if `REACT_APP_API_URL` points to it.
- If the map or feed don’t load:
  - Check browser Network tab: requests should go to `REACT_APP_API_URL` (e.g. `…/api/v1/map/vip-businesses`, `…/api/v1/flash-deals/active`).
  - Check backend CORS: response headers must allow your frontend origin (the one in `CORS_ORIGINS`).
  - Check backend logs for 4xx/5xx on those routes.

---

## 4. Optional: Places data (Lebanon + Dubai)

- Run the fetch script when you want to refresh map places (e.g. from your machine or a cron job):
  ```bash
  cd c:\Users\User\Desktop\jona 2\bili
  python scripts/fetch_lebanon_dubai_places.py
  ```
- Use the generated JSON (e.g. from a static URL or a small API) and, if you add that to the frontend, the map can show those places. The Map tab works without this (demo places only) until you wire that in.

---

## Quick checklist

| Step | Action |
|------|--------|
| Backend .env | `CORS_ORIGINS=https://your-live-frontend-url` |
| Backend .env | `APP_DEBUG=false`, `DATABASE_URL` = production DB |
| DB | `alembic upgrade head` (or rely on `create_all` + model import) |
| Frontend build env | `REACT_APP_API_URL=https://your-live-api-url` |
| Frontend | `npm run build` and deploy `build` folder |

Once these are done, the live version has all changes (Map, VIP, Flash Deals, CORS, API URL) implemented for production.
