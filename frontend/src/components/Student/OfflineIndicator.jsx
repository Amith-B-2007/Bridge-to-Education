import { useState, useEffect } from 'react';
import { offlineManager } from '../../utils/offline';
import db from '../../utils/db';

export function OfflineIndicator() {
  const [isOnline, setIsOnline] = useState(navigator.onLine);
  const [pendingActions, setPendingActions] = useState(0);

  useEffect(() => {
    offlineManager.addListener(setIsOnline);
    const countPending = async () => {
      try {
        const actions = await db.getPendingActions();
        setPendingActions(actions.length);
      } catch (e) { /* ignore */ }
    };
    countPending();
    const interval = setInterval(countPending, 2000);
    return () => clearInterval(interval);
  }, []);

  if (isOnline && pendingActions === 0) return null;

  const offlineStyle = {
    position: 'fixed',
    top: 16,
    right: 16,
    zIndex: 50,
    background: isOnline ? '#dcfce7' : '#fee2e2',
    borderLeft: `4px solid ${isOnline ? '#16a34a' : '#dc2626'}`,
    padding: '12px 16px',
    borderRadius: 8,
    boxShadow: '0 8px 20px rgba(15, 52, 96, 0.15)',
    minWidth: 200,
  };

  return (
    <div style={offlineStyle}>
      <p style={{
        fontSize: 13,
        fontWeight: 700,
        color: isOnline ? '#15803d' : '#991b1b',
        display: 'flex',
        alignItems: 'center',
        gap: 6,
      }}>
        <span style={{
          width: 8,
          height: 8,
          borderRadius: '50%',
          background: isOnline ? '#16a34a' : '#dc2626',
          display: 'inline-block',
        }} />
        {isOnline ? 'Online' : 'Offline Mode'}
      </p>
      {pendingActions > 0 && (
        <p style={{ fontSize: 12, color: '#475569', marginTop: 4 }}>
          {pendingActions} action(s) pending sync
        </p>
      )}
      {!isOnline && pendingActions === 0 && (
        <p style={{ fontSize: 12, color: '#475569', marginTop: 4 }}>
          Cached content still available
        </p>
      )}
    </div>
  );
}
