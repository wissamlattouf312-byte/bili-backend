/**
 * BILI Master System - User Dashboard Component
 * [cite: 2026-02-09]
 * 
 * Displays user wallet, credits, and USDT sweep status
 * Shows Bybit withdrawal information
 */
import React, { useState, useEffect } from 'react';
import './UserDashboard.css';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const UserDashboard = ({ userId }) => {
  const [walletData, setWalletData] = useState(null);
  const [withdrawalHistory, setWithdrawalHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (userId) {
      loadWalletData();
      loadWithdrawalHistory();
      
      // Refresh every 30 seconds
      const interval = setInterval(() => {
        loadWalletData();
      }, 30000);
      
      return () => clearInterval(interval);
    }
  }, [userId]);

  const loadWalletData = async () => {
    if (!userId) {
      setLoading(false);
      return;
    }
    
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 5000);
      
      const response = await fetch(`${API_BASE_URL}/api/v1/wallet/balance/${userId}`, {
        signal: controller.signal
      });
      
      clearTimeout(timeoutId);
      
      if (response.ok) {
        const data = await response.json();
        setWalletData(data);
        setError(null);
      } else {
        throw new Error('Failed to load wallet data');
      }
    } catch (err) {
      if (err.name !== 'AbortError') {
        setError('Unable to load wallet data. Backend may be starting.');
      }
    } finally {
      setLoading(false);
    }
  };

  const loadWithdrawalHistory = async () => {
    if (!userId) return;
    
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 5000);
      
      const response = await fetch(`${API_BASE_URL}/api/v1/wallet/withdrawal-history/${userId}`, {
        signal: controller.signal
      });
      
      clearTimeout(timeoutId);
      
      if (response.ok) {
        const data = await response.json();
        setWithdrawalHistory(data.withdrawals || []);
      }
    } catch (err) {
      // Silently fail - not critical
    }
  };

  if (loading) {
    return (
      <div className="user-dashboard-container">
        <div className="loading">Loading wallet data...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="user-dashboard-container">
        <div className="error-message">{error}</div>
      </div>
    );
  }

  if (!walletData) {
    return null;
  }

  const { 
    credits_balance, 
    usdt_balance, 
    withdrawal_threshold_usd,
    eligible_for_withdrawal,
    withdrawal_processed,
    withdrawal_message
  } = walletData;

  const progressToThreshold = Math.min((usdt_balance / withdrawal_threshold_usd) * 100, 100);
  const remainingToThreshold = Math.max(0, withdrawal_threshold_usd - usdt_balance);

  return (
    <div className="user-dashboard-container">
      <div className="dashboard-header">
        <h2>💰 Wallet Dashboard</h2>
      </div>

      <div className="wallet-cards">
        {/* Credits Balance Card */}
        <div className="wallet-card credits-card">
          <div className="card-icon">🎁</div>
          <div className="card-content">
            <div className="card-label">Habbet Credits</div>
            <div className="card-value">{credits_balance.toFixed(2)}</div>
            <div className="card-subtitle">Available Credits</div>
          </div>
        </div>

        {/* USDT Balance Card */}
        <div className="wallet-card usdt-card">
          <div className="card-icon">💵</div>
          <div className="card-content">
            <div className="card-label">USDT Value</div>
            <div className="card-value">${usdt_balance.toFixed(2)}</div>
            <div className="card-subtitle">Current Balance</div>
          </div>
        </div>
      </div>

      {/* USDT Sweep Status Section */}
      <div className="sweep-status-section">
        <h3>🚀 Bybit USDT Sweep Status</h3>
        
        <div className="sweep-info">
          <div className="sweep-threshold">
            <span className="threshold-label">Withdrawal Threshold:</span>
            <span className="threshold-value">${withdrawal_threshold_usd}</span>
          </div>

          <div className="progress-container">
            <div className="progress-bar">
              <div 
                className="progress-fill" 
                style={{ width: `${progressToThreshold}%` }}
              ></div>
            </div>
            <div className="progress-text">
              {usdt_balance.toFixed(2)} / {withdrawal_threshold_usd} USDT
            </div>
          </div>

          {eligible_for_withdrawal ? (
            <div className="sweep-status eligible">
              <div className="status-icon">✅</div>
              <div className="status-content">
                <div className="status-title">Eligible for Automatic Withdrawal</div>
                <div className="status-message">
                  {withdrawal_processed 
                    ? `Withdrawal processed: ${withdrawal_message || 'Success'}`
                    : 'Your balance has reached $50. Automatic withdrawal will be processed soon.'}
                </div>
              </div>
            </div>
          ) : (
            <div className="sweep-status pending">
              <div className="status-icon">⏳</div>
              <div className="status-content">
                <div className="status-title">Pending Automatic Withdrawal</div>
                <div className="status-message">
                  You need ${remainingToThreshold.toFixed(2)} more to reach the ${withdrawal_threshold_usd} threshold.
                  Once reached, your USDT will be automatically sent to your Bybit wallet.
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Withdrawal History */}
      {withdrawalHistory.length > 0 && (
        <div className="withdrawal-history">
          <h3>📜 Withdrawal History</h3>
          <div className="history-list">
            {withdrawalHistory.map((withdrawal, index) => (
              <div key={index} className="history-item">
                <div className="history-amount">-${withdrawal.amount_usdt.toFixed(2)} USDT</div>
                <div className="history-date">
                  {new Date(withdrawal.timestamp).toLocaleDateString()}
                </div>
                <div className="history-status">✓ Completed</div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default UserDashboard;
