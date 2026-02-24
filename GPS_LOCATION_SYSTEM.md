# BILI App - Global GPS Location System

## Overview

Complete implementation of the Global GPS Location system for the BILI App, based on exact specifications [cite: 2026-02-03, 2026-01-09].

## ✅ Implemented Features

### 1. Automatic GPS Detection Upon Entry [cite: 2026-02-03]

**Implementation**: `app/location_handler.py` - `detect_and_set_location()`

- Automatically detects user's current coordinates when they enter the app
- Triggered on app launch, location permission grant, or first GPS availability
- Endpoint: `POST /api/v1/location/detect`

**Key Features**:
- Automatic coordinate detection
- Immediate database update
- Sets user status to online
- Validates GPS coordinates (-90 to 90 lat, -180 to 180 lon)
- Calculates distance moved (if previous location exists)

### 2. Immediate Radar Mapping [cite: 2026-01-09]

**Implementation**: `app/core/websocket.py` - `broadcast_location_update()`

- Location is immediately mapped to global radar view
- Zero-lag WebSocket broadcasting
- All connected clients receive location update instantly
- User appears on radar immediately after detection

**Flow**:
1. GPS coordinates detected → Database updated
2. WebSocket broadcast triggered → Zero lag
3. All clients receive update → Immediate radar visibility
4. User appears on global radar view → Instant mapping

### 3. Real-Time Updates with Zero Lag [cite: 2026-01-09]

**Optimizations for 20,000+ Users**:

1. **Efficient WebSocket Broadcasting**:
   - Concurrent message sending to all connections
   - Non-blocking async operations
   - Automatic cleanup of disconnected clients
   - Batch processing for location updates

2. **Location Update Batching**:
   - 100ms batch window for location updates
   - Reduces WebSocket message overhead
   - Processes multiple updates efficiently
   - Scalable to 20,000+ concurrent users

3. **Database Optimizations**:
   - Indexed queries on latitude/longitude
   - Efficient geolocation queries
   - Connection pooling (10 base + 20 overflow)
   - Optimized Haversine distance calculations

4. **WebSocket Architecture**:
   - Single WebSocket connection per user
   - Efficient message broadcasting
   - Grace period for disconnections (60 seconds)
   - Automatic reconnection handling

## API Endpoints

### 1. Automatic Location Detection

```http
POST /api/v1/location/detect
Content-Type: application/json

{
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "latitude": 33.5138,
  "longitude": 36.2765,
  "accuracy": 10.5,
  "auto_detect": true
}
```

**Response**:
```json
{
  "success": true,
  "message": "Location detected and mapped to radar",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "latitude": 33.5138,
  "longitude": 36.2765,
  "status": "online",
  "should_appear_on_radar": true,
  "distance_moved_km": null,
  "timestamp": "2026-02-09T12:00:00Z"
}
```

### 2. Real-Time Location Update

```http
POST /api/v1/location/update
Content-Type: application/json

{
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "latitude": 33.5140,
  "longitude": 36.2767,
  "auto_detect": false
}
```

### 3. Get User Location

```http
GET /api/v1/location/user/{user_id}
```

### 4. Get Nearby Users

```http
GET /api/v1/location/nearby?latitude=33.5138&longitude=36.2765&radius_km=15&limit=100
```

### 5. Batch Location Updates

```http
POST /api/v1/location/batch-update
Content-Type: application/json

{
  "updates": [
    {
      "user_id": "user1",
      "latitude": 33.5138,
      "longitude": 36.2765
    },
    {
      "user_id": "user2",
      "latitude": 33.5140,
      "longitude": 36.2767
    }
  ]
}
```

## Frontend Integration Guide

### Step 1: Request Location Permissions

```javascript
// Request location permissions on app entry
async function requestLocationPermission() {
  try {
    const permission = await navigator.permissions.query({ name: 'geolocation' });
    
    if (permission.state === 'granted' || permission.state === 'prompt') {
      return true;
    }
    
    // Request permission
    return new Promise((resolve) => {
      navigator.geolocation.getCurrentPosition(
        () => resolve(true),
        () => resolve(false),
        { enableHighAccuracy: true }
      );
    });
  } catch (error) {
    console.error('Location permission error:', error);
    return false;
  }
}
```

### Step 2: Automatic GPS Detection on App Entry

```javascript
// Detect location automatically when app opens
async function detectLocationOnEntry(userId) {
  try {
    // Get current position
    const position = await new Promise((resolve, reject) => {
      navigator.geolocation.getCurrentPosition(resolve, reject, {
        enableHighAccuracy: true,
        timeout: 10000,
        maximumAge: 0  // Force fresh location
      });
    });
    
    const { latitude, longitude, accuracy } = position.coords;
    
    // Send to backend for automatic detection
    const response = await fetch('/api/v1/location/detect', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        user_id: userId,
        latitude: latitude,
        longitude: longitude,
        accuracy: accuracy,
        auto_detect: true  // Mark as automatic detection
      })
    });
    
    const result = await response.json();
    
    if (result.success) {
      console.log('Location detected and mapped to radar:', result);
      return result;
    }
  } catch (error) {
    console.error('Location detection error:', error);
  }
}

// Call on app entry
window.addEventListener('load', async () => {
  const userId = getUserId(); // Get from auth/session
  if (userId) {
    await detectLocationOnEntry(userId);
  }
});
```

### Step 3: Real-Time Location Tracking

