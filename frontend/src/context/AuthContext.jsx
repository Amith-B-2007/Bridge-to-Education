import React, { createContext, useState, useContext, useEffect } from 'react';
import api from '../utils/api';
import { firebaseSignOut } from '../services/firebaseAuthService';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const getStoredUser = () => {
    try {
      const raw = localStorage.getItem('currentUser');
      return raw ? JSON.parse(raw) : null;
    } catch (err) {
      console.warn('Failed to parse stored currentUser', err);
      return null;
    }
  };

  useEffect(() => {
    const token = localStorage.getItem('access_token');
    if (token) {
      fetchUserProfile();
    } else {
      const storedUser = getStoredUser();
      if (storedUser) {
        setUser(storedUser);
      }
      setLoading(false);
    }
  }, []);

  const fetchUserProfile = async () => {
    try {
      const response = await api.get('/users/profile/');
      setUser(response.data);
      setError(null);
    } catch (err) {
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      setUser(null);
    } finally {
      setLoading(false);
    }
  };

  const login = async (username, password) => {
    setError(null);
    try {
      const response = await api.post('/users/login/', {
        username,
        password,
      });
      const { access, refresh, user: userData } = response.data;
      localStorage.setItem('access_token', access);
      localStorage.setItem('refresh_token', refresh);
      localStorage.setItem('currentUser', JSON.stringify(userData));
      setUser(userData);
      return userData;
    } catch (err) {
      console.error('Login error:', err.response?.data);
      const message = err.response?.data?.detail || 
                     Object.values(err.response?.data || {}).flat().join(', ') || 
                     'Login failed';
      setError(message);
      throw err;
    }
  };

  const register = async (userData) => {
    setError(null);
    try {
      const response = await api.post('/users/register/', userData);
      const { access, refresh, user: newUser } = response.data;
      localStorage.setItem('access_token', access);
      localStorage.setItem('refresh_token', refresh);
      localStorage.setItem('currentUser', JSON.stringify(newUser));
      setUser(newUser);
      return newUser;
    } catch (err) {
      const message = err.response?.data?.detail || 'Registration failed';
      setError(message);
      throw err;
    }
  };

  const logout = async () => {
    try {
      await firebaseSignOut();
    } catch (err) {
      console.warn('Firebase sign-out failed:', err.message || err);
    }

    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('currentUser');
    setUser(null);
  };

  const setAuthUser = (userData) => {
    localStorage.setItem('currentUser', JSON.stringify(userData));
    setUser(userData);
  };

  const value = {
    user,
    loading,
    error,
    login,
    register,
    logout,
    setAuthUser,
    isAuthenticated: !!user,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};
