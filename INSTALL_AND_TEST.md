# BILI Master System - Installation & Testing Guide

## ✅ All Files Are Saved and Ready!

All 40+ files have been created and saved in: `c:\Users\User\Desktop\jona 2\bili\`

## 🚀 Quick Start to Test Radar

### Step 1: Install Dependencies
```bash
cd "c:\Users\User\Desktop\jona 2\bili"
pip install -r requirements.txt
```

### Step 2: Set Up Database (PostgreSQL)
```bash
# Create database
createdb bili_db

# Update .env file with your database credentials
# DATABASE_URL=postgresql://user:password@localhost:5432/bili_db
```

### Step 3: Run Database Migrations
```bash
# Initialize Alembic (if not done)
alembic init alembic

# Create initial migration
alembic revision --autogenerate -m "Initial migration"

# Apply migrations
alembic upgrade head
```

### Step 4: Start the Server
```bash
python run.py
```

Server will start at: **http://localhost:8000**

### Step 5: Test Radar Endpoint

#### Option A: Use the Test Script
```bash
python test_radar.py
```

#### Option B: Use Browser/Postman
1. Open: **http://localhost:8000/api/docs**
2. Navigate to: **GET /api/v1/radar/users**
3. Click "Try it out"
4. Enter coordinates (optional):
   - latitude: 33.8938
   - longitude: 35.5018
   - radius_km: 15
5. Click "Execute"

#### Option C: Use curl
```bash
# Get all radar users
curl http://localhost:8000/api/v1/radar/users

# Get radar users with location filter
curl "http://localhost:8000/api/v1/radar/users?latitude=33.8938&longitude=35.5018&radius_km=15"

# Get radar statistics
curl http://localhost:8000/api/v1/radar/stats
```

## 🧪 Testing Silent Decay Logic

The Radar endpoint implements **Silent Decay Logic** [cite: 2026-01-30]:
- ✅ Only shows users with `status="online"` OR (`status="offline"` AND `balance > 0.00`)
- ✅ Users with `status="offline"` AND `balance=0.00` are **instantly removed**

### Test Scenarios:

1. **Create a user with 0 credits and set offline** → Should NOT appear on radar
2. **Create a user with credits and set offline** → SHOULD appear on radar
3. **Create a user online** → SHOULD appear on radar

## 📋 Key Endpoints to Test

### Radar Endpoints:
- `GET /api/v1/radar/users` - Get users on radar (Silent Decay applied)
- `POST /api/v1/radar/update-status` - Update user status (triggers Silent Decay)
- `POST /api/v1/radar/update-location` - Update user location
- `GET /api/v1/radar/stats` - Get radar statistics
- `POST /api/v1/radar/silent-decay-check` - Manual Silent Decay check

### Other Endpoints:
- `GET /api/v1/guest/businesses` - Browse businesses (no auth)
- `POST /api/v1/claim/business` - Claim business (awards 20 credits)
- `POST /api/v1/admin/login` - Admin login (sends SMS to 03 520 580)
- `GET /api/v1/admin/zero-balance-watchdog` - Monitor zero-balance users

## 🔍 Verify Files Are Complete

Check these critical files exist:
- ✅ `app/api/v1/endpoints/radar.py` - Silent Decay Logic
- ✅ `app/api/v1/endpoints/admin.py` - Admin alerts
- ✅ `app/api/v1/endpoints/claim.py` - 20 credits reward
- ✅ `app/core/websocket.py` - WebSocket manager
- ✅ `app/core/background_tasks.py` - Background monitoring
- ✅ `.env` - Configuration (all 'X' placeholders)

## ⚠️ Troubleshooting

### Server won't start:
- Check if port 8000 is available
- Verify all dependencies installed: `pip install -r requirements.txt`
- Check database connection in `.env`

### Import errors:
- Make sure you're running from the `bili` directory
- Verify Python path includes the project root
- Check all `__init__.py` files exist

### Database errors:
- Ensure PostgreSQL is running
- Verify DATABASE_URL in `.env` is correct
- Run migrations: `alembic upgrade head`

## ✅ All Files Are Ready!

All files have been created and saved. You can now:
1. Install dependencies
2. Set up database
3. Start server
4. Test Radar endpoint!

**The Silent Decay Logic is fully implemented and ready to test!** 🎉
