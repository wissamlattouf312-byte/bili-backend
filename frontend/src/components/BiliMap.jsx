import React, { useState, useEffect, useRef, useMemo, useCallback } from 'react';
import { GoogleMap, Marker, InfoWindow, DirectionsService, DirectionsRenderer } from '@react-google-maps/api';
import MapFeed from './MapFeed';
import { nearMeRadiusKm, defaultLocation } from '../appConfig';
import { filterNearMe, GEOLOCATION } from '../utils/geo';
import useSeedPlaces from '../hooks/useSeedPlaces';
import './BiliMap.css';

const API_BASE = process.env.REACT_APP_API_URL || '';
const GOOGLE_MAPS_API_KEY = process.env.REACT_APP_GOOGLE_MAPS_API_KEY || '';

const defaultCenter = { lat: 33.9, lng: 35.5 }; // Lebanon
const defaultZoom = 10;
const mapContainerStyle = { width: '100%', height: '100%', minHeight: '280px' };

// Sync map view to user location (center + zoom 14 on first fix)
function useUserLocationTracker(mapRef, userPosition) {
  const didCenter = useRef(false);
  useEffect(() => {
    const map = mapRef.current;
    if (!map || !userPosition?.lat || !userPosition?.lng) return;
    map.panTo({ lat: userPosition.lat, lng: userPosition.lng });
    if (!didCenter.current) {
      didCenter.current = true;
      map.setZoom(14);
    }
  }, [mapRef, userPosition]);
}

// Options that work better on desktop (no GPS): prefer cache, longer timeout
const GEO_OPTIONS = {
  enableHighAccuracy: false,
  timeout: 20000,
  maximumAge: 300000, // 5 min cache OK
};

