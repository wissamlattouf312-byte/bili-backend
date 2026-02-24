import React, { useState, useEffect } from 'react';
import { useLoadScript } from '@react-google-maps/api';
import './App.css';
import { appConfig } from './appConfig';
import TopCounter from './components/TopCounter';
import StoreFeed from './components/StoreFeed';
import WalletPanel from './components/WalletPanel';
import ClaimButton from './components/ClaimButton';
import AddToHomeScreenPrompt from './components/AddToHomeScreenPrompt';
import BiliMap from './components/BiliMap';
import AdminPanel from './components/AdminPanel';

const GOOGLE_MAPS_API_KEY = process.env.REACT_APP_GOOGLE_MAPS_API_KEY || '';

const WELCOME_KEY = 'bili_welcome_claimed';
const USER_KEY = 'bili_user_id';
const CREDITS_CLAIMED = 'bili_credits_claimed';
const CREDITS_BALANCE = 'bili_credits_balance';

function hasClaimedWelcome() {
  try {
    const rewardStr = String(appConfig.claimReward);
    if (window.localStorage?.getItem(WELCOME_KEY) === '1') return true;
    if (window.localStorage?.getItem(CREDITS_CLAIMED) === rewardStr) return true;
    if (window.localStorage?.getItem(CREDITS_BALANCE) === rewardStr) return true;
    return false;
  } catch {
    return false;
  }
}

