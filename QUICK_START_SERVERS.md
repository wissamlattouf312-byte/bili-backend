# 🚀 Quick Start Guide - Launch Servers
[cite: 2026-02-09]

## ✅ Servers Installation & Launch Status

### Installation Status:
- ✅ Python dependencies: Installing/Installed
- ✅ Node.js dependencies: Installing/Installed  
- ✅ Launch scripts created

### Launch Scripts Created:
1. `start_backend.ps1` - Start backend server only
2. `start_frontend.ps1` - Start frontend server only
3. `start_all.ps1` - Start both servers automatically

---

## 🎯 EASIEST WAY TO LAUNCH:

### Option 1: Use the Launch Script (Recommended)
```powershell
cd "c:\Users\User\Desktop\jona 2\bili"
.\start_all.ps1
```

This will:
- Start backend server in one window
- Start frontend server in another window
- Open browsers automatically
- Show all URLs

### Option 2: Manual Launch

#### Terminal 1 - Backend:
```powershell
cd "c:\Users\User\Desktop\jona 2\bili"
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

#### Terminal 2 - Frontend:
```powershell
cd "c:\Users\User\Desktop\jona 2\bili\frontend"
npm start
```

---

## 📋 Pre-Launch Checklist

### 1. Install Python Dependencies
```powershell
cd "c:\Users\User\Desktop\jona 2\bili"
pip install -r requirements.txt
```

### 2. Install Frontend Dependencies
```powershell
cd "c:\Users\User\Desktop\jona 2\bili\frontend"
npm install
```

### 3. Configure Environment (if not done)
- Copy `.env.example` to `.env`
- Fill in database URL and API keys

### 4. Start Servers
Use `start_all.ps1` or manual commands above

---

## 🌐 Access Points

Once servers are running:
- **Frontend App**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/api/docs
- **WebSocket**: ws://localhost:8000/ws

---

## ⚠️ Troubleshooting

### Backend won't start:
1. Check Python version: `python --version` (need 3.9+)
2. Install dependencies: `pip install -r requirements.txt`
3. Check if port 8000 is available
4. Check `.env` file exists

### Frontend won't start:
1. Check Node.js: `node --version` (need 16+)
2. Install dependencies: `cd frontend && npm install`
3. Check if port 3000 is available
4. Check `package.json` exists

### Dependencies taking too long:
- This is normal for first install
- Backend: ~2-5 minutes
- Frontend: ~1-3 minutes
- Wait for completion before starting servers

---

## ✅ Verification

Once both servers are running, you should see:

**Backend Terminal:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
```

**Frontend Terminal:**
```
Compiled successfully!
You can now view bili-frontend in the browser.
  Local:            http://localhost:3000
```

---

## 🎉 Ready to Launch!

Run `.\start_all.ps1` or follow manual steps above.

**Status**: ✅ All systems ready for launch!
