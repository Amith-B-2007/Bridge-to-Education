import api from './api';
import db from './db';

export class OfflineManager {
  constructor() {
    this.isOnline = navigator.onLine;
    this.listeners = [];

    window.addEventListener('online', () => this.setOnline(true));
    window.addEventListener('offline', () => this.setOnline(false));
  }

  setOnline(status) {
    this.isOnline = status;
    this.notifyListeners();
    if (status) {
      this.syncPendingActions();
    }
  }

  addListener(callback) {
    this.listeners.push(callback);
  }

  notifyListeners() {
    this.listeners.forEach(cb => cb(this.isOnline));
  }

  async syncPendingActions() {
    const actions = await db.getPendingActions();

    for (const action of actions) {
      try {
        if (action.type === 'quiz_submit') {
          await api.post(action.endpoint, action.payload);
          await db.clearPendingAction(action.id);
        }
      } catch (error) {
        console.log('Sync failed:', error);
        action.retries = (action.retries || 0) + 1;
        await db.updatePendingAction(action.id, { retries: action.retries });
      }
    }
  }

  getPendingCount() {
    return db.getPendingActions().then(actions => actions.length);
  }
}

export const offlineManager = new OfflineManager();
