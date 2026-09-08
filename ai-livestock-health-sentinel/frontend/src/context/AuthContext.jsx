import React, { createContext, useState, useContext, useEffect } from 'react';

const AuthContext = createContext();

export const API_BASE_URL = 'http://localhost:8000';

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem('sentinel_token'));
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (token) {
      // In a real app we'd fetch profile. 
      // For this hackathon demo, we decode user details from token payload or stored config.
      const storedRole = localStorage.getItem('sentinel_role');
      const storedName = localStorage.getItem('sentinel_fullname');
      const storedUsername = localStorage.getItem('sentinel_username');
      if (storedRole) {
        setUser({
          username: storedUsername,
          role: storedRole,
          fullname: storedName
        });
      }
    }
    setLoading(false);
  }, [token]);

  const login = async (username, password) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ username, password }),
      });

      if (!response.ok) {
        const err = await response.json();
        throw new Error(err.detail || 'Login failed');
      }

      const data = await response.json();
      localStorage.setItem('sentinel_token', data.access_token);
      localStorage.setItem('sentinel_role', data.role);
      localStorage.setItem('sentinel_fullname', data.fullname);
      localStorage.setItem('sentinel_username', username);
      
      setToken(data.access_token);
      setUser({
        username,
        role: data.role,
        fullname: data.fullname
      });
      return data;
    } catch (error) {
      throw error;
    }
  };

  const register = async (userData) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/auth/register`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(userData),
      });

      if (!response.ok) {
        const err = await response.json();
        throw new Error(err.detail || 'Registration failed');
      }
      return await response.json();
    } catch (error) {
      throw error;
    }
  };

  const logout = () => {
    localStorage.removeItem('sentinel_token');
    localStorage.removeItem('sentinel_role');
    localStorage.removeItem('sentinel_fullname');
    localStorage.removeItem('sentinel_username');
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
