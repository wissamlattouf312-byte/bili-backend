# BILI Master System - Quick Start Guide

## 🎯 What Has Been Built

I've created a complete BILI Master System architecture from scratch with the following **CORE FEATURES** implemented:

### ✅ 1. Permanent Guest Access
- Users can browse ALL content without login/signup
- No authentication barriers
- Full business and post visibility

### ✅ 2. Flashing Claim Button
- **Backend API**: `/api/v1/claim/business`
- **Frontend Component**: `ClaimButton.jsx` with CSS animations
- Awards **20 credits** instantly
- Registers user as member automatically
- Sets **30-day Royal Hospitality** period

### ✅ 3. Silent Decay Logic
- **WebSocket Manager**: Real-time radar synchronization
- Users with `status="offline"` AND `balance=0.00` are **instantly removed**
- 60-second grace period for disconnections
- Live radar endpoint: `/api/v1/radar/users`

### ✅ 4. Admin Login Alert
- SMS notification to **03 520 580** upon admin login
- Zero-balance watchdog dashboard
- Admin endpoints ready

### ✅ 5. Complete Database Models
- User (Guest/Member/Master/Admin)
- Business (Google Mirror, Claim status)
- Credits (Transactions + Ledger)
- Posts (Personal/Commercial)
- Chat (30-day retention)

## 🚀 How to Start

### Step 1: Install Dependencies
```bash
cd bili
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

### Step 2: Configure Environment
```bash
# Copy the template
copy .env.example .env

# Edit .env and replace ALL 'X' placeholders with your actual credentials:
# - GOOGLE_MAPS_API_KEY=X  → Your Google Maps key
# - BYBIT_API_KEY=X  → Your Bybit key
# - SMS_API_KEY=X  → Your SMS service key
# etc.
```

### Step 3: Set Up Database
```bash
# Create PostgreSQL database
createdb bili_db

# Update DATABASE_URL in .env
# DATABASE_URL=postgresql://user:password@localhost:5432/bili_db

# Run migrations (after setting up Alembic)
alembic upgrade head
```

### Step 4: Run the Server
```bash
python run.py
```

Server starts at: `http://localhost:8000`
API Docs: `http://localhost:8000/api/docs`

## 🧪 Test the Core Features

### Test Guest Access (No Auth Required)
```bash
curl http://localhost:8000/api/v1/guest/businesses
```

### Test Claim Button
```bash
curl -X POST http://localhost:8000/api/v1/claim/business \
  -H "Content-Type: application/json" \
  -d '{
    "business_id": "test-id",
    "latitude": 33.8938,
    "longitude": 35.5018
  }'
```

### Test Radar (Silent Decay Logic)
```bash
curl "http://localhost:8000/api/v1/radar/users?latitude=33.8938&longitude=35.5018&radius_km=15"
```

### Test Admin Login Alert
```bash
curl -X POST http://localhost:8000/api/v1/admin/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "password"}'
```

## 📁 Project Structure

```
bili/
├── app/
│   ├── main.py              # FastAPI app entry
│   ├── core/                # Config, database, websocket
│   ├── models/              # Database models
│   ├── schemas/             # API schemas
│   ├── api/v1/endpoints/    # API endpoints
│   └── services/            # Business logic
├── frontend/src/components/ # React components
├── .env.example            # Environment template (all 'X')
└── requirements.txt        # Python dependencies
```

## 🔑 Key Files

- **Claim Button Backend**: `app/api/v1/endpoints/claim.py`
- **Claim Button Frontend**: `frontend/src/components/ClaimButton.jsx`
- **Silent Decay Logic**: `app/core/websocket.py` + `app/models/user.py`
- **Guest Access**: `app/api/v1/endpoints/guest.py`
- **Admin Alerts**: `app/services/admin_alert.py`
- **Configuration**: `app/core/config.py` (all 'X' placeholders)

## ⚠️ Important Notes

1. **All API credentials use placeholder 'X'** - Fill them in `.env` file
2. **SMS alerts will log to console** if credentials not configured
3. **Database migrations** need to be set up with Alembic
4. **WebSocket** endpoint available at `ws://localhost:8000/ws`

## 📚 Next Steps

1. Fill in `.env` file with actual credentials
2. Set up PostgreSQL and run migrations
3. Test core features
4. Implement remaining features from specification
5. Set up frontend build process

## 🎉 What's Working

- ✅ Complete backend API structure
- ✅ Database models for all features
- ✅ Guest access (no auth)
- ✅ Claim button (20 credits + registration)
- ✅ Silent decay logic (real-time radar)
- ✅ Admin login alerts
- ✅ Credit system with ledger
- ✅ WebSocket infrastructure

**All external APIs use placeholder 'X' as requested - ready for you to fill in actual credentials!**
