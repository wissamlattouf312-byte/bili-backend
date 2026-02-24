# BILI Master System — Full Spec (11 Sections + Appendix A)

This document is the **single reference** for what the full BILI app was specified to include. It is derived from your project’s implementation status, checklists, and onboarding docs.

---

## Section 1 — Guest Access & Onboarding

- **Permanent Guest Access**: Users can enter the app without login/signup; full browsing and visibility for guests.
- **Tabs**: ROBO_Radar, Store (محل), Profile.
- **Flashing Claim**: Prominent “Claim” (e.g. 20 Habbet) available at any time; no business required for general claim.
- **Conversion**: Guest → Active Member on claim; 20 Habbet credited; 30-day Royal Hospitality period set.
- **Config**: Reward amount and related values editable in one place (e.g. `appConfig.js`), not scattered in component code.

**Status**: ✅ Implemented (guest, claim, tabs, config, referral link in Profile).

---

## Section 2 — Credit System & Ledger

- **Credits (Habbet)**: Award on claim; balance shown in UI (top counter + Profile).
- **Ledger**: Clear history of credit movements (additions/deductions).
- **Royal Hospitality**: 30-day period; no withdrawal/sweep during this period (backend block).
- **Send-to-zero**: Optional control to “spend” or reset the welcome reward balance back to 0 for demo/testing.

**Status**: ✅ Implemented (balance, ledger demo, withdrawal block, top-counter send-to-zero).

---

## Section 3 — Viral Gateway & Referrals

- **Auto-entry links**: Shareable links with `?ref=CODE`; no login required to open.
- **Referral tracking**: Who referred whom (e.g. `referral_code`, `referred_by_id`).
- **Referrer reward**: 5 Habbet to referrer when a new user claims (backend + frontend).
- **Profile**: Show “Your referral link” and Copy; message when no code yet.

**Status**: ✅ Implemented (ref in URL, claim sends ref, 5 Habbet to referrer, Profile section).

---

## Section 4 — ROBO_Radar & Location

- **Radar view**: First tab; nearby / activity list (demo or API-driven).
- **Silent Decay**: Users with 0 credits and offline removed from radar; WebSocket/backend support.
- **Real radar (optional)**: Location-based visibility; reuse or wire `LocationRadar` when backend is ready.

**Status**: ✅ Radar list + placeholder + claim in tab; ✅ Backend Silent Decay; ⏳ Real location/API when needed.

---

## Section 5 — Store (محل)

- **Store feed**: List of businesses/offers (demo or API).
- **Guest visibility**: Store content visible without login.

**Status**: ✅ Demo store list; ⏳ Connect to real API when ready.

---

## Section 6 — Smart Advertising

- **Post types**: Commercial vs personal; 48-hour expiration logic (model/backend).
- **Notifications**: In-app or browser notifications with cooldown (e.g. 12 hours).
- **Radius-based visibility**: Show offers/ads only to users “near” a location.

**Status**: ✅ Post model; ⏳ Notification system; ⏳ Radius visibility.

---

## Section 7 — Video & Media

- **Video support**: Post model supports video.
- **BILI watermark**: Overlay on video content.
- **Thumbnails**: Generate for video posts.
- **WhatsApp preview**: Optimize sharing preview.

**Status**: ✅ Model support; ⏳ Compression, watermark, thumbnails, WhatsApp preview.

---

## Section 8 — Elite Vault & Mastery (CV System)

- **Master fields**: User model has master/CV fields.
- **CV upload**: Endpoint for CV/portfolio upload.
- **Master verification**: Workflow for verifying masters.
- **Proximity follow**: Alerts when masters are nearby (or similar).

**Status**: ✅ User model; ⏳ CV upload, verification, proximity alerts.

---

## Section 9 — Administration

- **Admin alerts**: SMS to 03 520 580 on admin login (and related events).
- **Zero-balance watchdog**: Dashboard/alert for users at 0 balance.
- **Analytics dashboard**: Full implementation of admin analytics.
- **$50 auto-sweep**: Automatic transfer to Bybit when balance threshold reached.
- **Feature toggles**: e.g. store compliance on/off.

**Status**: ✅ Admin alert + watchdog structure; ⏳ Full analytics; ⏳ Bybit sweep; ⏳ Toggles.

---

## Section 10 — Governance & Safety

- **Credit ledger**: Full history (implemented).
- **Invisible mode**: User toggle to hide from radar/visibility.
- **Block-list**: Block users or content.
- **Search/filter**: Advanced search and filtering.
- **AI content filtering**: Optional automated content checks.
- **Offline caching**: Cache for offline or poor connectivity.

**Status**: ✅ Ledger; ⏳ Invisible, block-list, search, AI filter, offline cache.

---

## Section 11 — Legal, Chat & Account Lifecycle

- **Chat retention**: 30-day retention policy (model).
- **Auto-deletion job**: Remove chat data after retention period.
- **Terms & disclaimers**: In-app terms and legal text.
- **Copyright checks**: Process or policy for copyright.
- **Age gate**: +18 or similar restrictions where required.
- **Account deletion**: User-initiated account deletion workflow.

**Status**: ✅ Model; ⏳ Deletion job, terms, copyright, age gate, deletion flow.

---

## Appendix A — Configuration & Deployment

- **API keys**: All external APIs use placeholder `X` until real keys are set (Google Maps, Bybit, WhatsApp, SMS, Firebase, JWT).
- **Environment**: `.env` / `app/core/config.py`; frontend `appConfig.js` for reward amounts and tunables.
- **Database**: PostgreSQL; migrations (e.g. Alembic); run when DB is enabled.
- **Deployment**: Frontend build → Netlify (or similar); backend optional (uvicorn + ngrok for API from phone).
- **Testing**: Guest access, claim flow, ledger, referral, Profile link; then backend/radar when connected.

**Status**: ✅ Placeholders and config pattern; ✅ Build + Netlify; ⏳ Fill real keys and DB when ready.

---

## Summary Table

| Section | Name                         | Done | Pending / optional                    |
|--------|------------------------------|------|---------------------------------------|
| 1      | Guest Access & Onboarding   | ✅   | —                                     |
| 2      | Credit System & Ledger      | ✅   | —                                     |
| 3      | Viral Gateway & Referrals   | ✅   | —                                     |
| 4      | ROBO_Radar & Location       | ✅   | Real location/API                     |
| 5      | Store                       | ✅   | Real API                              |
| 6      | Smart Advertising           | ⏳   | Notifications, radius                 |
| 7      | Video & Media               | ⏳   | Watermark, thumbnails, WhatsApp       |
| 8      | Elite Vault & Mastery       | ⏳   | CV upload, verification, proximity    |
| 9      | Administration              | ⏳   | Analytics, Bybit sweep, toggles      |
| 10     | Governance & Safety         | ⏳   | Invisible, block-list, search, cache  |
| 11     | Legal, Chat & Lifecycle     | ⏳   | Deletion job, terms, age gate         |
| App. A | Configuration & Deployment  | ✅   | Real keys, DB, full backend when ready|

---

Use this file as the **canonical “what was requested”** for the full BILI Master System. Next steps can be chosen by picking a section and working through its ⏳ items.
