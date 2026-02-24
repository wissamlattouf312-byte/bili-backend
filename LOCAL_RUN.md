# Run BILI on your laptop

## Quick start (one click)

1. Double-click **`start-bili-local.bat`** (in the `bili` folder).
2. Two terminal windows will open (backend + frontend). Wait until the frontend window shows "Compiled successfully!" (about 15–20 seconds).
3. Your browser should open automatically. If it doesn’t, open this link yourself:

   **http://localhost:3000**

   If that doesn’t work, try: **http://127.0.0.1:3000**

---

## Manual start (two terminals)

**Terminal 1 – Backend**
```bash
cd "c:\Users\User\Desktop\jona 2\bili"
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```
Leave this running. Backend will be at http://localhost:8000

**Terminal 2 – Frontend**
```bash
cd "c:\Users\User\Desktop\jona 2\bili\frontend"
npm start
```
Wait for "Compiled successfully!". Then open in your browser:

**http://localhost:3000**

---

## If the link doesn’t work

- **"This site can’t be reached" / "Connection refused"**  
  The app isn’t running yet. Start it with `start-bili-local.bat` or the manual steps above and wait until the frontend compiles.

- **Blank page**  
  Wait a bit longer for the first compile, then refresh (F5). Check the frontend terminal for errors.

- **localhost doesn’t open**  
  Try **http://127.0.0.1:3000** instead.

- **Port 3000 already in use**  
  The frontend will offer another port (e.g. 3001). Use the URL shown in that terminal, e.g. http://localhost:3001

- **"Network error" or "Cannot reach server" on Admin login (or map not loading)**  
  The **backend** is not running or not reachable. Start it in a separate terminal:
  ```bash
  cd "c:\Users\User\Desktop\jona 2\bili"
  python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
  ```
  Keep that window open. The frontend at http://localhost:3000 talks to the API at http://localhost:8000.

---

## Deployed (online) link

If you’ve deployed to Netlify, the live app is usually at:

**https://shiny-choux-bddd03.netlify.app/**

(Only use this if you’ve run `seed-then-deploy.bat` or deployed the frontend to Netlify.)
