import { messaging } from '../config/firebaseConfig';
import { getToken, onMessage } from 'firebase/messaging';

// Get FCM token for push notifications
export const getFCMToken = async () => {
  try {
    if (!messaging) {
      console.warn('Cloud Messaging not supported in this browser');
      return null;
    }

    const token = await getToken(messaging, {
      vapidKey: import.meta.env.VITE_FIREBASE_VAPID_KEY || '',
    });

    if (token) {
      console.log('FCM Token:', token);
      // Save token to database for later use
      localStorage.setItem('fcmToken', token);
      return token;
    } else {
      console.log('No FCM token available');
      return null;
    }
  } catch (error) {
    console.error('Error getting FCM token:', error);
    return null;
  }
};

// Listen for incoming messages
export const listenForMessages = (callback) => {
  if (!messaging) {
    console.warn('Cloud Messaging not supported');
    return;
  }

  onMessage(messaging, (payload) => {
    console.log('Message received:', payload);
    callback(payload);

    // Show browser notification
    if ('Notification' in window && Notification.permission === 'granted') {
      new Notification(payload.notification?.title || 'New Message', {
        body: payload.notification?.body,
        icon: payload.notification?.image,
        badge: payload.notification?.badge,
      });
    }
  });
};

// Request notification permission
export const requestNotificationPermission = async () => {
  try {
    if (!('Notification' in window)) {
      console.log('Notifications not supported');
      return false;
    }

    if (Notification.permission === 'granted') {
      return true;
    }

    if (Notification.permission !== 'denied') {
      const permission = await Notification.requestPermission();
      return permission === 'granted';
    }

    return false;
  } catch (error) {
    console.error('Error requesting notification permission:', error);
    return false;
  }
};

// Send test notification
export const sendTestNotification = (title, body) => {
  if ('Notification' in window && Notification.permission === 'granted') {
    new Notification(title, {
      body: body,
      icon: '/notification-icon.png',
    });
  }
};
