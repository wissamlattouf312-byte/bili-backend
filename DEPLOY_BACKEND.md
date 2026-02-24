# Deploy BILI backend online (so phones can use the API)

You need the **backend** deployed somewhere public so that when you open the Netlify frontend on iPhone or Samsung, the app can load pins, login, map data, etc. Below is one way using **Render** (free tier).

**Quick path:** See **[CONNECTING_BACKEND_FRONTEND.md](./CONNECTING_BACKEND_FRONTEND.md)** for a single step-by-step that creates and connects both backend and frontend.

---

## Option: Render (free tier)

A **`render.yaml`** Blueprint is in this repo so Render can create the service from the repo. You can use **Blueprint** (New → Blueprint, connect repo, set Root Directory if needed) or **Web Service** (manual).

1. **Push your code to GitHub**  
   (If you use Git only locally, create a repo on GitHub and push the `bili` project.)

2. **Go to [Render](https://render.com)** → Sign in (e.g. with GitHub).

3. **New → Blueprint** (or **Web Service**)  
   - Connect the repo that contains the BILI backend (the folder with `app/`, `requirements.txt`, `render.yaml`).  
   - If the backend is inside a subfolder (e.g. `bili`), set **Root Directory** to that folder.  
   - With **Blueprint**, Render uses `render.yaml`; you still must set **CORS_ORIGINS** in the service Environment after deploy.

4. **Configure the service**
   - **Name:** e.g. `bili-api`
   - **Region:** pick one close to you
   - **Runtime:** Python 3
   - **Build Command:**
     ```bash
     pip install -r requirements.txt
     ```
   - **Start Command:**
     ```bash
     uvicorn app.main:app --host 0.0.0.0 --port $PORT
     ```
   - **Instance type:** Free (spins down after ~15 min inactivity; first request may be slow)

5. **Environment variables** (in Render dashboard → your service → Environment)

   Add at least:

   | Key | Value |
   |-----|--------|
   | `DATABASE_URL` | `sqlite:///./bili.db` (simple; data is lost on redeploy) **or** a Postgres URL if you add a Render Postgres DB |
   | `CORS_ORIGINS` | Your Netlify URL, e.g. `https://your-site.netlify.app` (no trailing slash) |
   | `JWT_SECRET_KEY` | A long random string (e.g. generate one and paste it) |
   | `APP_DEBUG` | `false` |

   Optional (same as in your local `.env` if you use them):

   - `GOOGLE_MAPS_API_KEY`
   - `SMS_API_KEY`, `SMS_API_URL`, `ADMIN_PHONE_NUMBER` (for admin login SMS)

   **Note:** On the free tier with SQLite, the database file is on the server’s disk; it may be reset on redeploy. For persistent data (pins, admin user), add a **Postgres** database in Render and set `DATABASE_URL` to the URL Render gives you (e.g. `postgresql://user:pass@host/dbname`).

6. **Deploy**  
   Click **Create Web Service**. Render will build and run the backend and give you a URL like `https://bili-api.onrender.com`.

7. **Use this URL as the API in the frontend**
   - In **Netlify** → your site → **Environment variables**, set:
     - `REACT_APP_API_URL` = `https://bili-api.onrender.com` (your Render URL, no trailing slash)
   - Redeploy the frontend on Netlify so the new build uses this URL.

Now when you open the Netlify app on your phone, it will call the Render backend and all changes (pins, login, etc.) are tested against the online backend.

---

## CORS

The backend allows requests from origins listed in `CORS_ORIGINS`. You set `CORS_ORIGINS` on Render to your Netlify URL (e.g. `https://your-app.netlify.app`). If you use multiple frontend URLs (e.g. preview deploys), add them comma-separated:  
`https://your-app.netlify.app,https://deploy-preview-123--your-app.netlify.app`

---

## Quick recap

1. Deploy backend on Render (or similar), get `https://your-api.onrender.com`.
2. Set backend env: `CORS_ORIGINS=https://your-site.netlify.app`, `DATABASE_URL`, `JWT_SECRET_KEY`, etc.
3. Set Netlify env: `REACT_APP_API_URL=https://your-api.onrender.com`.
4. Redeploy frontend on Netlify. Test on iPhone/Samsung; both use the same online backend.
