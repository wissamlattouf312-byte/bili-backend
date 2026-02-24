import React, { useState, useEffect } from 'react';
import './TopCounter.css';
import { appConfig } from '../appConfig';

const STORAGE_KEY_CLAIMED = 'bili_credits_claimed';
const STORAGE_KEY_BALANCE = 'bili_credits_balance';

export default function TopCounter({ onClaimSuccess }) {
  const [balance, setBalance] = useState(0);
  const [claimed, setClaimed] = useState(false);
  const [toast, setToast] = useState(null);

  useEffect(() => {
    const reward = appConfig.claimReward;
    const savedBalance = localStorage.getItem(STORAGE_KEY_BALANCE);
    const savedClaimed = localStorage.getItem(STORAGE_KEY_CLAIMED);
    if (savedBalance === String(reward) || savedClaimed === String(reward)) {
      setBalance(reward);
      setClaimed(true);
      if (savedBalance !== String(reward)) {
        localStorage.setItem(STORAGE_KEY_BALANCE, String(reward));
      }
    }
  }, []);

  const handleClaim = () => {
    const reward = appConfig.claimReward;
    if (claimed || balance >= reward) return;

    setBalance(reward);
    setClaimed(true);
    localStorage.setItem(STORAGE_KEY_CLAIMED, String(reward));
    localStorage.setItem(STORAGE_KEY_BALANCE, String(reward));
    onClaimSuccess?.({ credit_balance: reward });
    window.dispatchEvent(new CustomEvent('bili_credits_changed'));
    window.dispatchEvent(new CustomEvent('bili_show_add_to_home'));
    setToast(`${reward} Habbet added!`);
    setTimeout(() => setToast(null), 2000);
  };

  const handleSendToZero = () => {
    const reward = appConfig.claimReward;
    if (balance < reward) return;

    setBalance(0);
    setClaimed(false);
    localStorage.setItem(STORAGE_KEY_BALANCE, '0');
    localStorage.setItem(STORAGE_KEY_CLAIMED, '0');
    window.dispatchEvent(new CustomEvent('bili_credits_changed'));
  };

  return (
    <div className="top-counter-wrap">
      {toast && <div className="top-counter__toast" role="status">{toast}</div>}
      <div
        className={`top-counter ${balance === 0 ? 'top-counter--flash' : ''}`}
        onClick={balance === 0 ? handleClaim : undefined}
        role={balance === 0 ? 'button' : 'none'}
        aria-label={balance === 0 ? `Claim ${appConfig.claimReward} tokens` : 'Balance'}
      >
        <span className="top-counter__icon">🪙</span>
        <span className="top-counter__value">{balance}</span>
      </div>
      {balance >= appConfig.claimReward && (
        <button
          type="button"
          className="top-counter__send"
          onClick={handleSendToZero}
          aria-label={`Send ${appConfig.claimReward} points to zero`}
          title={`إرسال ${appConfig.claimReward} → صفر`}
        >
          <span className="top-counter__send-icon" aria-hidden>📤</span>
          <span className="top-counter__send-label">0</span>
        </button>
      )}
    </div>
  );
}
