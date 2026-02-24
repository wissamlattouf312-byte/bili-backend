# BILI — Next steps & unused files

## Next steps (from project docs)

### From BILI_NEXT_STEPS.md

| # | Area | Status | Next action |
|---|------|--------|-------------|
| 1 | Royal Hospitality (30 days) | Done (DB, claim, withdrawal block) | Optional: block any other credit deduction during grace period if new features add deductions |
| 2 | Viral Gateway & Referrals | Done (ref link, 5 Habbet, Profile section) | — |
| 3 | **Smart Advertising** | Post model done | Add notification system (12h cooldown), radius-based visibility |
| 4 | **Video & media** | Post model supports video | Add video compression, BILI watermark, thumbnails, WhatsApp preview |

### From IMPLEMENTATION_STATUS.md (still open)

- **Smart Advertising:** notification system (12-hour cooldown), radius-based visibility  
- **Video:** compression, BILI watermark, thumbnail generation, WhatsApp preview  
- **Elite Vault / Master:** CV upload endpoint, master verification, proximity follow alerts  
- **Admin:** analytics dashboard (full), $50 auto-sweep to Bybit, feature toggles  
- **Governance:** invisible mode, block-list, search/filter, AI content filter, offline caching  
- **Legal / chat:** auto-deletion job, terms, copyright, age gate, account deletion  
- **WhatsApp acquisition:** multi-device gateway, scheduler, human-pulse algorithm  

**Suggested order to tackle next**

1. **ROBO_Radar content** — Replace placeholder with a simple radar/list view (even demo data).  
2. **Smart Advertising** — Notifications + radius-based visibility.  
3. **Video / media** — Watermark, thumbnails (when you have real posts).

---

## Files not in use right now

### Frontend (not imported in App or index)

| File | Purpose | Note |
|------|--------|------|
| `frontend/src/components/UserDashboard.jsx` | Wallet/balance/withdrawal from API | App uses **WalletPanel** (demo/localStorage) instead. Use this when you connect a real wallet API. |
| `frontend/src/components/UserDashboard.css` | Styles for UserDashboard | Same as above. |
| `frontend/src/components/LocationRadar.jsx` | Location-based radar, API + WebSocket | App uses a simple ROBO_Radar placeholder. Use when you add real radar/location. |
| `frontend/src/components/LocationRadar.css` | Styles for LocationRadar | Same as above. |
| `frontend/src/ErrorBoundary.jsx` | React error boundary | Not wrapped in `index.js`. Optional: wrap `<App />` with it to catch UI errors. |

**Summary:**  
- **UserDashboard** = full wallet/API version; **WalletPanel** = current demo.  
- **LocationRadar** = full radar; **ROBO_Radar** tab = placeholder.  
- **ErrorBoundary** = optional safety; not required for current flow.

You can keep these files for when you add backend/radar; or remove them if you want a leaner repo (and reintroduce later from git history if needed).

---

## Backend

Backend endpoints and models are used when the app calls the API (e.g. with ngrok). The frontend currently works in “demo” mode without them. No backend files are listed as unused; they are just not called until you connect the app to the backend.
