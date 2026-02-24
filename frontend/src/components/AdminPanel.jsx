import React, { useState, useEffect } from 'react';
import './AdminPanel.css';

const API_BASE = process.env.REACT_APP_API_URL || 'http://127.0.0.1:8000';
const ADMIN_TOKEN_KEY = 'bili_admin_token';

export default function AdminPanel() {
  const [token, setToken] = useState(() => window.localStorage?.getItem(ADMIN_TOKEN_KEY) || null);
  const [loginUsername, setLoginUsername] = useState('');
  const [loginPassword, setLoginPassword] = useState('');
  const [loginError, setLoginError] = useState(null);
  const [pins, setPins] = useState([]);
  const [pasteInput, setPasteInput] = useState('');
  const [pinName, setPinName] = useState('');
  const [profileUrl, setProfileUrl] = useState('');
  const [addStatus, setAddStatus] = useState(null);
  const [loading, setLoading] = useState(false);
  const [refreshingId, setRefreshingId] = useState(null);
  const [setupMessage, setSetupMessage] = useState(null);
  const [setupLoading, setSetupLoading] = useState(false);
  const [backendReachable, setBackendReachable] = useState(null);

  useEffect(() => {
    if (token) return;
    fetch(`${API_BASE}/api/v1/health`)
      .then((r) => r.ok && setBackendReachable(true))
      .catch(() => setBackendReachable(false));
  }, [token]);

  const fetchPins = () => {
    fetch(`${API_BASE}/api/v1/map/pins`)
      .then((r) => r.json())
      .then(setPins)
      .catch(() => setPins([]));
  };

  useEffect(() => {
    if (token) fetchPins();
  }, [token]);

  const handleLogin = (e) => {
    e.preventDefault();
    setLoginError(null);
    const user = (loginUsername || '').trim();
    const pass = (loginPassword || '').trim();
    if (!user || !pass) {
      setLoginError('Enter username and password.');
      return;
    }
    setLoading(true);
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 15000);
    fetch(`${API_BASE}/api/v1/admin/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username: user, password: pass }),
      signal: controller.signal,
    })
      .then((r) => {
        if (!r.ok && r.status >= 500) throw new Error('Server error');
        return r.json().catch(() => ({}));
      })
      .then((data) => {
        if (data.token) {
          window.localStorage.setItem(ADMIN_TOKEN_KEY, data.token);
          setToken(data.token);
          setLoginUsername('');
          setLoginPassword('');
        } else {
          setLoginError(data.detail || Array.isArray(data.detail) ? data.detail[0]?.msg || data.detail : 'Login failed');
        }
      })
      .catch((err) => {
        clearTimeout(timeoutId);
        const msg = err && err.message;
        if (err.name === 'AbortError') {
          setLoginError('Request timed out. Is the backend running? Start it: cd bili then python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000');
        } else if (msg === 'Failed to fetch' || msg === 'Load failed' || msg === 'NetworkError when attempting to fetch resource') {
          setLoginError('Cannot reach server. Start the backend: in bili folder run "python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000"');
        } else if (msg === 'Server error') {
          setLoginError('Server error. Check backend terminal for errors.');
        } else {
          setLoginError(msg || 'Network error');
        }
      })
      .finally(() => {
        clearTimeout(timeoutId);
        setLoading(false);
      });
  };

  const handleLogout = () => {
    window.localStorage.removeItem(ADMIN_TOKEN_KEY);
    setToken(null);
  };

  const handleCreateAdmin = () => {
    setSetupMessage(null);
    setSetupLoading(true);
    fetch(`${API_BASE}/api/v1/admin/setup`, { method: 'POST' })
      .then((r) => {
        return r.json().catch(() => ({})).then((data) => ({ ok: r.ok, status: r.status, data }));
      })
      .then(({ ok, status, data }) => {
        if (ok && data.created) {
          setSetupMessage(`Admin created. Log in with username: ${data.username}, password: ${data.password_hint || 'admin123'}.`);
          setLoginError(null);
          return;
        }
        const detail = typeof data.detail === 'string' ? data.detail : (Array.isArray(data.detail) ? data.detail[0]?.msg || JSON.stringify(data.detail) : null);
        if (status === 400 && detail && detail.includes('already exists')) {
          setSetupMessage('An admin user already exists. Log in with username: admin@bili.local, password: admin123.');
          setLoginError(null);
        } else if (status === 503 || (status >= 500 && detail && detail.includes('Database'))) {
          setSetupMessage(detail || 'Database unavailable. Start PostgreSQL, or check DATABASE_URL in bili/.env');
        } else if (status >= 500) {
          setSetupMessage(detail || 'Server error. Is PostgreSQL running? Start the database, then try again.');
        } else {
          setSetupMessage(detail || 'Setup failed.');
        }
      })
      .catch(() => setSetupMessage('Cannot reach server. Start the backend (uvicorn) first, then try again.'))
      .finally(() => setSetupLoading(false));
  };

  const handleAddPin = (e) => {
    e.preventDefault();
    if (!pasteInput.trim()) return;
    setAddStatus(null);
    setLoading(true);
    fetch(`${API_BASE}/api/v1/admin/map-pins`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({
        coordinates_or_url: pasteInput.trim(),
        name: pinName.trim() || undefined,
        profile_url: profileUrl.trim() || undefined,
      }),
    })
      .then((r) => {
        if (r.status === 401 || r.status === 403) {
          window.localStorage.removeItem(ADMIN_TOKEN_KEY);
          setToken(null);
          throw new Error('Session expired. Please log in again.');
        }
        return r.json();
      })
      .then((data) => {
        if (data.success) {
          setPasteInput('');
          setPinName('');
          setProfileUrl('');
          setAddStatus(
            data.pin?.latest_content_title
              ? 'Pin added. Latest content fetched; pins refresh automatically every 30 min.'
              : 'Pin added. It appears on the map for all users.'
          );
          fetchPins();
          window.dispatchEvent(new CustomEvent('bili_map_pins_updated'));
        } else {
          const msg = Array.isArray(data.detail)
            ? data.detail.map((d) => d.msg || d).join(', ')
            : (data.detail || 'Failed to add pin');
          setAddStatus(msg);
        }
      })
      .catch(() => setAddStatus('Network error'))
      .finally(() => setLoading(false));
  };

  const handleDeletePin = (pinId) => {
    if (!window.confirm('Remove this pin from the map?')) return;
    setLoading(true);
    fetch(`${API_BASE}/api/v1/admin/map-pins/${pinId}`, {
      method: 'DELETE',
      headers: { Authorization: `Bearer ${token}` },
    })
      .then((r) => {
        if (r.status === 401 || r.status === 403) {
          window.localStorage.removeItem(ADMIN_TOKEN_KEY);
          setToken(null);
          return {};
        }
        return r.json();
      })
      .then((data) => {
        if (data.success) {
          fetchPins();
          window.dispatchEvent(new CustomEvent('bili_map_pins_updated'));
        }
      })
      .finally(() => setLoading(false));
  };

  const handleRefreshPin = (pinId) => {
    setRefreshingId(pinId);
    fetch(`${API_BASE}/api/v1/admin/map-pins/${pinId}/refresh`, {
      method: 'POST',
      headers: { Authorization: `Bearer ${token}` },
    })
      .then((r) => {
        if (r.status === 401 || r.status === 403) {
          window.localStorage.removeItem(ADMIN_TOKEN_KEY);
          setToken(null);
          return {};
        }
        return r.json();
      })
      .then((data) => {
        if (data.success) {
          fetchPins();
          window.dispatchEvent(new CustomEvent('bili_map_pins_updated'));
        }
      })
      .finally(() => setRefreshingId(null));
  };

  if (!token) {
    return (
      <div className="admin-panel">
        <h2>Admin</h2>
        {backendReachable === false && (
          <p className="admin-panel__error">
            Backend not reachable at {API_BASE}. Start it in a terminal: cd to the bili folder, then run: python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
          </p>
        )}
        {backendReachable === true && (
          <p className="admin-panel__success" style={{ marginBottom: 8 }}>Backend connected.</p>
        )}
        <p className="admin-panel__hint">Log in to add map pins (store locations).</p>
        <form className="admin-panel__login" onSubmit={handleLogin}>
          <input
            type="text"
            placeholder="Username / phone"
            value={loginUsername}
            onChange={(e) => setLoginUsername(e.target.value)}
            className="admin-panel__input"
          />
          <input
            type="password"
            placeholder="Password"
            value={loginPassword}
            onChange={(e) => setLoginPassword(e.target.value)}
            className="admin-panel__input"
          />
          {loginError && <p className="admin-panel__error">{loginError}</p>}
          {setupMessage && (
            <p className={setupMessage.includes('error') || setupMessage.includes('Cannot reach') ? 'admin-panel__error' : 'admin-panel__success'}>
              {setupMessage}
            </p>
          )}
          <button type="submit" className="admin-panel__btn" disabled={loading}>
            {loading ? 'Logging in…' : 'Log in'}
          </button>
        </form>
        <p className="admin-panel__hint" style={{ marginTop: 12 }}>
          First time? Create the default admin user, then log in with the credentials shown.
        </p>
        <button
          type="button"
          className="admin-panel__btn"
          onClick={handleCreateAdmin}
          disabled={setupLoading}
          style={{ marginTop: 4 }}
        >
          {setupLoading ? 'Creating…' : 'Create default admin user'}
        </button>
      </div>
    );
  }

  return (
    <div className="admin-panel">
      <div className="admin-panel__header">
        <h2>Admin</h2>
        <button type="button" className="admin-panel__logout" onClick={handleLogout}>
          Log out
        </button>
      </div>

      <section className="admin-panel__section">
        <h3>Map pins (store locations)</h3>
        <p className="admin-panel__hint">
          Paste coordinates or a Google Maps URL. Add a profile URL (e.g. YouTube channel) to show the store’s latest video/post; content refreshes automatically every 30 min.
        </p>
        <form className="admin-panel__add-pin" onSubmit={handleAddPin}>
          <textarea
            placeholder="Coordinates or map URL: 33.89, 35.51 or https://www.google.com/maps?q=33.89,35.51"
            value={pasteInput}
            onChange={(e) => setPasteInput(e.target.value)}
            className="admin-panel__textarea"
            rows={2}
          />
          <input
            type="text"
            placeholder="Store name (optional)"
            value={pinName}
            onChange={(e) => setPinName(e.target.value)}
            className="admin-panel__input"
          />
          <input
            type="url"
            placeholder="Profile URL for latest content (e.g. YouTube channel URL)"
            value={profileUrl}
            onChange={(e) => setProfileUrl(e.target.value)}
            className="admin-panel__input"
          />
          <button type="submit" className="admin-panel__btn" disabled={loading || !pasteInput.trim()}>
            Add pin
          </button>
        </form>
        {addStatus && (
          <p className={addStatus.startsWith('Pin added') ? 'admin-panel__success' : 'admin-panel__error'}>
            {addStatus}
          </p>
        )}

        <h4>Current pins</h4>
        <ul className="admin-panel__pin-list">
          {pins.length === 0 && <li className="admin-panel__pin-list-empty">No pins yet. Add one above.</li>}
          {pins.map((pin) => (
            <li key={pin.id} className="admin-panel__pin-item">
              <div className="admin-panel__pin-main">
                {pin.latest_content_thumbnail && (
                  <img
                    src={pin.latest_content_thumbnail}
                    alt=""
                    className="admin-panel__pin-thumb"
                  />
                )}
                <div className="admin-panel__pin-info">
                  <span className="admin-panel__pin-name">{pin.name}</span>
                  <span className="admin-panel__pin-coords">
                    {pin.latitude.toFixed(4)}, {pin.longitude.toFixed(4)}
                  </span>
                  {pin.profile_url && (
                    <span className="admin-panel__pin-profile">Profile: on</span>
                  )}
                  {pin.latest_content_title && (
                    <span className="admin-panel__pin-latest" title={pin.latest_content_title}>
                      Latest: {pin.latest_content_title.slice(0, 40)}
                      {pin.latest_content_title.length > 40 ? '…' : ''}
                    </span>
                  )}
                </div>
              </div>
              <div className="admin-panel__pin-actions">
                {pin.profile_url && (
                  <button
                    type="button"
                    className="admin-panel__pin-refresh"
                    onClick={() => handleRefreshPin(pin.id)}
                    disabled={loading || refreshingId === pin.id}
                    aria-label="Refresh latest content"
                  >
                    {refreshingId === pin.id ? '…' : 'Refresh'}
                  </button>
                )}
                <button
                  type="button"
                  className="admin-panel__pin-delete"
                  onClick={() => handleDeletePin(pin.id)}
                  disabled={loading}
                  aria-label="Remove pin"
                >
                  Remove
                </button>
              </div>
            </li>
          ))}
        </ul>
      </section>
    </div>
  );
}
