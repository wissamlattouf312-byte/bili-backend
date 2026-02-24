# Admin Login – Add pins manually

## 1. Start backend and frontend

**Option A – One click**  
Double‑click **`start-bili-local.bat`** in the `bili` folder.

**Option B – Two terminals**

- **Backend** (leave this window open):
  ```bash
  cd "c:\Users\User\Desktop\jona 2\bili"
  python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
  ```
  Wait until you see: **`Application startup complete.`**

- **Frontend**:
  ```bash
  cd "c:\Users\User\Desktop\jona 2\bili\frontend"
  npm start
  ```
  Wait until you see: **`Compiled successfully!`**

## 2. Create the admin user (only once)

The project uses **SQLite** by default (`bili.db` in the bili folder), so you don’t need PostgreSQL. Tables are created on backend startup.

From the **bili** folder run once:

```bash
python scripts/create_admin_user.py
```

You should see: **`Admin user created.`**

Or in the app: open **Admin** tab → click **“Create default admin user”** → then log in.

## 3. Final Admin credentials

| Field       | Value                |
|------------|----------------------|
| **Username** | `admin@bili.local` or `03520580` |
| **Password** | `admin123`           |

## 4. Log in and add pins

1. Open **http://localhost:3000** (or http://127.0.0.1:3000).
2. Go to the **Admin** tab.
3. Log in with the username and password above.
4. Use **“Map pins (store locations)”** to add pins (paste coordinates or a Google Maps URL, optional name and profile URL).

---

- Backend must show **Application startup complete**.
- Frontend must show **Compiled successfully** and **Backend connected** on the Admin page.
- To use **PostgreSQL** instead of SQLite, set in `bili/.env`:  
  `DATABASE_URL=postgresql://user:password@localhost:5432/bili_db`  
  and run: `alembic upgrade head` from the bili folder before starting the backend.