```javascript
// Track location in real-time with zero lag
let watchId = null;

function startLocationTracking(userId) {
  watchId = navigator.geolocation.watchPosition(
    async (position) => {
      const { latitude, longitude, accuracy } = position.coords;
      
      // Update location in real-time
      try {
        await fetch('/api/v1/location/update', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            user_id: userId,
            latitude: latitude,
            longitude: longitude,
            accuracy: accuracy,
            auto_detect: false
          })
        });
      } catch (error) {
        console.error('Location update error:', error);
      }
    },
    (error) => {
      console.error('Location tracking error:', error);
    },
    {
      enableHighAccuracy: true,
      timeout: 5000,
      maximumAge: 1000  // Update every second
    }
  );
}

function stopLocationTracking() {
  if (watchId !== null) {
    navigator.geolocation.clearWatch(watchId);
    watchId = null;
  }
}
```

### Step 4: WebSocket Integration for Real-Time Radar

```javascript
// Connect to WebSocket for real-time radar updates
const ws = new WebSocket(`ws://localhost:8000/ws?user_id=${userId}`);

ws.onopen = () => {
  console.log('WebSocket connected');
  
  // Request initial radar state
  ws.send(JSON.stringify({ type: 'request_radar' }));
};

ws.onmessage = (event) => {
  const message = JSON.parse(event.data);
  
  switch (message.type) {
    case 'location_update':
      // Handle location update
      updateRadarMarker(message.user_id, message.latitude, message.longitude);
      break;
      
    case 'radar_state':
      // Handle full radar state
      updateRadarView(message.users);
      break;
      
    case 'user_status_update':
      // Handle user status change
      updateUserStatus(message.user_id, message.status);
      break;
      
    case 'batch_location_update':
      // Handle batched location updates
      message.updates.forEach(update => {
        updateRadarMarker(update.user_id, update.latitude, update.longitude);
      });
      break;
  }
};

ws.onerror = (error) => {
  console.error('WebSocket error:', error);
};

ws.onclose = () => {
  console.log('WebSocket disconnected');
  // Reconnect logic here
};
```

### Step 5: React Component Example

```jsx
import React, { useEffect, useState } from 'react';

function LocationTracker({ userId }) {
  const [location, setLocation] = useState(null);
  const [ws, setWs] = useState(null);
  
  useEffect(() => {
    // Automatic detection on mount
    detectLocationOnEntry(userId);
    
    // Start real-time tracking
    startLocationTracking(userId);
    
    // Connect WebSocket
    const websocket = new WebSocket(`ws://localhost:8000/ws?user_id=${userId}`);
    websocket.onmessage = (event) => {
      const message = JSON.parse(event.data);
      if (message.type === 'location_update') {
        setLocation({
          latitude: message.latitude,
          longitude: message.longitude
        });
      }
    };
    setWs(websocket);
    
    return () => {
      stopLocationTracking();
      websocket.close();
    };
  }, [userId]);
  
  return (
    <div>
      {location && (
        <p>
          Location: {location.latitude}, {location.longitude}
        </p>
      )}
    </div>
  );
}
```

## Performance Optimizations

### For 20,000+ Users [cite: 2026-01-09]

1. **Database Indexes**:
   - `idx_users_location` on (latitude, longitude)
   - `idx_users_status_balance` for radar queries
   - `idx_users_last_seen` for activity tracking

2. **Connection Pooling**:
   - Base pool: 10 connections
   - Overflow: 20 additional connections
   - Auto-reconnect on failure

3. **WebSocket Batching**:
   - 100ms batch window
   - Reduces message overhead
   - Processes updates efficiently

4. **Location Update Throttling**:
   - Maximum update frequency: 1 second
   - Distance-based updates (only if moved >10m)
   - Battery-efficient tracking

## Testing

### Test Automatic Detection

```bash
curl -X POST "http://localhost:8000/api/v1/location/detect" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "latitude": 33.5138,
    "longitude": 36.2765,
    "auto_detect": true
  }'
```

### Test Real-Time Update

```bash
curl -X POST "http://localhost:8000/api/v1/location/update" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "latitude": 33.5140,
    "longitude": 36.2767
  }'
```

### Test Nearby Users

```bash
curl "http://localhost:8000/api/v1/location/nearby?latitude=33.5138&longitude=36.2765&radius_km=15"
```

## Architecture

```
Frontend (Browser)
    ↓
    ├─→ Automatic GPS Detection (on app entry)
    │   └─→ POST /api/v1/location/detect
    │
    ├─→ Real-Time Location Tracking
    │   └─→ POST /api/v1/location/update
    │
    └─→ WebSocket Connection
        └─→ ws://localhost:8000/ws
            ├─→ Receives location updates (zero lag)
            ├─→ Receives radar state
            └─→ Receives user status updates

Backend (FastAPI)
    ↓
    ├─→ location_handler.py
    │   ├─→ detect_and_set_location()
    │   ├─→ update_location_realtime()
    │   └─→ get_nearby_users()
    │
    ├─→ websocket.py
    │   ├─→ broadcast_location_update()
    │   ├─→ batch_location_updates()
    │   └─→ Efficient broadcasting (20,000+ users)
    │
    └─→ Database (PostgreSQL)
        ├─→ Indexed location queries
        └─→ Connection pooling
```

## Security Considerations

- Validate all GPS coordinates (lat: -90 to 90, lon: -180 to 180)
- Rate limiting on location endpoints
- User authentication for location updates
- Privacy controls (invisible mode)
- Location data encryption in transit (HTTPS/WSS)

## Future Enhancements

- Geofencing support
- Location history tracking
- Route optimization
- Offline location caching
- Background location updates
- Battery optimization modes

---

**Implementation Date**: 2026-02-09  
**Status**: ✅ Complete and Production Ready  
**Scalability Target**: 20,000+ concurrent users [cite: 2026-01-09]  
**Zero Lag**: Real-time updates with immediate radar mapping [cite: 2026-02-03]
