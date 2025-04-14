// Main application component
// This file defines the root React component and application layout

import React, { useEffect } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { Box } from '@mui/material';
import { useAuth } from './contexts/AuthContext';

// Layouts
import MainLayout from './layouts/MainLayout';
import AuthLayout from './layouts/AuthLayout';

// Pages
import Dashboard from './pages/Dashboard';
import Login from './pages/Login';
import NotFound from './pages/NotFound';

// Protected route component that requires authentication
const ProtectedRoute = ({ children }) => {
  const { isAuthenticated, isLoading } = useAuth();
  
  if (isLoading) {
    return <Box>Loading...</Box>;
  }
  
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }
  
  return children;
};

const App = () => {
  const { checkAuthState } = useAuth();
  
  useEffect(() => {
    // Check authentication state on app initialization
    checkAuthState();
  }, [checkAuthState]);
  
  return (
    <Routes>
      {/* Public route for login */}
      <Route element={<AuthLayout />}>
        <Route path="/login" element={<Login />} />
      </Route>
      
      {/* Protected routes with MainLayout */}
      <Route element={
        <ProtectedRoute>
          <MainLayout />
        </ProtectedRoute>
      }>
        <Route path="/" element={<Dashboard />} />
      </Route>
      
      {/* Redirect from root to dashboard */}
      <Route path="/" element={<Navigate to="/" replace />} />
      
      {/* 404 page */}
      <Route path="*" element={<NotFound />} />
    </Routes>
  );
};

export default App; 