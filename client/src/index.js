// React application entry point
// This file initializes the React application and mounts it to the DOM

import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';
import { ThemeProvider } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import App from './App';
import { AuthProvider } from './contexts/AuthContext';
import { StoreProvider } from './contexts/StoreContext';
import theme from './theme';
import './styles/global.css';
import reportWebVitals from './reportWebVitals';

// Configure API client with auth tokens
const configureApiClient = () => {
  // This would typically set up axios or fetch with auth interceptors
  console.log('API client configured');
};

// Main application entry point
const main = () => {
  configureApiClient();
  
  const root = ReactDOM.createRoot(document.getElementById('root'));
  
  root.render(
    <React.StrictMode>
      <StoreProvider>
        <AuthProvider>
          <ThemeProvider theme={theme}>
            <CssBaseline />
            <BrowserRouter>
              <App />
            </BrowserRouter>
          </ThemeProvider>
        </AuthProvider>
      </StoreProvider>
    </React.StrictMode>
  );
};

// Initialize the application
main();

// If you want to start measuring performance in your app, pass a function
// to log results (for example: reportWebVitals(console.log))
reportWebVitals(); 