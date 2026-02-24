# 🚀 Manual Server Start Instructions
[cite: 2026-02-09]

## Step-by-Step Manual Launch

### Terminal 1 - Backend Server:
```powershell
cd "c:\Users\User\Desktop\jona 2\bili"
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

**Expected Output:**
- `INFO:     Uvicorn running on http://127.0.0.1:8000`
- `INFO:     Application startup complete.`

---

### Terminal 2 - Frontend Server:
```powershell
cd "c:\Users\User\Desktop\jona 2\bili\frontend"
npm start
```

**Expected Output:**
- `Compiled successfully!`
- `webpack compiled with X warnings`
- `Local: http://localhost:3000`

---

### Step 3 - Open Chrome:
**ONLY after Terminal 2 shows "Compiled successfully"**, manually:
1. Open Chrome browser
2. Navigate to: `http://localhost:3000`

---

## ✅ What You Should See:

### For Guest Users:
- **Claim Button**: Prominently displayed with text **"20 حبة"**
- **Welcome Message**: "Welcome to BILI!"
- **Guest Info**: "Click the Claim button above to get started and earn 20 Habbet credits."

### Claim Button Features:
- ✅ Text: **"20 حبة"** (Arabic)
- ✅ Prominent, flashing style
- ✅ Available at any time
- ✅ Awards 20 Habbet credits
- ✅ Converts Guest → Active Member

---

## 🔧 Configuration Verified:

- ✅ **Guest Mode**: Default entry point (`isGuest: true`)
- ✅ **Claim Button**: Displays "20 حبة"
- ✅ **No Breakpoints**: Clean code, no debugger statements
- ✅ **Backend**: Port 8000 (FastAPI/Uvicorn)
- ✅ **Frontend**: Port 3000 (React/Webpack)

---

## 📝 Notes:

- Keep both terminals open while using the app
- Backend runs with `--reload` (auto-restarts on code changes)
- Frontend runs with hot-reload (auto-refreshes browser)
- Guest mode is active by default - no login required
- Claim button is always visible for guest users

---

**Status**: ✅ Ready for manual start!