function App() {
  const [, setWelcomeClaimed] = useState(false);
  const [hasClaimed, setHasClaimed] = useState(() => hasClaimedWelcome());
  const [activeTab, setActiveTab] = useState('ROBO_Radar');
  const [navigationDestination, setNavigationDestination] = useState(null);

  // Load Google Maps script once at app level so it stays loaded when switching tabs
  const { isLoaded: isMapScriptLoaded, loadError: mapScriptLoadError } = useLoadScript({
    googleMapsApiKey: GOOGLE_MAPS_API_KEY,
    preventGoogleFontsLoading: true,
  });

  const [userId, setUserId] = useState(() => {
    try {
      return window.localStorage?.getItem(USER_KEY) || null;
    } catch {
      return null;
    }
  });

  const refreshClaimed = () => {
    const claimed = hasClaimedWelcome();
    setWelcomeClaimed(claimed);
    setHasClaimed(claimed);
  };

  useEffect(() => {
    try {
      const params = new URLSearchParams(window.location.search);
      const ref = params.get('ref');
      if (ref) localStorage.setItem('bili_referral_code', ref.trim());
      refreshClaimed();
      setActiveTab(hasClaimedWelcome() ? 'Store_Tab' : 'ROBO_Radar');
      const uid = window.localStorage?.getItem(USER_KEY) || null;
      setUserId(uid);
    } catch {
      // ignore
    }
  }, []);

  useEffect(() => {
    const onCreditsChanged = () => refreshClaimed();
    window.addEventListener('bili_credits_changed', onCreditsChanged);
    return () => window.removeEventListener('bili_credits_changed', onCreditsChanged);
  }, []);

  useEffect(() => {
    const onNavigateTo = (e) => {
      const { lat, lng, name } = e.detail || {};
      if (lat != null && lng != null) {
        setNavigationDestination({ lat, lng, name: name || 'Store' });
        setActiveTab('Map_Tab');
      }
    };
    window.addEventListener('bili_navigate_to', onNavigateTo);
    return () => window.removeEventListener('bili_navigate_to', onNavigateTo);
  }, []);

  const handleWelcomeClaimSuccess = (data) => {
    setWelcomeClaimed(true);
    if (data?.user_id) setUserId(String(data.user_id));
    try {
      window.localStorage.setItem(WELCOME_KEY, '1');
      if (data?.user_id) window.localStorage.setItem(USER_KEY, String(data.user_id));
      window.localStorage.setItem('bili_credits_claimed', String(appConfig.claimReward));
      window.localStorage.setItem('bili_credits_balance', String(appConfig.claimReward));
      if (data?.referral_code) window.localStorage.setItem('bili_my_referral_code', data.referral_code);
    } catch {
      // ignore storage errors
    }
    window.dispatchEvent(new CustomEvent('bili_credits_changed'));
    window.dispatchEvent(new CustomEvent('bili_show_add_to_home'));
    setActiveTab('Store_Tab');
  };

  return (
    <div className="App app-clean-v1">
      <AddToHomeScreenPrompt />
      <TopCounter onClaimSuccess={() => {}} />

      <header className="app-header-clean">
        <h1>BILI</h1>
        <p>Permanent Guest • BILI_CLEAN_V1</p>
        <button
          type="button"
          className="app-header-install"
          onClick={() => window.dispatchEvent(new CustomEvent('bili_show_add_to_home', { detail: { force: true } }))}
        >
          Add to Home Screen / Install app
        </button>
      </header>

      <nav className="app-tabs">
        <button
          type="button"
          className={`app-tab ${activeTab === 'ROBO_Radar' ? 'app-tab--active' : ''}`}
          onClick={() => setActiveTab('ROBO_Radar')}
        >
          ROBO_Radar
        </button>
        <button
          type="button"
          className={`app-tab ${activeTab === 'Store_Tab' ? 'app-tab--active' : ''}`}
          onClick={() => setActiveTab('Store_Tab')}
        >
          Store / محل
        </button>
        <button
          type="button"
          className={`app-tab ${activeTab === 'Map_Tab' ? 'app-tab--active' : ''}`}
          onClick={() => setActiveTab('Map_Tab')}
        >
          Map
        </button>
        <button
          type="button"
          className={`app-tab ${activeTab === 'Profile_Tab' ? 'app-tab--active' : ''}`}
          onClick={() => setActiveTab('Profile_Tab')}
        >
          Profile
        </button>
        <button
          type="button"
          className={`app-tab ${activeTab === 'Admin_Tab' ? 'app-tab--active' : ''}`}
          onClick={() => setActiveTab('Admin_Tab')}
        >
          Admin
        </button>
      </nav>

      <main className="app-main-clean">
        {activeTab === 'ROBO_Radar' && (
          <section className="tab-panel">
            <h2>ROBO_Radar</h2>
            <p>Nearby and activity — tap the coin above to claim {appConfig.claimReward} Habbet.</p>
            {!hasClaimed ? (
              <ClaimButton
                userId={userId}
                isGuest={!userId}
                onClaimSuccess={handleWelcomeClaimSuccess}
              />
            ) : (
              <div className="tab-panel__section robo-radar-claimed">
                <p className="robo-radar-claimed-msg">You’ve already claimed your {appConfig.claimReward} Habbet. Check your balance in the top corner or in Profile.</p>
              </div>
            )}
            <div className="tab-panel__section radar-list">
              <h3>Nearby & activity</h3>
              <ul className="radar-list__list">
                {appConfig.radarDemoItems.map((item) => (
                  <li key={item.id} className="radar-list__item">
                    <span className="radar-list__title">{item.title}</span>
                    <span className="radar-list__subtitle">{item.subtitle}</span>
                  </li>
                ))}
              </ul>
            </div>
          </section>
        )}
        {activeTab === 'Store_Tab' && (
          <section className="tab-panel">
            <h2>Store / محل</h2>
            <StoreFeed />
          </section>
        )}
        {activeTab === 'Map_Tab' && (
          <section className="tab-panel">
            <h2>Map</h2>
            <BiliMap
              initialDestination={navigationDestination}
              onClearNavigation={() => setNavigationDestination(null)}
              isScriptLoaded={isMapScriptLoaded}
              scriptLoadError={mapScriptLoadError}
            />
          </section>
        )}
        {activeTab === 'Profile_Tab' && (
          <section className="tab-panel">
            <h2>Profile</h2>
            <WalletPanel />
          </section>
        )}
        {activeTab === 'Admin_Tab' && (
          <section className="tab-panel">
            <AdminPanel />
          </section>
        )}
      </main>
    </div>
  );
}

export default App;
