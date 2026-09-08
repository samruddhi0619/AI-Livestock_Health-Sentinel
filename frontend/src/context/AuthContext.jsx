import React, { createContext, useState, useContext, useEffect } from 'react';
import { authApi, API_BASE_URL } from '../api/client';

export { API_BASE_URL };

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(() => {
    try {
      const stored = localStorage.getItem('sentinel_user');
      return stored ? JSON.parse(stored) : null;
    } catch (e) {
      return null;
    }
  });

  const [token, setToken] = useState(() => localStorage.getItem('sentinel_token'));
  const [loading, setLoading] = useState(true);

  // Validate token and sync profile from backend on mount or token change
  useEffect(() => {
    const initAuth = async () => {
      if (token) {
        try {
          const profile = await authApi.getMe();
          setUser(profile);
          localStorage.setItem('sentinel_user', JSON.stringify(profile));
        } catch (err) {
          console.warn('Session verification failed, clearing credentials:', err.message);
          logout();
        }
      } else {
        setUser(null);
      }
      setLoading(false);
    };

    initAuth();
  }, [token]);

  const login = async (username, password) => {
    try {
      const data = await authApi.login({ username: username.trim(), password: password.trim() });
      
      const authToken = data.access_token;
      const userProfile = data.user || {
        username: username.trim(),
        role: data.role || 'FARMER'
      };

      localStorage.setItem('sentinel_token', authToken);
      localStorage.setItem('sentinel_user', JSON.stringify(userProfile));

      setToken(authToken);
      setUser(userProfile);
      return data;
    } catch (error) {
      throw error;
    }
  };

  const register = async (userData) => {
    try {
      const data = await authApi.register(userData);
      return data;
    } catch (error) {
      throw error;
    }
  };

  const logout = () => {
    localStorage.removeItem('sentinel_token');
    localStorage.removeItem('sentinel_user');
    setToken(null);
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, token, loading, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
