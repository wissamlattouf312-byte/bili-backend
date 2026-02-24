# 🚀 BILI Master System - Launch Guide
[cite: 2026-02-09]

## ✅ SINGLE RUN BUTTON CREATED

### To Launch the App:

**Simply double-click:** `RUN.bat`

This will:
1. ✅ Clean up any existing processes
2. ✅ Check Python and Node.js
3. ✅ Start Backend Server (http://localhost:8000)
4. ✅ Start Frontend Server (http://localhost:3000)
5. ✅ Open browser automatically

---

## 📋 What Happens:

1. **Backend Server** opens in a new window
   - URL: http://localhost:8000
   - API Docs: http://localhost:8000/api/docs

2. **Frontend Server** opens in a new window
   - URL: http://localhost:3000
   - React development server

3. **Browser** opens automatically to:
   - http://localhost:3000 (Main App)
   - http://localhost:8000/api/docs (API Documentation)

---

## ⚠️ First Time Setup:

If this is your first run, you may need to:

1. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Install Frontend dependencies:**
   ```bash
   cd frontend
   npm install
   ```

3. **Configure .env file:**
   - Copy `.env.example` to `.env`
   - Fill in database URL and API keys

---

## 🎯 Quick Access:

- **Frontend App**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/api/docs
- **WebSocket**: ws://localhost:8000/ws

---

## 🛑 To Stop Servers:

Close the two server windows (Backend and Frontend), or press `Ctrl+C` in each window.

---

**Status**: ✅ Ready to launch with single `RUN.bat` file!
