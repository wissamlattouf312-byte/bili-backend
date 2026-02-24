/**
 * Loads store locations from static places.json (manual data only).
 * No Google Places API is used: no search, no autocomplete, no place fetching.
 * Add or edit frontend/public/places.json to change store locations.
 */
import { useState, useEffect } from 'react';

const PLACES_JSON_URL = process.env.PUBLIC_URL
  ? `${process.env.PUBLIC_URL.replace(/\/$/, '')}/places.json`
  : '/places.json';

let cachedPromise = null;

function fetchPlacesJson() {
  if (cachedPromise) return cachedPromise;
  cachedPromise = fetch(PLACES_JSON_URL)
    .then((r) => {
      if (!r.ok) throw new Error('Places not available');
      return r.json();
    })
    .then((data) => {
      const list = data?.places ?? (Array.isArray(data) ? data : []);
      return list;
    });
  return cachedPromise;
}

/**
 * Returns { places, loading, error }.
 * places: array of { place_id, name, vicinity, lat, lng, rating, user_ratings_total, photo_path }
 */
export function useSeedPlaces() {
  const [places, setPlaces] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    setLoading(true);
    setError(null);
    fetchPlacesJson()
      .then((list) => {
        setPlaces(Array.isArray(list) ? list : []);
        setError(null);
      })
      .catch((err) => {
        setPlaces([]);
        setError(err.message || 'Failed to load places');
      })
      .finally(() => setLoading(false));
  }, []);

  return { places, loading, error };
}

export default useSeedPlaces;
