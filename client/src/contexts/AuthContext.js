import React, { createContext, useState, useContext, useCallback } from 'react';

// Create context
const AuthContext = createContext();

// Custom hook to use the auth context
export const useAuth = () => useContext(AuthContext);

export const AuthProvider = ({ children }) => {
  // Set initial state to authenticated with Ryan user
  const [user, setUser] = useState({ name: 'Ryan' });
  const [isAuthenticated, setIsAuthenticated] = useState(true);
  const [isLoading, setIsLoading] = useState(false);

  // Function to check if user is authenticated (e.g., on app load)
  const checkAuthState = useCallback(async () => {
    setIsLoading(true);
    try {
      // Always set the Ryan user in localStorage
      localStorage.setItem('username', 'Ryan');
      
      // Always authenticated with Ryan user
      setIsAuthenticated(true);
      setUser({ name: 'Ryan' });
    } catch (error) {
      console.error('Auth check failed:', error);
      // Even if there's an error, still set to authenticated
      setIsAuthenticated(true);
      setUser({ name: 'Ryan' });
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Login function that automatically succeeds with the Ryan user
  const login = async (username) => {
    setIsLoading(true);
    try {
      const fixedUsername = 'Ryan';
      // Store Ryan username in localStorage
      localStorage.setItem('username', fixedUsername);
      setIsAuthenticated(true);
      setUser({ name: fixedUsername });
      return true;
    } catch (error) {
      console.error('Login failed:', error);
      // Even if there's an error, still set to authenticated
      setIsAuthenticated(true);
      setUser({ name: 'Ryan' });
      return true;
    } finally {
      setIsLoading(false);
    }
  };

  // Logout function - we'll keep this for UI consistency but it won't actually log out
  const logout = () => {
    // Don't remove username from localStorage
    // Don't set isAuthenticated to false
    // Just for UI, show a temporary logged out state, then auto-login again
    setIsLoading(true);
    setTimeout(() => {
      setIsAuthenticated(true);
      setUser({ name: 'Ryan' });
      setIsLoading(false);
    }, 500);
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