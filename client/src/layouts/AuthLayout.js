import React from 'react';
import { Outlet } from 'react-router-dom';
import { Container, Box, Paper, Typography } from '@mui/material';

const AuthLayout = () => {
  return (
    <Box 
      sx={{
        display: 'flex',
        flexDirection: 'column',
        minHeight: '100vh',
        bgcolor: 'background.default',
        py: 6
      }}
    >
      <Container maxWidth="sm">
        <Box sx={{ display: 'flex', justifyContent: 'center', mb: 4 }}>
          <Typography 
            variant="h4" 
            component="div" 
            sx={{ fontWeight: 'bold', color: 'primary.main' }}
          >
            LangChain Agents
          </Typography>
        </Box>
        
        <Paper 
          elevation={3} 
          sx={{ 
            p: 4, 
            display: 'flex', 
            flexDirection: 'column', 
            alignItems: 'center'
          }}
        >
          <Outlet />
        </Paper>
      </Container>
      
      <Box 
        component="footer" 
        sx={{ 
          py: 3, 
          mt: 'auto', 
          textAlign: 'center'
        }}
      >
        <Typography variant="body2" color="text.secondary">
          © {new Date().getFullYear()} LangChain Agents
        </Typography>
      </Box>
    </Box>
  );
};

export default AuthLayout; 