import React, { createContext, useContext, useState, useEffect } from 'react';

const AuthContext = createContext();

export const useAuth = () => {
  return useContext(AuthContext);
};

export const AuthProvider = ({ children }) => {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [user, setUser] = useState(null);
  const [role, setRole] = useState(null); // 'Artist' or 'Collector'

  // Simulate checking localStorage or API for persisted login
  useEffect(() => {
    console.log('AuthContext useEffect running');
    try {
      const storedUser = localStorage.getItem('user');
      const storedToken = localStorage.getItem('token');
      console.log('Stored user:', storedUser);
      console.log('Stored token:', storedToken);
      if (storedUser && storedToken) {
        const userData = JSON.parse(storedUser);
        console.log('Setting user data:', userData);
        setUser(userData);
        setRole(userData.role === "artist" ? "Artist" : "Collector");
        setIsLoggedIn(true);
        console.log('Login state set to true');
      } else {
        console.log('No stored user/token found');
      }
    } catch (error) {
      console.error('Error loading user data:', error);
      localStorage.removeItem('user');
      localStorage.removeItem('token');
    }
  }, []);

  const login = (userData, userRole, token) => {
    console.log('Login function called with:', userData, userRole, token);
    setUser(userData);
    setRole(userData.role === "artist" ? "Artist" : "Collector");
    setIsLoggedIn(true);
    localStorage.setItem('user', JSON.stringify(userData));
    if (token) {
      localStorage.setItem('token', token);
    }
    console.log('Login state updated, isLoggedIn should be true');
  };

  const logout = () => {
    setUser(null);
    setRole(null);
    setIsLoggedIn(false);
    localStorage.removeItem('user');

    localStorage.removeItem('token');
  };

  const value = {
    isLoggedIn,
    user,
    role,
    login,
    logout,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};
