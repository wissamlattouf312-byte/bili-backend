/**
 * BILI app config — change values here instead of in component source code.
 * Edit this file when you want to change reward amounts, labels, radar items, etc.
 */

/** "Near me" radius in km for Map and Store (places with promotions). */
export const nearMeRadiusKm = 15;

/** Fallback when geolocation fails (e.g. desktop, timeout). Beirut center so demo places show. */
export const defaultLocation = { lat: 33.9, lng: 35.5 };

/** Places that run promotions — used on Map and Store; only those near user are shown. */
export const placesWithPromotions = [
  {
    place_id: 'promo1',
    name: 'Coffee Hub',
    vicinity: 'Beirut',
    lat: 33.89,
    lng: 35.51,
    promotionText: 'Free tasting for 30 days · BILI powered',
    photo_urls: [],
    rating: 4.5,
  },
  {
    place_id: 'promo2',
    name: 'Gym Central',
    vicinity: 'Verdun',
    lat: 33.87,
    lng: 35.48,
    promotionText: '0.5 credit per ad after hospitality · 15km radius',
    photo_urls: [],
    rating: 4.2,
  },
  {
    place_id: 'promo3',
    name: 'Master Barber',
    vicinity: 'Hamra',
    lat: 33.9,
    lng: 35.48,
    promotionText: 'Elite Vault profile · Proximity alerts',
    photo_urls: [],
    rating: 4.8,
  },
];

export const appConfig = {
  /** Welcome reward amount (Habbet) when user claims from top coin or "20 حبة" button */
  claimReward: 25,

  /** Referral reward (Habbet) given to referrer when a new user claims */
  referralReward: 5,

  /** Royal Hospitality period in days (shown in UI; backend has its own setting) */
  royalHospitalityDays: 30,

  /** ROBO_Radar tab: demo list of nearby / activity items (edit titles and subtitles) */
  radarDemoItems: [
    { id: 'r1', title: 'Coffee Hub', subtitle: '~ 0.3 km • Open now', type: 'place' },
    { id: 'r2', title: 'Gym Central', subtitle: '~ 0.8 km • Opens 6:00', type: 'place' },
    { id: 'r3', title: 'Master Barber', subtitle: '~ 1.2 km • Open now', type: 'place' },
    { id: 'r4', title: 'Weekly offer', subtitle: '2 Habbet off • Ends in 2 days', type: 'offer' },
    { id: 'r5', title: 'New member nearby', subtitle: 'Just claimed 20 Habbet', type: 'activity' },
  ],
};

export default appConfig;
