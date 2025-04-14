import React, { useState } from 'react';
import { 
  TextField, 
  Button, 
  Typography, 
  Box, 
  CircularProgress
} from '@mui/material';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

const Login = () => {
  const [username, setUsername] = useState('');
  const [error, setError] = useState('');
  const { login, isLoading } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    
    if (!username) {
      setError('Please enter your username');
      return;
    }
    
    const success = await login(username);
    if (success) {
      navigate('/');
    } else {
      setError('Failed to login. Please try again.');
    }
  };

  return (
    <Box sx={{ width: '100%' }}>
      <Typography component="h1" variant="h5" align="center" gutterBottom>
        Welcome
      </Typography>
      
      {error && (
        <Typography color="error" align="center" sx={{ mb: 2 }}>
          {error}
        </Typography>
      )}
      
      <Box component="form" onSubmit={handleSubmit} sx={{ mt: 1 }}>
        <TextField
          margin="normal"
          required
          fullWidth
          id="username"
          label="Your Name"
          name="username"
          autoComplete="name"
          autoFocus
          value={username}
          onChange={(e) => setUsername(e.target.value)}
        />
        <Button
          type="submit"
          fullWidth
          variant="contained"
          sx={{ mt: 3, mb: 2 }}
          disabled={isLoading}
        >
          {isLoading ? <CircularProgress size={24} /> : 'Continue'}
        </Button>
      </Box>
    </Box>
  );
};

export default Login; 