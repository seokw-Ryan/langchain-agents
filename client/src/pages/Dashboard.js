import React, { useEffect } from 'react';
import { Typography, Box, Card, CardContent, Grid, Button } from '@mui/material';
import { useNavigate } from 'react-router-dom';
import { useStore } from '../contexts/StoreContext';

const Dashboard = () => {
  const { agents, fetchAgents, isLoading } = useStore();
  const navigate = useNavigate();

  useEffect(() => {
    fetchAgents();
  }, [fetchAgents]);

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Dashboard
        </Typography>
        <Button 
          variant="contained" 
          color="primary"
          onClick={() => navigate('/agents/builder')}
        >
          Create New Agent
        </Button>
      </Box>

      {isLoading ? (
        <Typography>Loading...</Typography>
      ) : (
        <>
          <Typography variant="h6" gutterBottom>
            Your Agents
          </Typography>
          
          <Grid container spacing={3}>
            {agents.map((agent) => (
              <Grid item xs={12} sm={6} md={4} key={agent.id}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" component="div">
                      {agent.name}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      {agent.description}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
          
          {agents.length === 0 && (
            <Typography variant="body1" sx={{ mt: 2 }}>
              You haven't created any agents yet. Click "Create New Agent" to get started!
            </Typography>
          )}
        </>
      )}
    </Box>
  );
};

export default Dashboard; 