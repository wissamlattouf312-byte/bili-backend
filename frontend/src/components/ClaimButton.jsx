import React, { useState } from 'react';
import './ClaimButton.css';
import { appConfig } from '../appConfig';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const ClaimButton = ({ userId, isGuest = true, onClaimSuccess }) => {
  const [isClaiming, setIsClaiming] = useState(false);
  const [error, setError] = useState(null);

  const applyLocalClaim = () => {
    const reward = appConfig.claimReward;
    try {
      localStorage.setItem('bili_credits_claimed', String(reward));
      localStorage.setItem('bili_credits_balance', String(reward));
      window.dispatchEvent(new CustomEvent('bili_credits_changed'));
    } catch (e) {
      // ignore
    }
    onClaimSuccess?.({ credit_balance: reward, user_id: null });
  };

  const handleClaim = async () => {
    setIsClaiming(true);
    setError(null);

    try {
      let device_id = localStorage.getItem('bili_device_id');
      if (!device_id) {
        device_id = `device_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
        localStorage.setItem('bili_device_id', device_id);
      }

      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 10000);

      const response = await fetch(`${API_BASE_URL}/api/v1/claim/reward`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          device_id: device_id,
          phone_number: null,
          latitude: null,
          longitude: null,
          referral_code: localStorage.getItem('bili_referral_code') || undefined,
        }),
        signal: controller.signal
      });

      clearTimeout(timeoutId);

      if (!response.ok) {
        let errorMessage = 'Failed to claim reward';
        try {
          const errorData = await response.json();
          errorMessage = errorData.detail || errorData.message || errorMessage;
        } catch (e) {
          errorMessage = response.statusText || errorMessage;
        }
        throw new Error(errorMessage);
      }

      const data = await response.json();

      if (data.user_id) {
        try {
          localStorage.setItem('bili_user_id', data.user_id);
        } catch {
          // ignore
        }
      }

      const creditsAwarded = data.credit_balance ?? appConfig.claimReward;
      let msg = `Success! You've been awarded ${creditsAwarded} Habbet!\n\nRoyal Hospitality Period: 30 days!\n\nYou are now an Active Member!`;
      if (data.referral_code) {
        const shareUrl = `${window.location.origin}${window.location.pathname}?ref=${encodeURIComponent(data.referral_code)}`;
        msg += `\n\nShare your link (5 Habbet per new member):\n${shareUrl}`;
      }
      alert(msg);

      if (onClaimSuccess) {
        onClaimSuccess(data);
      }
    } catch (err) {
      applyLocalClaim();
      setError(null);
    } finally {
      setIsClaiming(false);
    }
  };

  return (
    <div className="claim-button-container prominent">
      <div className="claim-button-label">Welcome Reward</div>
      <button
        className="claim-button flashing"
        onClick={handleClaim}
        disabled={isClaiming}
      >
        {isClaiming ? 'Claiming...' : `${appConfig.claimReward} حبة`}
      </button>
      <div className="claim-button-subtitle">Available at any time • Instant registration</div>
      {error && <div className="claim-error">{error}</div>}
    </div>
  );
};

export default ClaimButton;
