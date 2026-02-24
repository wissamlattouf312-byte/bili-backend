# Deploy BILI – Frontend + Backend (you run these)

I can’t access your Netlify/Render/Heroku accounts, so **you** need to run the deploy steps below. Everything is prepared so it’s as quick as possible.

---

## Frontend (already built)

The production build is ready at:

**`bili/frontend/build`**

### Option A: Netlify (drag & drop)

1. Go to [https://app.netlify.com](https://app.netlify.com) and log in.
2. Drag the **`frontend/build`** folder onto the “Deploy manually” zone.
3. After deploy, set **Environment variables** (Site settings → Environment variables):
   - **Key:** `REACT_APP_API_URL`  
   - **Value:** `https://YOUR-BACKEND-URL` (your live API URL, no trailing slash).
4. Trigger a **new deploy** (Deploys → Trigger deploy) so the new variable is used.

### Option B: Netlify (Git repo)

1. Push your code to GitHub/GitLab.
2. In Netlify: Add new site → Import from Git → choose repo.
3. **Build settings:**  
   - Base directory: `frontend`  
   - Build command: `npm run build`  
   - Publish directory: `frontend/build`  
   (Or leave default if the repo root is `frontend`.)
4. Add env var **`REACT_APP_API_URL`** = your live backend URL.
5. Deploy.

---

## Backend (FastAPI)

Use one of: **Render**, **Railway**, **Heroku**, or a VPS.

### 1. Prepare

- **Procfile** and **runtime.txt** are in the project root (`bili/`).
- Backend root for deploy = folder that contains `app/`, `requirements.txt`, `Procfile` (i.e. **`bili`**).

### 2. Render.com

1. [https://dashboard.render.com](https://dashboard.render.com) → New → Web Service.
2. Connect your repo (or upload).
3. **Root directory:** `bili` (or leave blank if repo root is `bili`).
4. **Build:** `pip install -r requirements.txt`
5. **Start:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
6. **Environment:** Add `DATABASE_URL`, `CORS_ORIGINS` = your Netlify frontend URL (e.g. `https://your-site.netlify.app`), and other vars from `.env.example`.
7. Deploy. Copy the service URL (e.g. `https://bili-xxx.onrender.com`).

### 3. Railway

1. [https://railway.app](https://railway.app) → New project → Deploy from GitHub (or upload).
2. Set root to the backend folder (`bili`).
3. Add **Postgres** in the same project if you use DB; Railway sets `DATABASE_URL`.
4. Variables: `CORS_ORIGINS` = your frontend URL, plus any others from `.env.example`.
5. Deploy and copy the generated URL.

### 4. Heroku

```bash
cd c:\Users\User\Desktop\jona 2\bili
heroku create bili-api
heroku config:set CORS_ORIGINS=https://your-netlify-site.netlify.app
heroku config:set DATABASE_URL=postgres://...
git subtree push --prefix bili heroku main
```

(Adjust `--prefix` if your repo layout differs.)

---

## After both are live

1. **Frontend:** Set (or update) **`REACT_APP_API_URL`** to the backend URL and redeploy.
2. **Backend:** Set **`CORS_ORIGINS`** to the frontend URL (e.g. `https://your-app.netlify.app`).
3. Open the frontend URL → Map tab and other features should work with the live API.

---

## Quick recap

| What            | Where / action |
|-----------------|----------------|
| Frontend build  | Already at `bili/frontend/build`; deploy that folder (or connect repo). |
| Frontend config | Env var `REACT_APP_API_URL` = backend URL, then redeploy. |
| Backend         | Deploy `bili` (Procfile + requirements.txt) to Render/Railway/Heroku. |
| Backend config  | `CORS_ORIGINS` = frontend URL; `DATABASE_URL` and rest from `.env.example`. |

If you tell me which host you use (e.g. Netlify + Render), I can give you the exact clicks and commands for that combo.