export default function BiliMap({ initialDestination = null, onClearNavigation, isScriptLoaded = false, scriptLoadError = null }) {
  const { places: seedPlaces, loading: placesLoading, error: placesError } = useSeedPlaces();
  const [userPosition, setUserPosition] = useState(null);
  const [locationDenied, setLocationDenied] = useState(false);
  const [usingFallback, setUsingFallback] = useState(false);
  const [vipBusinesses, setVipBusinesses] = useState([]);
  const [flashDeals, setFlashDeals] = useState([]);
  const [manualPins, setManualPins] = useState([]);
  const mapRef = useRef(null);
  const [selectedMarker, setSelectedMarker] = useState(null); // { position: { lat, lng }, content, name? } name = store name for Navigate
  // In-app navigation: destination { lat, lng, name }; route stays on our map (no external Google Maps)
  const [navigationDestination, setNavigationDestination] = useState(initialDestination);
  const [directionsResult, setDirectionsResult] = useState(null);

  useUserLocationTracker(mapRef, userPosition);

  // Sync when App passes initialDestination (e.g. from Store "Navigate")
  useEffect(() => {
    if (initialDestination) setNavigationDestination(initialDestination);
  }, [initialDestination]);

  // Clear route when destination changes so we don't show stale directions
  useEffect(() => {
    if (!navigationDestination) setDirectionsResult(null);
  }, [navigationDestination]);

  const clearNavigation = useCallback(() => {
    setNavigationDestination(null);
    setDirectionsResult(null);
    onClearNavigation?.();
  }, [onClearNavigation]);

  const onMapLoad = useCallback((mapInstance) => {
    mapRef.current = mapInstance;
  }, []);

  // User location: real or fallback when unavailable/timeout (so map still works)
  useEffect(() => {
    if (!navigator.geolocation) {
      setUserPosition(defaultLocation);
      setUsingFallback(true);
      return;
    }
    const watchId = navigator.geolocation.watchPosition(
      (pos) => {
        setUserPosition({
          lat: pos.coords.latitude,
          lng: pos.coords.longitude,
        });
        setLocationDenied(false);
        setUsingFallback(false);
      },
      (err) => {
        // Always use demo area so map still works (denied, unavailable, or "location disabled")
        setUserPosition(defaultLocation);
        setUsingFallback(true);
        setLocationDenied(err?.code === GEOLOCATION.PERMISSION_DENIED);
      },
      GEO_OPTIONS
    );
    return () => navigator.geolocation.clearWatch(watchId);
  }, []);

  // VIP businesses (BILI registered)
  useEffect(() => {
    fetch(`${API_BASE}/api/v1/map/vip-businesses`)
      .then((r) => (r.ok ? r.json() : { businesses: [] }))
      .then((data) => setVipBusinesses(data.businesses || []))
      .catch(() => setVipBusinesses([]));
  }, []);

  // Flash deals (active, not expired)
  useEffect(() => {
    fetch(`${API_BASE}/api/v1/flash-deals/active`)
      .then((r) => (r.ok ? r.json() : []))
      .then(setFlashDeals)
      .catch(() => setFlashDeals([]));
  }, []);

  // Manual map pins (admin-added; no Places API). Refetch when admin adds/removes.
  const fetchManualPins = useCallback(() => {
    fetch(`${API_BASE}/api/v1/map/pins`)
      .then((r) => (r.ok ? r.json() : []))
      .then(setManualPins)
      .catch(() => setManualPins([]));
  }, []);
  useEffect(() => {
    fetchManualPins();
  }, [fetchManualPins]);
  useEffect(() => {
    const onPinsUpdated = () => fetchManualPins();
    window.addEventListener('bili_map_pins_updated', onPinsUpdated);
    return () => window.removeEventListener('bili_map_pins_updated', onPinsUpdated);
  }, [fetchManualPins]);

  const vipNearMe = useMemo(
    () =>
      filterNearMe(
        vipBusinesses.map((b) => ({ ...b, lat: b.latitude, lng: b.longitude })),
        userPosition?.lat,
        userPosition?.lng,
        nearMeRadiusKm
      ),
    [vipBusinesses, userPosition?.lat, userPosition?.lng]
  );
  const flashDealsNearMe = useMemo(
    () =>
      filterNearMe(
        flashDeals.map((d) => ({ ...d, lat: d.latitude, lng: d.longitude })),
        userPosition?.lat,
        userPosition?.lng,
        nearMeRadiusKm
      ),
    [flashDeals, userPosition?.lat, userPosition?.lng]
  );
  const placesNearMe = useMemo(
    () => filterNearMe(seedPlaces, userPosition?.lat, userPosition?.lng, nearMeRadiusKm),
    [seedPlaces, userPosition?.lat, userPosition?.lng]
  );

  const googlePlaceIdsFromVip = new Set(vipBusinesses.map((b) => b.google_place_id));
  const placesOnMap = placesNearMe.filter((p) => !googlePlaceIdsFromVip.has(p.place_id));

  const manualPinsNearMe = useMemo(
    () =>
      filterNearMe(
        manualPins.map((p) => ({ ...p, lat: p.latitude, lng: p.longitude })),
        userPosition?.lat,
        userPosition?.lng,
        nearMeRadiusKm
      ),
    [manualPins, userPosition?.lat, userPosition?.lng]
  );

  const feedItems = useMemo(() => {
    const items = [];
    vipNearMe.forEach((b) => {
      items.push({
        id: `vip-${b.id}`,
        type: 'vip',
        name: b.display_name || b.name,
        lat: b.latitude,
        lng: b.longitude,
        photo_url: null,
        is_vip: true,
        distance_km: b.distance_km,
      });
    });
    flashDealsNearMe.forEach((d) => {
      items.push({
        id: `flash-${d.id}`,
        type: 'flash_deal',
        name: d.title,
        description: d.description,
        lat: d.latitude,
        lng: d.longitude,
        photo_url: d.image_url,
        expires_at: d.expires_at,
        distance_km: d.distance_km,
      });
    });
    placesNearMe.forEach((p) => {
      const photoUrl = p.photo_path
        ? (process.env.PUBLIC_URL || '').replace(/\/$/, '') + p.photo_path
        : null;
      items.push({
        id: p.place_id,
        type: 'place',
        name: p.name,
        vicinity: p.vicinity,
        description:
          p.rating != null && p.user_ratings_total != null
            ? `Rating ${p.rating} · ${p.user_ratings_total} reviews`
            : null,
        lat: p.lat,
        lng: p.lng,
        photo_url: photoUrl,
        distance_km: p.distance_km,
      });
    });
    manualPinsNearMe.forEach((p) => {
      items.push({
        id: `pin-${p.id}`,
        type: 'manual_pin',
        name: p.name,
        lat: p.latitude,
        lng: p.longitude,
        photo_url: p.latest_content_thumbnail || null,
        description: p.latest_content_title || null,
        latest_content_url: p.latest_content_url || null,
        distance_km: p.distance_km,
      });
    });
    return items;
  }, [vipNearMe, flashDealsNearMe, placesNearMe, manualPinsNearMe]);

  // Start in-app navigation on our map (user stays in app; no external Google Maps)
  const handlePhotoClick = (lat, lng, name) => {
    setNavigationDestination({ lat, lng, name: name || 'Store' });
  };

  const mapCenter = userPosition
    ? { lat: userPosition.lat, lng: userPosition.lng }
    : defaultCenter;

  if (!GOOGLE_MAPS_API_KEY) {
    return (
      <div className="bili-map-wrap">
        <div className="bili-map-feed-panel">
          <p className="map-feed__empty">
            Set REACT_APP_GOOGLE_MAPS_API_KEY in frontend/.env to show the map.
          </p>
        </div>
        <div className="bili-map-container bili-map-container--placeholder">
          <div className="bili-map bili-map--placeholder">Map requires Maps JavaScript API key.</div>
        </div>
      </div>
    );
  }

  if (scriptLoadError) {
    return (
      <div className="bili-map-wrap">
        <div className="bili-map-feed-panel" />
        <div className="bili-map-container bili-map-container--placeholder">
          <div className="bili-map bili-map--placeholder">Map failed to load. Check your API key and network.</div>
        </div>
      </div>
    );
  }

  if (!isScriptLoaded) {
    return (
      <div className="bili-map-wrap">
        <div className="bili-map-feed-panel" />
        <div className="bili-map-container bili-map-container--placeholder">
          <div className="bili-map bili-map--loading">Loading map…</div>
        </div>
      </div>
    );
  }

  return (
    <div className="bili-map-wrap">
      <div className="bili-map-feed-panel">
        <h3>Near me</h3>
        {(usingFallback || locationDenied) && (
          <div className="bili-map-feed-fallback-wrap">
            <p className="bili-map-feed-fallback">
              {locationDenied
                ? "Using demo area (Beirut) — location was denied or the browser reported it as disabled. You can still browse the map and stores."
                : "Using demo area — we couldn't detect your position. You can still browse the map and stores."}
            </p>
            <button
              type="button"
              className="bili-map-feed-try-again"
              onClick={() => {
                setUsingFallback(false);
                setLocationDenied(false);
                setUserPosition(null);
                navigator.geolocation?.getCurrentPosition(
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
              }}
            >
              Try location again
            </button>
          </div>
        )}
        {placesLoading && <p className="map-feed__empty">Loading places…</p>}
        {placesError && <p className="map-feed__empty">{placesError}</p>}
        {navigationDestination && (
          <div className="bili-map-nav-bar">
            <span className="bili-map-nav-dest">Walking to: {navigationDestination.name}</span>
            <button type="button" className="bili-map-nav-clear" onClick={clearNavigation}>
              Clear route
            </button>
          </div>
        )}
        {!placesLoading && !placesError && (
          <MapFeed
            items={feedItems}
            onPhotoClick={handlePhotoClick}
            emptyMessage={
              !userPosition
                ? 'Getting your location…'
                : 'No places near you in this area. Use the button below to explore the demo.'
            }
          />
        )}
        {!placesLoading &&
          !placesError &&
          feedItems.length === 0 &&
          userPosition &&
          !usingFallback && (
            <div className="bili-map-feed-fallback-wrap">
              <button
                type="button"
                className="bili-map-feed-try-again"
                onClick={() => {
                  setUserPosition(defaultLocation);
                  setUsingFallback(true);
                }}
              >
                Show demo area (Beirut)
              </button>
            </div>
          )}
      </div>
      <div className="bili-map-container">
        <GoogleMap
            mapContainerStyle={mapContainerStyle}
            center={mapCenter}
            zoom={defaultZoom}
            onLoad={onMapLoad}
            options={{ scrollwheel: true }}
            className="bili-map"
          >
            {userPosition && (
              <Marker
                position={{ lat: userPosition.lat, lng: userPosition.lng }}
                label={{ text: '🚗', fontSize: '24px' }}
                zIndex={1000}
                onClick={() =>
                  setSelectedMarker({
                    position: { lat: userPosition.lat, lng: userPosition.lng },
                    content: 'You (BILI)',
                    name: null,
                  })
                }
              />
            )}
            {vipNearMe.map((b) => (
              <Marker
                key={`vip-${b.id}`}
                position={{ lat: b.latitude, lng: b.longitude }}
                label={{ text: '⭐', fontSize: '20px' }}
                zIndex={900}
                onClick={() =>
                  setSelectedMarker({
                    position: { lat: b.latitude, lng: b.longitude },
                    content: (
                      <>
                        <strong>⭐ {b.display_name || b.name}</strong>
                        <br />
                        BILI Partner
                      </>
                    ),
                    name: b.display_name || b.name,
                  })
                }
              />
            ))}
            {flashDealsNearMe.map((d) => (
              <Marker
                key={`flash-${d.id}`}
                position={{ lat: d.latitude, lng: d.longitude }}
                label={{ text: '📍', fontSize: '18px' }}
                onClick={() =>
                  setSelectedMarker({
                    position: { lat: d.latitude, lng: d.longitude },
                    content: (
                      <>
                        <strong>⚡ {d.title}</strong>
                        <br />
                        Flash Deal · 24h
                      </>
                    ),
                    name: d.title,
                  })
                }
              />
            ))}
            {placesOnMap.map((p) => (
              <Marker
                key={p.place_id}
                position={{ lat: p.lat, lng: p.lng }}
                label={{ text: '📍', fontSize: '18px' }}
                onClick={() =>
                  setSelectedMarker({
                    position: { lat: p.lat, lng: p.lng },
                    content: p.name,
                    name: p.name,
                  })
                }
              />
            ))}
            {manualPins.map((pin) => (
              <Marker
                key={pin.id}
                position={{ lat: pin.latitude, lng: pin.longitude }}
                label={{ text: '📍', fontSize: '18px' }}
                onClick={() =>
                  setSelectedMarker({
                    position: { lat: pin.latitude, lng: pin.longitude },
                    content: (
                      <>
                        <strong>{pin.name}</strong>
                        {pin.latest_content_thumbnail && (
                          <div className="bili-map-infowindow-media">
                            <a
                              href={pin.latest_content_url || '#'}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="bili-map-infowindow-thumb-link"
                            >
                              <img
                                src={pin.latest_content_thumbnail}
                                alt=""
                                className="bili-map-infowindow-thumb"
                              />
                            </a>
                            {pin.latest_content_title && (
                              <span className="bili-map-infowindow-latest-title">
                                {pin.latest_content_title.slice(0, 60)}
                                {pin.latest_content_title.length > 60 ? '…' : ''}
                              </span>
                            )}
                          </div>
                        )}
                      </>
                    ),
                    name: pin.name,
                  })
                }
              />
            ))}
            {selectedMarker?.position && (
              <InfoWindow
                position={selectedMarker.position}
                onCloseClick={() => setSelectedMarker(null)}
              >
                <div className="bili-map-infowindow">
                  {typeof selectedMarker.content === 'string'
                    ? selectedMarker.content
                    : selectedMarker.content}
                  {selectedMarker.name && (
                    <button
                      type="button"
                      className="bili-map-infowindow-nav"
                      onClick={() => {
                        setNavigationDestination({
                          lat: selectedMarker.position.lat,
                          lng: selectedMarker.position.lng,
                          name: selectedMarker.name,
                        });
                        setSelectedMarker(null);
                      }}
                    >
                      Navigate (walking route on map)
                    </button>
                  )}
                </div>
              </InfoWindow>
            )}
            {navigationDestination && (
              <DirectionsService
                options={{
                  origin: userPosition
                    ? { lat: userPosition.lat, lng: userPosition.lng }
                    : defaultCenter,
                  destination: {
                    lat: navigationDestination.lat,
                    lng: navigationDestination.lng,
                  },
                  travelMode: 'WALKING',
                }}
                callback={(result, status) => {
                  if (status === 'OK' && result) {
                    setDirectionsResult(result);
                    const map = mapRef.current;
                    if (map && result.routes?.[0]?.bounds) {
                      map.fitBounds(result.routes[0].bounds, { top: 60, right: 60, bottom: 60, left: 60 });
                    }
                  } else {
                    setDirectionsResult(null);
                  }
                }}
              />
            )}
            {directionsResult && <DirectionsRenderer directions={directionsResult} options={{ suppressMarkers: false }} />}
          </GoogleMap>
      </div>
    </div>
  );
}
