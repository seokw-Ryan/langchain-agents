import React, { createContext, useContext, useState, useCallback } from 'react';
import axios from 'axios';

// Create context
const AuthContext = createContext();

// Custom hook to use the auth context
export const useAuth = () => useContext(AuthContext);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  // Function to check if user is authenticated (e.g., on app load)
  const checkAuthState = useCallback(async () => {
    setIsLoading(true);
    try {
      // Check token in localStorage
      const token = localStorage.getItem('auth_token');
      
      if (token) {
        // For now, just simulate successful auth check
        // In production, you'd validate the token with your backend
        setIsAuthenticated(true);
        setUser({ id: '1', name: 'Demo User' });
      } else {
        setIsAuthenticated(false);
        setUser(null);
      }
    } catch (error) {
      console.error('Auth check failed:', error);
      setIsAuthenticated(false);
      setUser(null);
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Login function
  const login = async (email, password) => {
    setIsLoading(true);
    try {
      // In a real app, make an API call to your auth endpoint
      // For now, just simulate a successful login
      localStorage.setItem('auth_token', 'demo_token');
      setIsAuthenticated(true);
      setUser({ id: '1', name: 'Demo User' });
      return true;
    } catch (error) {
      console.error('Login failed:', error);
      return false;
    } finally {
      setIsLoading(false);
    }
  };

  // Logout function
  const logout = () => {
    localStorage.removeItem('auth_token');
    setIsAuthenticated(false);
    setUser(null);
  };

  // Register function
  const register = async (name, email, password) => {
    setIsLoading(true);
    try {
      // In a real app, make an API call to your register endpoint
      // For now, just simulate a successful registration
      return true;
    } catch (error) {
      console.error('Registration failed:', error);
      return false;
    } finally {
      setIsLoading(false);
    }
  };

  // Auth context value
  const value = {
    user,
    isAuthenticated,
    isLoading,
    checkAuthState,
    login,
    logout,
    register
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}; 