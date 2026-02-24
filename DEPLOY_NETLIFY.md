# Deploy BILI frontend to Netlify (test on iPhone, Samsung, etc.)

To test on real devices (iPhone, Samsung), you need **both**:

1. **Backend** deployed online (e.g. [Render](https://render.com)) so the API is reachable from the internet.
2. **Frontend** on Netlify, with `REACT_APP_API_URL` set to that backend URL.

**Single guide:** **[CONNECTING_BACKEND_FRONTEND.md](./CONNECTING_BACKEND_FRONTEND.md)** walks through creating and connecting both.  
Otherwise: deploy backend first ([DEPLOY_BACKEND.md](./DEPLOY_BACKEND.md)), then frontend below.

---

## 1. Build the frontend

From the project root (e.g. `c:\Users\User\Desktop\jona 2\bili`):

```bash
cd frontend
npm install
npm run build
```

This creates the `frontend/build` folder that Netlify will serve.

---

## 2. Deploy to Netlify

### Option A — Netlify CLI (quick from your machine)

1. Install Netlify CLI once (if you don’t have it):
   ```bash
   npm install -g netlify-cli
   ```

2. Log in (opens browser):
   ```bash
   netlify login
   ```

3. From the **frontend** folder, deploy the existing build:
   ```bash
   cd frontend
   netlify deploy --prod --dir=build
   ```
   - First time: choose “Create & configure a new site”, pick your team, and give the site a name (e.g. `bili-app`).
   - Next times: it will use the same site and just update the live URL.

4. Netlify will print the live URL (e.g. `https://bili-app.netlify.app`). Open it on your iPhone or Samsung to test.

### Option B — Netlify website (drag & drop)

1. Build locally (step 1 above).
2. Go to [https://app.netlify.com](https://app.netlify.com) → **Sites** → **Add new site** → **Deploy manually**.
3. Drag the **`frontend/build`** folder into the drop zone.
4. Netlify will give you a URL. Use that on your devices.

### Option C — Git (auto deploy on push)

1. Push your repo to GitHub/GitLab/Bitbucket.
2. In Netlify: **Add new site** → **Import an existing project** → connect the repo.
3. Set:
   - **Base directory:** `frontend`
   - **Build command:** `npm run build`
   - **Publish directory:** `frontend/build` (or `build` if base directory is already `frontend`).
4. Add env vars (see step 3 below), then deploy.

---

## 3. Backend URL for phones (important)

On your phone, the app will call `REACT_APP_API_URL`. If that is `http://127.0.0.1:8000`, the phone cannot reach your PC.

- **Recommended — Deploy backend to the cloud**  
  Follow **[DEPLOY_BACKEND.md](./DEPLOY_BACKEND.md)** (e.g. Render). Then in Netlify set **REACT_APP_API_URL** to your backend URL (e.g. `https://bili-api.onrender.com`) and redeploy the frontend. All changes (pins, login, etc.) are then tested against the same online backend on every device.

- **Quick test only — Tunnel from your PC**  
  Run the backend locally, then run **ngrok**: `ngrok http 8000`. Use the ngrok HTTPS URL as **REACT_APP_API_URL** in Netlify and redeploy. Your phone can hit that URL while your PC is on; not suitable for persistent testing.

---

## 4. Set env vars in Netlify (for Option A or C)

In Netlify: **Site settings** → **Environment variables**:

| Variable | Value |
|----------|--------|
| `REACT_APP_API_URL` | Your **public** backend URL (e.g. `https://your-api.onrender.com` or ngrok URL) |
| `REACT_APP_GOOGLE_MAPS_API_KEY` | Same key as in `frontend/.env` (optional if you already baked it into the build) |

Then trigger a new deploy (e.g. **Deploys** → **Trigger deploy** → **Deploy site**) so the new build uses these values.

---

## Quick recap

- **Backend:** Deploy first (see [DEPLOY_BACKEND.md](./DEPLOY_BACKEND.md)); set `CORS_ORIGINS` to your Netlify URL.
- **Frontend:** Build (`cd frontend` → `npm run build`), then deploy (`netlify deploy --prod --dir=build` or drag `frontend/build`).
- **Phones:** In Netlify set `REACT_APP_API_URL` to your backend URL, redeploy, then open the Netlify URL on iPhone/Samsung. All changes are tested against the online backend.
