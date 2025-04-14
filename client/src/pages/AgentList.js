import React, { useEffect } from 'react';
import { 
  Typography, 
  Box, 
  Card, 
  CardContent, 
  Grid, 
  Button,
  IconButton,
  CardActions,
  Divider
} from '@mui/material';
import { useNavigate } from 'react-router-dom';
import { useStore } from '../contexts/StoreContext';
import DeleteIcon from '@mui/icons-material/Delete';
import EditIcon from '@mui/icons-material/Edit';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';

const AgentList = () => {
  const { agents, fetchAgents, isLoading } = useStore();
  const navigate = useNavigate();

  useEffect(() => {
    fetchAgents();
  }, [fetchAgents]);

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          My Agents
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
        <Grid container spacing={3}>
          {agents.map((agent) => (
            <Grid item xs={12} md={6} key={agent.id}>
              <Card>
                <CardContent>
                  <Typography variant="h6" component="div">
                    {agent.name}
                  </Typography>
                  <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                    {agent.description}
                  </Typography>
                </CardContent>
                <Divider />
                <CardActions>
                  <Button 
                    size="small" 
                    startIcon={<PlayArrowIcon />}
                    onClick={() => console.log('Run agent', agent.id)}
                  >
                    Run
                  </Button>
                  <IconButton size="small" aria-label="edit" onClick={() => console.log('Edit agent', agent.id)}>
                    <EditIcon fontSize="small" />
                  </IconButton>
                  <IconButton size="small" aria-label="delete" onClick={() => console.log('Delete agent', agent.id)}>
                    <DeleteIcon fontSize="small" />
                  </IconButton>
                </CardActions>
              </Card>
            </Grid>
          ))}
        </Grid>
      )}
      
      {agents.length === 0 && !isLoading && (
        <Box sx={{ textAlign: 'center', py: 4 }}>
          <Typography variant="body1" sx={{ mb: 2 }}>
            You haven't created any agents yet.
          </Typography>
          <Button 
            variant="contained" 
            color="primary"
            onClick={() => navigate('/agents/builder')}
          >
            Create Your First Agent
          </Button>
        </Box>
      )}
    </Box>
  );
};

export default AgentList; 