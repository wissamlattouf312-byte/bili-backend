/**
 * Haversine distance in km between two lat/lng points.
 */
export function getDistanceKm(lat1, lng1, lat2, lng2) {
  const R = 6371; // Earth radius km
  const dLat = ((lat2 - lat1) * Math.PI) / 180;
  const dLng = ((lng2 - lng1) * Math.PI) / 180;
  const a =
    Math.sin(dLat / 2) * Math.sin(dLat / 2) +
    Math.cos((lat1 * Math.PI) / 180) *
      Math.cos((lat2 * Math.PI) / 180) *
      Math.sin(dLng / 2) *
      Math.sin(dLng / 2);
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
  return R * c;
}

/**
 * Filter places with lat/lng to those within radiusKm of user, add distance_km.
 */
export function filterNearMe(places, userLat, userLng, radiusKm) {
  if (userLat == null || userLng == null || !places?.length) return [];
  return places
    .map((p) => {
      const lat = p.lat ?? p.latitude;
      const lng = p.lng ?? p.longitude;
      if (lat == null || lng == null) return null;
      const distance_km = getDistanceKm(userLat, userLng, lat, lng);
      if (distance_km > radiusKm) return null;
      return { ...p, distance_km };
    })
    .filter(Boolean)
    .sort((a, b) => (a.distance_km ?? 0) - (b.distance_km ?? 0));
}

/**
 * Add distance_km to all places and sort by distance (no radius filter).
 * Use for admin-added pins so they always show in Store tab.
 */
export function addDistanceAndSort(places, userLat, userLng) {
  if (userLat == null || userLng == null || !places?.length) return [];
  return places
    .map((p) => {
      const lat = p.lat ?? p.latitude;
      const lng = p.lng ?? p.longitude;
      if (lat == null || lng == null) return null;
      const distance_km = getDistanceKm(userLat, userLng, lat, lng);
      return { ...p, distance_km };
    })
    .filter(Boolean)
    .sort((a, b) => (a.distance_km ?? 0) - (b.distance_km ?? 0));
}

/** Geolocation error codes */
export const GEOLOCATION = {
  PERMISSION_DENIED: 1,
  POSITION_UNAVAILABLE: 2,
  TIMEOUT: 3,
};
