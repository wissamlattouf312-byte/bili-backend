import React, { useEffect, useState, useMemo } from 'react';
import { nearMeRadiusKm, defaultLocation } from '../appConfig';
import { filterNearMe, addDistanceAndSort, GEOLOCATION } from '../utils/geo';
import useSeedPlaces from '../hooks/useSeedPlaces';

const API_BASE = process.env.REACT_APP_API_URL || 'http://127.0.0.1:8000';

// Same as Map: prefer cache, longer timeout (works better on desktop / no GPS)
const GEO_OPTIONS = {
  enableHighAccuracy: false,
  timeout: 20000,
  maximumAge: 300000,
};

export default function StoreFeed() {
  const { places: seedPlaces, loading: placesLoading, error: placesError } = useSeedPlaces();
  const [userPosition, setUserPosition] = useState(null);
  const [locationDenied, setLocationDenied] = useState(false);
  const [usingFallback, setUsingFallback] = useState(false);
  const [selected, setSelected] = useState(null);
  const [manualPins, setManualPins] = useState([]);

  const fetchPins = () => {
    fetch(`${API_BASE}/api/v1/map/pins`)
      .then((r) => (r.ok ? r.json() : []))
      .then(setManualPins)
      .catch(() => setManualPins([]));
  };

  useEffect(() => {
    fetchPins();
    const onPinsUpdated = () => fetchPins();
    window.addEventListener('bili_map_pins_updated', onPinsUpdated);
    return () => window.removeEventListener('bili_map_pins_updated', onPinsUpdated);
  }, []);

  const manualPinsAsPlaces = useMemo(
    () =>
      manualPins.map((p) => ({
        place_id: `pin-${p.id}`,
        name: p.name || 'Store',
        lat: p.latitude,
        lng: p.longitude,
        imageUrl: p.latest_content_thumbnail || null,
      })),
    [manualPins]
  );

  const seedNearMe = useMemo(
    () => filterNearMe(seedPlaces, userPosition?.lat, userPosition?.lng, nearMeRadiusKm),
    [seedPlaces, userPosition?.lat, userPosition?.lng]
  );

  // Seed places: only within "near me" radius. Admin pins: show all, sorted by distance.
  const pinsWithDistance = useMemo(
    () => addDistanceAndSort(manualPinsAsPlaces, userPosition?.lat, userPosition?.lng),
    [manualPinsAsPlaces, userPosition?.lat, userPosition?.lng]
  );

  const places = useMemo(
    () => [...seedNearMe, ...pinsWithDistance].sort((a, b) => (a.distance_km ?? 0) - (b.distance_km ?? 0)),
    [seedNearMe, pinsWithDistance]
  );

  useEffect(() => {
    if (!navigator.geolocation) {
      setUserPosition(defaultLocation);
      setUsingFallback(true);
      return;
    }
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        setUserPosition({ lat: pos.coords.latitude, lng: pos.coords.longitude });
        setLocationDenied(false);
        setUsingFallback(false);
      },
      (err) => {
        // Always use demo area so the app still works (denied, unavailable, or "location disabled")
        setUserPosition(defaultLocation);
        setUsingFallback(true);
        setLocationDenied(err?.code === GEOLOCATION.PERMISSION_DENIED);
      },
      GEO_OPTIONS
    );
  }, []);

  // If location is taking too long or browser never responds, use demo so user isn't stuck
  useEffect(() => {
    if (userPosition) return;
    const t = setTimeout(() => {
      setUserPosition(defaultLocation);
      setUsingFallback(true);
    }, 8000);
    return () => clearTimeout(t);
  }, [userPosition]);

  const startInAppNavigation = (lat, lng, name) => {
    window.dispatchEvent(
      new CustomEvent('bili_navigate_to', { detail: { lat, lng, name: name || 'Store' } })
    );
  };

  const tryLocationAgain = () => {
    setLocationDenied(false);
    setUserPosition(null);
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (pos) => {
          setUserPosition({ lat: pos.coords.latitude, lng: pos.coords.longitude });
          setUsingFallback(false);
        },
        () => {
          setUserPosition(defaultLocation);
          setUsingFallback(true);
        },
        GEO_OPTIONS
      );
    } else {
      setUserPosition(defaultLocation);
      setUsingFallback(true);
    }
  };

  if (!userPosition) {
    return (
      <div className="store-feed__status-wrap">
        <p className="store-feed__status">Getting your location…</p>
        <button
          type="button"
          className="store-feed__use-demo-btn"
          onClick={() => {
            setUserPosition(defaultLocation);
            setUsingFallback(true);
          }}
        >
          Use demo area instead
        </button>
      </div>
    );
  }

  if (placesLoading) {
    return <p className="store-feed__status">Loading places…</p>;
  }

  if (placesError) {
    return <p className="store-feed__status store-feed__status--error">{placesError}</p>;
  }

  if (!places.length) {
    return (
      <div className="store-feed__status-wrap store-feed__no-nearby">
        <p className="store-feed__status">
          No places in your area yet. Tap below to explore the demo area (Beirut).
        </p>
        <p className="store-feed__status-hint">
          On desktop, location can be approximate (Wi‑Fi/IP). Run the seed script to add more areas.
        </p>
        <button
          type="button"
          className="store-feed__use-demo-btn"
          onClick={() => {
            setUserPosition(defaultLocation);
            setUsingFallback(true);
          }}
        >
          Show demo area (Beirut)
        </button>
      </div>
    );
  }

  return (
    <div className="store-feed">
      {(usingFallback || locationDenied) && (
        <div className="store-feed__fallback-wrap">
          <p className="store-feed__status store-feed__fallback">
            {locationDenied
              ? "Using demo area (Beirut) — location was denied or the browser reported it as disabled. You can still browse stores and the map."
              : "Using demo area — we couldn't detect your position. You can still browse stores and the map."}
          </p>
          <button
            type="button"
            className="store-feed__try-again-btn"
            onClick={tryLocationAgain}
          >
            Try location again
          </button>
        </div>
      )}
      <p className="store-feed__subtitle">Near you</p>
      {places.map((place) => {
        const photoSrc = place.imageUrl
          ? place.imageUrl
          : place.photo_path
            ? (process.env.PUBLIC_URL || '').replace(/\/$/, '') + place.photo_path
            : null;
        return (
          <article
            key={place.place_id}
            className={`store-feed__item ${selected?.place_id === place.place_id ? 'store-feed__item--selected' : ''}`}
            onClick={() => setSelected(selected?.place_id === place.place_id ? null : place)}
            role="button"
            tabIndex={0}
            onKeyDown={(e) => {
              if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                setSelected(selected?.place_id === place.place_id ? null : place);
              }
            }}
            aria-label={`View ${place.name}`}
          >
            <div className="store-feed__thumb">
              {photoSrc ? (
                <img src={photoSrc} alt={place.name} />
              ) : (
                <div className="store-feed__thumb-placeholder">📍</div>
              )}
            </div>
            <div className="store-feed__meta">
              <h3>{place.name}</h3>
              {(place.rating != null || place.user_ratings_total != null) && (
                <p>
                  {place.rating != null && `Rating ${place.rating}`}
                  {place.rating != null && place.user_ratings_total != null && ' · '}
                  {place.user_ratings_total != null && `${place.user_ratings_total} reviews`}
                </p>
              )}
              {place.distance_km != null && (
                <span className="store-feed__distance">~ {place.distance_km.toFixed(1)} km</span>
              )}
            </div>
          </article>
        );
      })}
      {selected && (
        <div className="store-feed__detail" role="dialog" aria-label="Place detail">
          <div className="store-feed__detail-inner">
            <h3>{selected.name}</h3>
            {(selected.rating != null || selected.user_ratings_total != null) && (
              <p>
                {selected.rating != null && `Rating ${selected.rating}`}
                {selected.rating != null && selected.user_ratings_total != null && ' · '}
                {selected.user_ratings_total != null && `${selected.user_ratings_total} reviews`}
              </p>
            )}
            {selected.distance_km != null && (
              <p className="store-feed__detail-distance">~ {selected.distance_km.toFixed(1)} km</p>
            )}
            <button
              type="button"
              className="store-feed__detail-nav"
              onClick={(e) => {
                e.stopPropagation();
                startInAppNavigation(selected.lat, selected.lng, selected.name);
              }}
            >
              Navigate
            </button>
            <button
              type="button"
              className="store-feed__detail-close"
              onClick={(e) => { e.stopPropagation(); setSelected(null); }}
            >
              Close
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
