# Creating and connecting backend + frontend (Netlify + Render)

One path to get the app online so you can test on iPhone/Samsung with one backend and one frontend.

---

## Step 1 — Deploy the backend (Render)

1. **Push the `bili` project to GitHub**  
   (Create a repo; push the folder that contains `app/`, `requirements.txt`, `render.yaml`.)

2. **Render**  
   - Go to [render.com](https://render.com) and sign in (e.g. with GitHub).  
   - **New** → **Blueprint** (or **Web Service** if you prefer manual setup).  
   - Connect the repo. If the repo root is the `bili` folder, leave **Root Directory** blank. If the repo is the parent and `bili` is a subfolder, set **Root Directory** to `bili`.  
   - If you use **Blueprint**: Render will read `render.yaml` and create the service. You still need to set **CORS_ORIGINS** in the dashboard (see below).  
   - If you use **Web Service** (no Blueprint): set **Build Command** to `pip install -r requirements.txt`, **Start Command** to `uvicorn app.main:app --host 0.0.0.0 --port $PORT`, and add the env vars from the table below.

3. **Environment variables** (Render → your service → **Environment**)

   | Key | Value |
   |-----|--------|
   | `DATABASE_URL` | `sqlite:///./bili.db` (simple; data can reset on redeploy) or a Postgres URL from Render |
   | `CORS_ORIGINS` | **Your Netlify URL** (e.g. `https://your-app.netlify.app`) — no trailing slash. Add after you have the frontend URL. |
   | `JWT_SECRET_KEY` | Long random string (generate and paste) |
   | `APP_DEBUG` | `false` |

   Optional: `GOOGLE_MAPS_API_KEY`, `SMS_API_KEY`, `SMS_API_URL`, `ADMIN_PHONE_NUMBER` (if you use them).

4. **Deploy**  
   Let Render build and deploy. Copy the service URL (e.g. `https://bili-api.onrender.com`).  
   - **Health check:** `https://bili-api.onrender.com/api/v1/health` should return OK.

---

## Step 2 — Deploy the frontend (Netlify)

1. **Build**
   ```bash
   cd bili/frontend
   npm install
   npm run build
   ```

2. **Deploy**
   - **Option A — Netlify CLI:**  
     `npm install -g netlify-cli`, then `netlify login`, then from `frontend`: `netlify deploy --prod --dir=build`.  
   - **Option B — Drag & drop:**  
     [app.netlify.com](https://app.netlify.com) → **Add new site** → **Deploy manually** → drag the `frontend/build` folder.  
   - **Option C — Git:**  
     Connect the repo, set **Base directory** to `frontend`, **Build command** to `npm run build`, **Publish directory** to `build`.

3. **Copy your Netlify URL**  
   (e.g. `https://bili-app.netlify.app`.)

---

## Step 3 — Connect them

1. **Backend (Render)**  
   - Open your Render service → **Environment**.  
   - Set **CORS_ORIGINS** = your Netlify URL, e.g. `https://bili-app.netlify.app` (no trailing slash).  
   - Save. Render will redeploy if needed.

2. **Frontend (Netlify)**  
   - Open your Netlify site → **Site settings** → **Environment variables**.  
   - Add:
     - **REACT_APP_API_URL** = your Render backend URL (e.g. `https://bili-api.onrender.com`), no trailing slash.
     - **REACT_APP_GOOGLE_MAPS_API_KEY** = your Maps key (if you use the map).
   - **Trigger a new deploy** (e.g. **Deploys** → **Trigger deploy** → **Deploy site**) so the new build uses these values.

3. **Test**  
   - Open the Netlify URL in a browser; try Map, Store, Admin login.  
   - Open the same URL on your iPhone or Samsung. All requests go to the same online backend, so any changes (pins, etc.) are shared across devices.

---

## Checklist

| Done | Step |
|------|------|
| ☐ | Backend deployed on Render; health URL returns OK |
| ☐ | Frontend deployed on Netlify; site loads |
| ☐ | Render: `CORS_ORIGINS` = Netlify URL |
| ☐ | Netlify: `REACT_APP_API_URL` = Render URL; new deploy run |
| ☐ | Test in browser and on phone |

---

## Files added for this

- **`bili/render.yaml`** — Render Blueprint for the backend (optional; you can configure the Web Service manually instead).
- **`bili/frontend/.env.production.example`** — Example env vars for Netlify; copy the keys and set values in the Netlify UI.
- **WebSocket:** The frontend derives the WebSocket URL from `REACT_APP_API_URL` (https → wss), so you don’t need to set `REACT_APP_WS_URL` unless you use a different host for WS.

More detail: [DEPLOY_BACKEND.md](./DEPLOY_BACKEND.md), [DEPLOY_NETLIFY.md](./DEPLOY_NETLIFY.md).
