/**
 * BILI Master System - Location Radar Component
 * [cite: 2026-02-09]
 * 
 * Integrates with location_handler.py data stream via WebSocket
 * Displays real-time user locations on global radar view
 */
import React, { useState, useEffect, useRef } from 'react';
import './LocationRadar.css';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
// Derive WebSocket URL from API URL so one env var works (https://api.x → wss://api.x)
const WS_BASE_URL =
  process.env.REACT_APP_WS_URL ||
  (API_BASE_URL.replace(/^http/, 'ws') || 'ws://localhost:8000');

const LocationRadar = ({ userId, userLocation }) => {
  const [radarUsers, setRadarUsers] = useState([]);
  const [isConnected, setIsConnected] = useState(false);
  const [error, setError] = useState(null);
  const wsRef = useRef(null);
  const mapRef = useRef(null);

  useEffect(() => {
    // Initialize location detection on mount
    if (userLocation && userId) {
      detectLocationOnEntry();
    }

    // Connect to WebSocket for real-time updates
    connectWebSocket();

    // Cleanup on unmount
    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [userId, userLocation]);

  const detectLocationOnEntry = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/location/detect`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_id: userId,
          latitude: userLocation.latitude,
          longitude: userLocation.longitude,
          auto_detect: true
        }),
      });

      if (response.ok) {
        const data = await response.json();
        console.log('Location detected and mapped to radar:', data);
      }
    } catch (err) {
      console.error('Location detection error:', err);
    }
  };

  const connectWebSocket = () => {
    // Don't connect if no userId
    if (!userId) {
      return;
    }

    try {
      const ws = new WebSocket(`${WS_BASE_URL}/ws?user_id=${userId || ''}`);
      wsRef.current = ws;

      // Set connection timeout
      const connectionTimeout = setTimeout(() => {
        if (ws.readyState === WebSocket.CONNECTING) {
          ws.close();
          setError('Connection timeout. Radar will reconnect when backend is ready.');
        }
      }, 5000);

      ws.onopen = () => {
        clearTimeout(connectionTimeout);
        setIsConnected(true);
        setError(null);
        
        // Request initial radar state
        try {
          ws.send(JSON.stringify({ type: 'request_radar' }));
        } catch (e) {
          // Ignore send errors
        }
      };

      ws.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data);
          
          switch (message.type) {
            case 'radar_state':
              setRadarUsers(message.users || []);
              break;
              
            case 'location_update':
              updateUserLocation(message);
              break;
              
            case 'batch_location_update':
              if (message.updates && Array.isArray(message.updates)) {
                message.updates.forEach(update => {
                  updateUserLocation(update);
                });
              }
              break;
              
            case 'user_status_update':
              if (message.user_id) {
                updateUserStatus(message.user_id, message.status);
              }
              break;
          }
        } catch (err) {
          // Ignore parse errors - invalid message format
        }
      };

      ws.onerror = (error) => {
        clearTimeout(connectionTimeout);
        setIsConnected(false);
        // Don't show error immediately - backend may be starting
        setError(null);
      };

      ws.onclose = () => {
        clearTimeout(connectionTimeout);
        setIsConnected(false);
        
        // Only reconnect if we have a userId and it wasn't a manual close
        if (userId && wsRef.current === ws) {
          // Reconnect after 5 seconds (longer delay to avoid spam)
          setTimeout(() => {
            if (wsRef.current === ws) {
              connectWebSocket();
            }
          }, 5000);
        }
      };
    } catch (err) {
      // Silently fail - WebSocket may not be available
      setError(null);
    }
  };

  const updateUserLocation = (update) => {
    setRadarUsers(prevUsers => {
      const existingIndex = prevUsers.findIndex(u => u.user_id === update.user_id);
      const updatedUser = {
        ...update,
        latitude: update.latitude,
        longitude: update.longitude
      };

      if (existingIndex >= 0) {
        const updated = [...prevUsers];
        updated[existingIndex] = updatedUser;
        return updated;
      } else {
        return [...prevUsers, updatedUser];
      }
    });
  };

  const updateUserStatus = (user_id, status) => {
    setRadarUsers(prevUsers =>
      prevUsers.map(user =>
        user.user_id === user_id ? { ...user, status } : user
      )
    );
  };

  const calculateDistance = (lat1, lon1, lat2, lon2) => {
    const R = 6371; // Earth radius in km
    const dLat = (lat2 - lat1) * Math.PI / 180;
    const dLon = (lon2 - lon1) * Math.PI / 180;
    const a = Math.sin(dLat / 2) * Math.sin(dLat / 2) +
              Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
              Math.sin(dLon / 2) * Math.sin(dLon / 2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
    return R * c;
  };

  return (
    <div className="location-radar-container">
      <div className="radar-header">
        <h2>🌍 Global Radar</h2>
        <div className={`connection-status ${isConnected ? 'connected' : 'disconnected'}`}>
          {isConnected ? '● Connected' : '○ Disconnected'}
        </div>
      </div>

      {error && <div className="radar-error">{error}</div>}

      <div className="radar-map" ref={mapRef}>
        {userLocation && (
          <div className="user-marker current-user" style={{
            left: '50%',
            top: '50%',
            transform: 'translate(-50%, -50%)'
          }}>
            <div className="marker-pulse"></div>
            <div className="marker-label">You</div>
          </div>
        )}

        {radarUsers.map((user, index) => {
          if (!userLocation) return null;
          
          const distance = calculateDistance(
            userLocation.latitude,
            userLocation.longitude,
            user.latitude,
            user.longitude
          );

          // Simple relative positioning (for demo - use Google Maps in production)
          const angle = Math.random() * 360;
          const radius = Math.min(distance / 100, 0.4); // Scale to fit
          const x = 50 + radius * Math.cos(angle * Math.PI / 180) * 100;
          const y = 50 + radius * Math.sin(angle * Math.PI / 180) * 100;

          return (
            <div
              key={user.user_id || index}
              className={`user-marker ${user.status}`}
              style={{
                left: `${x}%`,
                top: `${y}%`,
                transform: 'translate(-50%, -50%)'
              }}
              title={`${user.display_name || 'User'} - ${distance.toFixed(1)} km away`}
            >
              <div className="marker-dot"></div>
              <div className="marker-label">{user.display_name || 'User'}</div>
            </div>
          );
        })}
      </div>

      <div className="radar-stats">
        <div className="stat-item">
          <span className="stat-label">Users Online:</span>
          <span className="stat-value">{radarUsers.filter(u => u.status === 'online').length}</span>
        </div>
        <div className="stat-item">
          <span className="stat-label">Total Visible:</span>
          <span className="stat-value">{radarUsers.length}</span>
        </div>
      </div>
    </div>
  );
};

export default LocationRadar;
