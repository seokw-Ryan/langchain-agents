import React, { createContext, useState, useContext, useCallback } from 'react';

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
      // Check username in localStorage
      const username = localStorage.getItem('username');
      
      if (username) {
        // Set user with the stored username
        setIsAuthenticated(true);
        setUser({ name: username });
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

  // Login function that only requires username
  const login = async (username) => {
    setIsLoading(true);
    try {
      if (!username.trim()) {
        return false;
      }
      
      // Store username in localStorage
      localStorage.setItem('username', username);
      setIsAuthenticated(true);
      setUser({ name: username });
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
    localStorage.removeItem('username');
    setIsAuthenticated(false);
    setUser(null);
  };

  // Auth context value
  const value = {
    user,
    isAuthenticated,
    isLoading,
    checkAuthState,
    login,
    logout
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

export default AuthContext; 