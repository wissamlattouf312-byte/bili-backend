import React, { useEffect, useState } from 'react';
import { appConfig } from '../appConfig';

const CLAIM_STORAGE_KEY = 'bili_credits_claimed';
const BALANCE_KEY = 'bili_credits_balance';
const MY_REFERRAL_KEY = 'bili_my_referral_code';
const DEVICE_ID_KEY = 'bili_device_id';

function getOrCreateReferralCode() {
  try {
    let code = window.localStorage?.getItem(MY_REFERRAL_KEY);
    if (code) return code;
    const deviceId = window.localStorage?.getItem(DEVICE_ID_KEY);
    const raw = deviceId || `local_${Date.now()}_${Math.random().toString(36).slice(2, 10)}`;
    code = 'L' + raw.replace(/\W/g, '').slice(-8).toUpperCase() || 'L' + Math.random().toString(36).slice(2, 10).toUpperCase();
    if (code.length < 4) code = 'L' + Math.random().toString(36).slice(2, 10).toUpperCase();
    window.localStorage.setItem(MY_REFERRAL_KEY, code);
    return code;
  } catch {
    return '';
  }
}

export default function WalletPanel() {
  const [balance, setBalance] = useState(0);
  const [ledger, setLedger] = useState([]);
  const [myReferralCode, setMyReferralCode] = useState('');
  const [copyFeedback, setCopyFeedback] = useState(false);

  const refreshFromStorage = () => {
    try {
      const reward = appConfig.claimReward;
      const rewardStr = String(reward);
      const claimed = window.localStorage?.getItem(CLAIM_STORAGE_KEY) === rewardStr;
      const bal = window.localStorage?.getItem(BALANCE_KEY);
      const numBalance = bal === rewardStr ? reward : claimed ? reward : 0;
      if (numBalance >= reward || claimed) {
        setBalance(numBalance >= reward ? numBalance : reward);
        setLedger([
          {
            id: 'demo-ledger-1',
            entry_type: 'credit',
            amount: reward,
            balance_before: 0,
            balance_after: reward,
            description: `Welcome Reward – ${reward} Habbet`,
            timestamp: new Date().toISOString(),
          },
        ]);
        const stored = window.localStorage?.getItem(MY_REFERRAL_KEY);
        setMyReferralCode(stored || getOrCreateReferralCode());
      } else {
        setBalance(0);
        setLedger([]);
        setMyReferralCode(window.localStorage?.getItem(MY_REFERRAL_KEY) || '');
      }
    } catch {
      setBalance(0);
      setLedger([]);
      setMyReferralCode('');
    }
  };

  useEffect(() => {
    refreshFromStorage();
    const onCreditsChanged = () => refreshFromStorage();
    window.addEventListener('bili_credits_changed', onCreditsChanged);
    return () => window.removeEventListener('bili_credits_changed', onCreditsChanged);
  }, []);

  const referralLink = myReferralCode
    ? `${window.location.origin}${window.location.pathname}${window.location.search ? window.location.search + '&' : '?'}ref=${encodeURIComponent(myReferralCode)}`
    : '';

  const handleCopyReferral = () => {
    if (!referralLink) return;
    try {
      navigator.clipboard.writeText(referralLink);
      setCopyFeedback(true);
      setTimeout(() => setCopyFeedback(false), 2000);
    } catch {
      setCopyFeedback(false);
    }
  };

  return (
    <div className="wallet">
      <div className="wallet__header">
        <div>
          <div className="wallet__label">Current Balance</div>
          <div className="wallet__balance">{balance.toFixed(2)} Habbet</div>
        </div>
        <div className="wallet__hospitality">
          <div className="wallet__label">Royal Hospitality</div>
          <div className="wallet__hospitality-status">{appConfig.royalHospitalityDays} days from claim</div>
        </div>
      </div>

      <button
        type="button"
        className="wallet__add-to-home"
        onClick={() => window.dispatchEvent(new CustomEvent('bili_show_add_to_home', { detail: { force: true } }))}
      >
        Add BILI to Home Screen
      </button>

      <div className="wallet__referral">
        <h3>Your referral link</h3>
        {myReferralCode ? (
          <>
            <p className="wallet__referral-hint">Share this link. You earn {appConfig.referralReward} Habbet when someone new claims {appConfig.claimReward} Habbet.</p>
            <div className="wallet__referral-row">
              <input
                type="text"
                readOnly
                value={referralLink}
                className="wallet__referral-input"
                aria-label="Referral link"
              />
              <button type="button" className="wallet__referral-copy" onClick={handleCopyReferral}>
                {copyFeedback ? 'Copied!' : 'Copy'}
              </button>
            </div>
          </>
        ) : (
          <p className="wallet__referral-empty">Claim {appConfig.claimReward} Habbet in ROBO_Radar to get your personal referral link and earn {appConfig.referralReward} Habbet per new member.</p>
        )}
      </div>

      <div className="wallet__ledger">
        <h3>Credits Ledger</h3>
        {ledger.length === 0 ? (
          <p className="wallet__status">No ledger entries yet.</p>
        ) : (
          <ul className="wallet__ledger-list">
            {ledger.map((entry) => (
              <li key={entry.id} className="wallet__ledger-item">
                <div className="wallet__ledger-main">
                  <span className="wallet__ledger-amount">
                    {entry.entry_type === 'credit' ? '+' : '-'}
                    {entry.amount.toFixed(2)}
                  </span>
                  <span className="wallet__ledger-desc">{entry.description}</span>
                </div>
                <div className="wallet__ledger-meta">
                  <span>{new Date(entry.timestamp).toLocaleString()}</span>
                  <span>{entry.balance_before.toFixed(2)} → {entry.balance_after.toFixed(2)}</span>
                </div>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}

