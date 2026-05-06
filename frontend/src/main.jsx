import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.jsx'
import './index.css'
import db from './utils/db'

// Initialize IndexedDB on app start
db.init()
  .then(() => console.log('IndexedDB initialized'))
  .catch(err => console.error('Failed to init IndexedDB:', err));

// Register Service Worker
if ('serviceWorker' in navigator) {
  navigator.serviceWorker.register('/service-worker.js')
    .then(reg => {
      console.log('Service Worker registered');
      // Check for updates periodically
      setInterval(() => reg.update(), 60000);
    })
    .catch(err => console.error('Service Worker registration failed:', err));
}

// Listen for sync messages from Service Worker
if ('serviceWorker' in navigator) {
  navigator.serviceWorker.addEventListener('message', event => {
    if (event.data.type === 'SYNC_PENDING_ACTIONS') {
      console.log('Syncing pending actions');
      // Will be handled by OfflineManager
    }
  });
}

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
