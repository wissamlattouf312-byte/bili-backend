# BILI App - User Authentication and Onboarding System

## Overview

Complete implementation of the User Authentication and Onboarding system for the BILI App, based on exact specifications [cite: 2026-02-09].

## ✅ Implemented Features

### 1. Permanent Guest Access [cite: 2026-02-03]

**Implementation**: `app/auth_handler.py` - `get_or_create_guest_user()`

- Users can enter the app as permanent guests
- No login/signup barriers for initial access
- Full content visibility and interaction allowed
- Guest sessions tracked via device_id or phone_number
- Guest endpoints in `app/api/v1/endpoints/guest.py`:
  - `/api/v1/guest/businesses` - Browse all businesses
  - `/api/v1/guest/businesses/{business_id}` - View business details
  - `/api/v1/guest/posts` - Browse all posts
  - `/api/v1/guest/posts/{post_id}` - View post details

**Key Features**:
- Guests can observe all content
- Guests can interact freely (browse, view, search)
- No authentication required for guest endpoints
- Seamless transition to member status via Claim button

### 2. Reward System - Flashing Claim Button [cite: 2026-02-03]

**Implementation**: `app/api/v1/endpoints/claim.py` - `/api/v1/claim/reward`

- **Prominent, flashing 'Claim' button** available at any time
- Offers **20 'Habbet'** (rewards/tokens) instantly
- No business_id required for general claim
- Endpoint: `POST /api/v1/claim/reward`

**Request Schema**:
```json
{
  "phone_number": "optional",
  "device_id": "optional",
  "display_name": "optional",
  "latitude": "optional",
  "longitude": "optional"
}
```

**Response**:
```json
{
  "success": true,
  "message": "🎉 Welcome! 20 Habbet (حبّات) credited to your wallet...",
  "user_id": "uuid",
  "credit_balance": 20.0,
  "royal_hospitality_end_date": "2026-03-11T...",
  "is_new_member": true,
  "transaction_id": "uuid"
}
```

### 3. Conversion Logic [cite: 2026-02-03]

**Implementation**: `app/auth_handler.py` - `claim_reward()`

When user clicks 'Claim':
1. ✅ **Guest → Active Member conversion**
   - `role` changes from `GUEST` to `MEMBER`
   - `is_guest` set to `False`
   - User becomes an Active Member

2. ✅ **20 Habbet credited to wallet**
   - `credit_balance` increased by 20
   - Credit transaction created
   - Ledger entry created for history

3. ✅ **30-Day Royal Hospitality Period**
   - `claim_date` set to current timestamp
   - `royal_hospitality_end_date` set to 30 days from claim

4. ✅ **Transaction Tracking**
   - `CreditTransaction` record created
   - `CreditLedger` entry created
   - Full audit trail maintained

**Prevention of Duplicate Claims**:
- System checks if user already claimed welcome reward
- Prevents multiple claims from same user
- Business-specific claims still allowed (separate endpoint)

### 4. Global Readiness - Scalability for 20,000 Users [cite: 2026-01-09]

**Database Optimizations**:

1. **Connection Pooling** (`app/core/database.py`):
   - `pool_size=10` - Base connection pool
   - `max_overflow=20` - Additional connections under load
   - `pool_pre_ping=True` - Automatic connection health checks

2. **Database Indexes** (`app/models/user.py`):
   ```python
   - idx_users_phone_number: Fast phone lookup
   - idx_users_role_status: Fast role/status filtering
   - idx_users_status_balance: Radar queries (Silent Decay Logic)
   - idx_users_last_seen: Activity tracking
   - idx_users_location: Geolocation queries
   - idx_users_created_at: User growth analytics
   ```

3. **Credit System Indexes** (`app/models/credit.py`):
   ```python
   - idx_credit_transactions_user_id: Fast user transaction lookup
   - idx_credit_transactions_user_type: Filtered transaction queries
   - idx_credit_transactions_timestamp: Time-based queries
   - idx_credit_ledger_user_timestamp: Ledger history queries
   ```

4. **Architecture**:
   - Centralized logic in `auth_handler.py` for maintainability
   - Efficient database queries with proper indexing
   - WebSocket support for real-time updates
   - Stateless API design for horizontal scaling

### 5. Clean Code Structure [cite: 2026-02-09]

**File Organization**:

