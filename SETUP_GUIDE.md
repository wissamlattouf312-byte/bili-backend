# BILI Master System - Setup Guide

## Prerequisites

- Python 3.9+
- PostgreSQL 12+
- Node.js 16+ (for frontend)
- npm or yarn

## Installation Steps

### 1. Backend Setup

```bash
# Navigate to project directory
cd bili

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy environment template
copy .env.example .env
# Linux/Mac: cp .env.example .env

# Edit .env file and replace all 'X' placeholders with actual credentials
```

### 2. Database Setup

```bash
# Create PostgreSQL database
createdb bili_db

# Update DATABASE_URL in .env file
# DATABASE_URL=postgresql://user:password@localhost:5432/bili_db

# Initialize Alembic migrations
alembic init alembic

# Create initial migration
alembic revision --autogenerate -m "Initial migration"

# Apply migrations
alembic upgrade head
```

### 3. Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm start
```

### 4. Run Backend Server

```bash
# From project root
python run.py

# Server will start on http://localhost:8000
# API docs available at http://localhost:8000/api/docs
```

## Environment Variables

Edit `.env` file and replace all `X` placeholders:

```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/bili_db

# Google Maps API (optional; deprecated seed scripts only)
GOOGLE_MAPS_API_KEY=YOUR_GOOGLE_MAPS_KEY

# Frontend: Maps JavaScript API key (required for map display). Set in frontend/.env:
# REACT_APP_GOOGLE_MAPS_API_KEY=YOUR_MAPS_JS_KEY
# Restrict this key to Maps JavaScript API and HTTP referrers (localhost, your Netlify domain) in Google Cloud Console.

# Bybit Wallet
BYBIT_API_KEY=YOUR_BYBIT_KEY
BYBIT_API_SECRET=YOUR_BYBIT_SECRET
BYBIT_WALLET_ADDRESS=YOUR_WALLET_ADDRESS

# WhatsApp Gateway
WHATSAPP_API_KEY=YOUR_WHATSAPP_KEY
WHATSAPP_API_URL=YOUR_WHATSAPP_URL

# SMS Service (for admin alerts)
SMS_API_KEY=YOUR_SMS_KEY
SMS_API_URL=YOUR_SMS_URL
ADMIN_PHONE_NUMBER=03520580

# JWT Secret
JWT_SECRET_KEY=YOUR_SECRET_KEY

# Other settings...
```

## Testing Core Features

### 1. Test Guest Access
```bash
curl http://localhost:8000/api/v1/guest/businesses
```

### 2. Test Claim Button
```bash
curl -X POST http://localhost:8000/api/v1/claim/business \
  -H "Content-Type: application/json" \
  -d '{"business_id": "test-business-id", "latitude": 33.8938, "longitude": 35.5018}'
```

### 3. Test Radar (Silent Decay Logic)
```bash
curl http://localhost:8000/api/v1/radar/users?latitude=33.8938&longitude=35.5018&radius_km=15
```

### 4. Test Admin Login Alert
```bash
curl -X POST http://localhost:8000/api/v1/admin/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "password"}'
```

## Development Notes

- All external API credentials use placeholder 'X' by default
- SMS alerts will log to console if credentials are not configured
- WebSocket connections available at `ws://localhost:8000/ws`
- Database models support all core features from specification

## Troubleshooting

1. **Database connection error**: Check DATABASE_URL in .env
2. **Migration errors**: Run `alembic upgrade head`
3. **Import errors**: Ensure virtual environment is activated
4. **Port already in use**: Change port in `run.py` or kill existing process
