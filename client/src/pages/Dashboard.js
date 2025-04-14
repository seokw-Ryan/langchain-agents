import React from 'react';
import { Typography, Box, Card, CardContent, Grid, Button } from '@mui/material';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import ChatInterface from '../components/ChatInterface';

const Dashboard = () => {
  const navigate = useNavigate();
  const { user } = useAuth();

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Welcome, {user?.name}!
        </Typography>
      </Box>

      <Grid container spacing={4}>
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <ChatInterface />
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Dashboard; 