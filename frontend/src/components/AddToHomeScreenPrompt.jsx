import React, { useState, useEffect } from 'react';
import './AddToHomeScreenPrompt.css';

const DISMISS_KEY = 'bili_add_to_home_prompt_dismissed';
const EVENT_SHOW = 'bili_show_add_to_home';

function isStandalone() {
  if (typeof window === 'undefined') return false;
  return (
    window.matchMedia('(display-mode: standalone)').matches ||
    window.navigator.standalone === true ||
    document.referrer.includes('android-app://')
  );
}

export default function AddToHomeScreenPrompt() {
  const [visible, setVisible] = useState(false);
  const [installPrompt, setInstallPrompt] = useState(null);
  const [installing, setInstalling] = useState(false);
  const [desktopFallback, setDesktopFallback] = useState(false);

  useEffect(() => {
    const onShow = (e) => {
      if (isStandalone()) return;
      const force = e?.detail?.force === true;
      try {
        if (!force && localStorage.getItem(DISMISS_KEY) === '1') return;
      } catch {
        // ignore
      }
      setDesktopFallback(false);
      setVisible(true);
    };
    window.addEventListener(EVENT_SHOW, onShow);
    return () => window.removeEventListener(EVENT_SHOW, onShow);
  }, []);

  useEffect(() => {
    const handler = (e) => {
      e.preventDefault();
      setInstallPrompt(e);
    };
    window.addEventListener('beforeinstallprompt', handler);
    return () => window.removeEventListener('beforeinstallprompt', handler);
  }, []);

  const handleDismiss = () => {
    try {
      localStorage.setItem(DISMISS_KEY, '1');
    } catch {
      // ignore
    }
    setDesktopFallback(false);
    setVisible(false);
  };

  const handleAddToHome = async () => {
    if (installPrompt) {
      setInstalling(true);
      try {
        await installPrompt.prompt();
        const { outcome } = await installPrompt.userChoice;
        if (outcome === 'accepted') {
          setInstallPrompt(null);
          handleDismiss();
        }
      } catch {
        // ignore
      }
      setInstalling(false);
      return;
    }
    if (typeof navigator !== 'undefined' && navigator.share) {
      try {
        await navigator.share({
          url: window.location.href,
          title: 'BILI',
          text: 'BILI Master System',
        });
        handleDismiss();
      } catch (err) {
        if (err?.name !== 'AbortError') {
          // User cancelled or share failed; ignore
        }
      }
      return;
    }
    setDesktopFallback(true);
  };

  if (!visible) return null;

  const canInstallNative = Boolean(installPrompt);

  return (
    <div className="add-to-home-overlay" role="dialog" aria-labelledby="add-to-home-title" aria-modal="true">
      <div className="add-to-home-backdrop" onClick={handleDismiss} aria-hidden="true" />
      <div className="add-to-home-card">
        <h2 id="add-to-home-title" className="add-to-home-title">Add BILI to your home screen</h2>
        {canInstallNative ? (
          <p className="add-to-home-subtitle">
            One tap adds BILI to your home screen like an app — no menu needed.
          </p>
        ) : !desktopFallback ? (
          <p className="add-to-home-subtitle">
            Tap the button below. Then choose <strong>Add to Home Screen</strong> in the menu that appears.
          </p>
        ) : null}
        {desktopFallback && (
          <p className="add-to-home-desktop-fallback">
            Use the <strong>Install</strong> icon (⊕) in your browser&apos;s address bar, or open this site in Chrome/Edge and refresh.
          </p>
        )}
        <button
          type="button"
          className="add-to-home-primary"
          onClick={handleAddToHome}
          disabled={installing}
        >
          {installing ? 'Opening…' : 'Add to Home Screen'}
        </button>
        <button type="button" className="add-to-home-dismiss" onClick={handleDismiss}>
          Not now
        </button>
      </div>
    </div>
  );
}
