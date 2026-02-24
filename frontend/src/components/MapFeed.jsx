import React from 'react';
import './MapFeed.css';

/**
 * Step 4: Feed of posts/photos. Clicking a photo triggers navigation to that location.
 */
export default function MapFeed({ items = [], onPhotoClick, emptyMessage }) {
  if (!items.length) {
    return (
      <p className="map-feed__empty">
        {emptyMessage || 'No posts or places with photos yet.'}
      </p>
    );
  }

  return (
    <ul className="map-feed__list">
      {items.map((item) => (
        <li key={item.id} className="map-feed__item">
          <button
            type="button"
            className="map-feed__thumb-btn"
            onClick={() => item.lat != null && item.lng != null && onPhotoClick?.(item.lat, item.lng, item.name)}
            aria-label={`Navigate to ${item.name}`}
          >
            {item.photo_url ? (
              <img src={item.photo_url} alt={item.name || ''} className="map-feed__thumb" />
            ) : (
              <div className="map-feed__thumb-placeholder">
                {item.is_vip ? '⭐' : item.type === 'flash_deal' ? '⚡' : '📍'}
              </div>
            )}
          </button>
          <div className="map-feed__meta">
            {item.is_vip && <span className="map-feed__vip">VIP</span>}
            <strong>{item.name}</strong>
            {item.vicinity && <span className="map-feed__vicinity">{item.vicinity}</span>}
            {item.description && <p className="map-feed__desc">{item.description}</p>}
            {item.distance_km != null && (
              <span className="map-feed__distance">~ {item.distance_km.toFixed(1)} km</span>
            )}
            {item.lat != null && item.lng != null && (
              <span className="map-feed__nav-hint">Tap to show route on map</span>
            )}
          </div>
        </li>
      ))}
    </ul>
  );
}