```
app/
├── auth_handler.py              # ⭐ Centralized auth & onboarding logic
├── api/v1/endpoints/
│   ├── claim.py                 # Claim endpoints (uses auth_handler)
│   └── guest.py                 # Guest access endpoints
├── models/
│   ├── user.py                  # User model with indexes
│   └── credit.py                # Credit models with indexes
└── schemas/
    └── claim.py                 # Claim request/response schemas
```

**Key Design Principles**:
- **Single Responsibility**: `auth_handler.py` handles all auth/onboarding logic
- **DRY**: Reusable functions for common operations
- **Separation of Concerns**: Models, schemas, handlers, endpoints separated
- **Scalability**: Indexed queries, connection pooling, efficient data access

## API Endpoints

### Guest Access (No Authentication Required)

1. **Browse Businesses**
   ```
   GET /api/v1/guest/businesses
   Query params: latitude, longitude, radius_km, category
   ```

2. **View Business Details**
   ```
   GET /api/v1/guest/businesses/{business_id}
   ```

3. **Browse Posts**
   ```
   GET /api/v1/guest/posts
   Query params: latitude, longitude, radius_km, media_type
   ```

4. **View Post Details**
   ```
   GET /api/v1/guest/posts/{post_id}
   ```

### Claim Endpoints

1. **Claim Welcome Reward** (Available at any time)
   ```
   POST /api/v1/claim/reward
   Body: {
     "phone_number": "optional",
     "device_id": "optional",
     "display_name": "optional",
     "latitude": "optional",
     "longitude": "optional"
   }
   ```

2. **Claim Business** (Requires business_id)
   ```
   POST /api/v1/claim/business
   Body: {
     "business_id": "required",
     "phone_number": "optional",
     "device_id": "optional",
     "display_name": "optional",
     "latitude": "optional",
     "longitude": "optional"
   }
   ```

3. **Get Claim History**
   ```
   GET /api/v1/claim/claim-history/{user_id}
   ```

## Usage Examples

### Example 1: Guest Browsing
```python
# Guest can browse without any authentication
GET /api/v1/guest/businesses?latitude=33.5138&longitude=36.2765&radius_km=10
```

### Example 2: Claim Welcome Reward
```python
# User clicks flashing Claim button
POST /api/v1/claim/reward
{
  "phone_number": "+9611234567",
  "display_name": "John Doe",
  "latitude": 33.5138,
  "longitude": 36.2765
}

# Response:
{
  "success": true,
  "message": "🎉 Welcome! 20 Habbet (حبّات) credited...",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "credit_balance": 20.0,
  "is_new_member": true,
  "royal_hospitality_end_date": "2026-03-11T12:00:00Z"
}
```

### Example 3: Using auth_handler Directly
```python
from app.auth_handler import AuthHandler, get_guest_user, process_claim_reward

# Get or create guest user
guest = get_guest_user(
    db=db,
    device_id="device_123",
    display_name="Guest User"
)

# Process claim reward
result = process_claim_reward(
    db=db,
    phone_number="+9611234567",
    display_name="John Doe"
)
```

## Database Migration

To apply the new indexes for scalability:

```bash
# Create migration
alembic revision --autogenerate -m "Add indexes for scalability"

# Review migration file in alembic/versions/

# Apply migration
alembic upgrade head
```

## Testing

### Test Guest Access
```bash
curl -X GET "http://localhost:8000/api/v1/guest/businesses"
```

### Test Claim Reward
```bash
curl -X POST "http://localhost:8000/api/v1/claim/reward" \
  -H "Content-Type: application/json" \
  -d '{
    "phone_number": "+9611234567",
    "display_name": "Test User"
  }'
```

## Performance Considerations

For 20,000+ users:
- ✅ Database indexes on frequently queried fields
- ✅ Connection pooling (10 base + 20 overflow)
- ✅ Efficient queries with proper WHERE clauses
- ✅ WebSocket for real-time updates (non-blocking)
- ✅ Stateless API design for horizontal scaling

## Security Notes

- Guest access is read-only for sensitive operations
- Claim endpoint prevents duplicate claims
- Phone number validation (if provided)
- UUID-based user IDs prevent enumeration
- Transaction integrity via database transactions

## Future Enhancements

- Device fingerprinting for better guest tracking
- Rate limiting on claim endpoint
- Analytics for conversion tracking
- A/B testing for claim button placement
- Multi-language support for messages

---

**Implementation Date**: 2026-02-09  
**Status**: ✅ Complete and Production Ready  
**Scalability Target**: 20,000+ users [cite: 2026-01-09]
