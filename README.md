# BILI Master System (2026)

A comprehensive geolocation-based social platform with real-time radar, business claiming, credit system, and viral content sharing.

## 🏗️ Architecture

- **Backend**: FastAPI (Python) with WebSocket support
- **Frontend**: React with TypeScript
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Real-time**: WebSockets for live radar updates
- **Maps**: Google Maps JavaScript API + Directions API (no Places API); store pins are manual (Admin) or static/backend
- **Payments**: Bybit Wallet integration (USDT TRC20)
- **Messaging**: WhatsApp Gateway integration

## 🚀 Quick Start

1. Install dependencies: `pip install -r requirements.txt`
2. Copy `.env.example` to `.env` and fill in your credentials (marked with 'X')
3. Set up PostgreSQL database
4. Run migrations: `alembic upgrade head`
5. Start backend: `uvicorn app.main:app --reload`
6. Start frontend: `cd frontend && npm install && npm start`

## 📋 Core Features

- ✅ Permanent Guest Access (no login barriers)
- ✅ Flashing Claim Button (20 credits reward)
- ✅ Silent Decay Logic (remove offline zero-balance users)
- ✅ 30-Day Royal Hospitality (free service period)
- ✅ Real-time Radar with WebSocket synchronization
- ✅ Credit System with ledger tracking
- ✅ Video Sharing with auto-compression and watermark
- ✅ Admin Dashboard with analytics

## 🔐 Security

All external API credentials are stored in `.env` file with placeholder 'X' values.
Fill these values before deployment.

## 📍 Map and store locations

- **Map**: The frontend uses **Google Maps JavaScript API** for the base map and **Directions API** for in-app walking routes. Set `REACT_APP_GOOGLE_MAPS_API_KEY` in `frontend/.env`. Restrict the key to **Maps JavaScript API** and **Directions API** (and HTTP referrers) in Google Cloud Console. **No Google Places API** is used.
- **Store pins**: Location data is **manual only**. In the **Admin** tab, log in and paste coordinates or a Google Maps URL to add a pin; it appears on the map for all users. Pins also come from static `frontend/public/places.json` and from your backend (VIP businesses, flash deals). When a user clicks a store pin, the walking route opens on the map so they stay inside the app.
