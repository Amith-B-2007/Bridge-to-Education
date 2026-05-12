import React, { createContext, useState, useEffect } from 'react';
import {
  onAuthChange,
  firebaseSignUp,
  firebaseSignIn,
  firebaseSignOut,
  getCurrentUser,
} from '../services/firebaseAuthService';
import { getFCMToken, requestNotificationPermission } from '../services/firebaseMessagingService';

export const FirebaseContext = createContext();

export const FirebaseProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    // Initialize auth listener
    const unsubscribe = onAuthChange((userData) => {
      setUser(userData);
      setLoading(false);
      if (userData) {
        localStorage.setItem('currentUser', JSON.stringify(userData));
      } else {
        localStorage.removeItem('currentUser');
      }
    });

    // Request notification permission and get FCM token
    requestNotificationPermission()
      .then(async (granted) => {
        if (granted) {
          const token = await getFCMToken();
          const currentUser = getCurrentUser();
          if (token && currentUser) {
            localStorage.setItem(`fcmToken_${currentUser.uid}`, token);
          }
        }
      })
      .catch(err => console.error('Notification setup error:', err));

    return unsubscribe;
  }, []);

  const signup = async (email, password, displayName, role = 'student') => {
    try {
      setError(null);
      const userData = await firebaseSignUp(email, password, displayName, role);
      setUser(userData);
      return userData;
    } catch (err) {
      setError(err.message);
      throw err;
    }
  };

  const login = async (email, password) => {
    try {
      setError(null);
      const userData = await firebaseSignIn(email, password);
      setUser(userData);
      return userData;
    } catch (err) {
      setError(err.message);
      throw err;
    }
  };

  const logout = async () => {
    try {
      setError(null);
      await firebaseSignOut();
      setUser(null);
    } catch (err) {
      setError(err.message);
      throw err;
    }
  };

  const value = {
    user,
    loading,
    error,
    signup,
    login,
    logout,
    isAuthenticated: !!user,
  };

  return (
    <FirebaseContext.Provider value={value}>
      {children}
    </FirebaseContext.Provider>
  );
};

// Custom hook to use Firebase context
export const useFirebase = () => {
  const context = React.useContext(FirebaseContext);
  if (!context) {
    throw new Error('useFirebase must be used within a FirebaseProvider');
  }
  return context;
};
