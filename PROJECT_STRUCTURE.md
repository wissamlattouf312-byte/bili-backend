# BILI Master System - Project Structure

## 📁 Directory Structure

```
bili/
├── app/                          # Main application package
│   ├── __init__.py
│   ├── main.py                   # FastAPI application entry point
│   ├── core/                     # Core configuration and utilities
│   │   ├── config.py            # Settings with placeholder 'X' for credentials
│   │   ├── database.py          # Database configuration
│   │   └── websocket.py         # WebSocket manager (Silent Decay Logic)
│   ├── models/                   # SQLAlchemy database models
│   │   ├── __init__.py
│   │   ├── user.py              # User model (Guest/Member/Master/Admin)
│   │   ├── business.py          # Business model (Google Mirror)
│   │   ├── credit.py            # Credit system models
│   │   ├── post.py              # Post model (Personal/Commercial)
│   │   └── chat.py              # Chat models (30-day retention)
│   ├── schemas/                  # Pydantic schemas for API
│   │   ├── claim.py
│   │   ├── business.py
│   │   ├── post.py
│   │   ├── radar.py
│   │   └── credits.py
│   ├── api/                      # API routes
│   │   └── v1/
│   │       ├── router.py        # Main API router
│   │       └── endpoints/
│   │           ├── guest.py      # Guest access (no auth)
│   │           ├── claim.py      # Claim button endpoint
│   │           ├── radar.py      # Live radar (Silent Decay)
│   │           ├── admin.py      # Admin endpoints
│   │           └── credits.py    # Credit ledger
│   └── services/                 # Business logic services
│       ├── sms.py               # SMS service (placeholder 'X')
│       └── admin_alert.py       # Admin login alerts
├── frontend/                     # React frontend
│   └── src/
│       └── components/
│           ├── ClaimButton.jsx  # Flashing claim button
│           └── ClaimButton.css
├── .env.example                 # Environment template (all 'X' placeholders)
├── requirements.txt             # Python dependencies
├── alembic.ini                  # Database migration config
├── run.py                       # Development server runner
└── README.md                    # Project documentation
```

## 🔑 Key Features Implemented

### ✅ 1. Permanent Guest Access
- **Location**: `app/api/v1/endpoints/guest.py`
- Users can browse businesses and posts without login/signup
- No authentication barriers for initial browsing

### ✅ 2. Flashing Claim Button
- **Backend**: `app/api/v1/endpoints/claim.py`
- **Frontend**: `frontend/src/components/ClaimButton.jsx`
- Awards 20 credits instantly
- Registers user as member
- Sets 30-day Royal Hospitality period

### ✅ 3. Silent Decay Logic
- **Location**: `app/core/websocket.py`, `app/models/user.py`
- Users with status="offline" AND balance=0.00 are removed from radar
- Real-time WebSocket synchronization
- 60-second grace period for disconnections

### ✅ 4. Admin Login Alert
- **Location**: `app/services/admin_alert.py`
- Sends SMS to 03 520 580 upon admin login
- Uses placeholder 'X' for SMS API credentials

## 🔐 Configuration

All external API credentials use placeholder 'X' and must be configured in `.env`:

- `GOOGLE_MAPS_API_KEY=X`
- `BYBIT_API_KEY=X`
- `BYBIT_API_SECRET=X`
- `WHATSAPP_API_KEY=X`
- `SMS_API_KEY=X`
- `FIREBASE_PROJECT_ID=X`

Fill these values in `.env` file before deployment.

## 🚀 Next Steps

1. Set up PostgreSQL database
2. Run migrations: `alembic upgrade head`
3. Configure `.env` file with actual credentials
4. Start backend: `python run.py`
5. Implement remaining features from specification
