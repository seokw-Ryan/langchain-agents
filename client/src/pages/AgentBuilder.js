import React, { useState } from 'react';
import { 
  Typography, 
  Box, 
  TextField, 
  Button, 
  Paper,
  Grid,
  FormControl,
  InputLabel,
  MenuItem,
  Select,
  Stepper,
  Step,
  StepLabel,
  CircularProgress
} from '@mui/material';
import { useNavigate } from 'react-router-dom';
import { useStore } from '../contexts/StoreContext';

const AgentBuilder = () => {
  const [activeStep, setActiveStep] = useState(0);
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [type, setType] = useState('research');
  const { createAgent, isLoading } = useStore();
  const navigate = useNavigate();

  const steps = ['Basic Information', 'Configure Capabilities', 'Confirm & Create'];

  const handleNext = () => {
    setActiveStep((prevStep) => prevStep + 1);
  };

  const handleBack = () => {
    setActiveStep((prevStep) => prevStep - 1);
  };

  const handleCreateAgent = async () => {
    const newAgent = {
      name,
      description,
      type,
      // Other configuration properties
    };
    
    const created = await createAgent(newAgent);
    if (created) {
      navigate('/agents');
    }
  };

  const getStepContent = (step) => {
    switch (step) {
      case 0:
        return (
          <Box sx={{ mt: 3 }}>
            <TextField
              fullWidth
              label="Agent Name"
              variant="outlined"
              required
              value={name}
              onChange={(e) => setName(e.target.value)}
              sx={{ mb: 3 }}
            />
            <TextField
              fullWidth
              label="Description"
              variant="outlined"
              required
              multiline
              rows={3}
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              sx={{ mb: 3 }}
            />
            <FormControl fullWidth>
              <InputLabel id="agent-type-label">Agent Type</InputLabel>
              <Select
                labelId="agent-type-label"
                id="agent-type"
                value={type}
                label="Agent Type"
                onChange={(e) => setType(e.target.value)}
              >
                <MenuItem value="research">Research Assistant</MenuItem>
                <MenuItem value="scheduling">Schedule Manager</MenuItem>
                <MenuItem value="guidance">Life Coach</MenuItem>
              </Select>
            </FormControl>
          </Box>
        );
      case 1:
        return (
          <Box sx={{ mt: 3 }}>
            <Typography variant="h6" gutterBottom>
              Configure Agent Capabilities
            </Typography>
            
            <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
              For this demo, we're using simplified configuration.
              In a real application, this would include more detailed settings.
            </Typography>
            
            <Grid container spacing={3}>
              <Grid item xs={12}>
                <Paper sx={{ p: 3, mb: 3 }}>
                  <Typography variant="subtitle1" gutterBottom>
                    LLM Model Selection
                  </Typography>
                  <FormControl fullWidth sx={{ mt: 2 }}>
                    <InputLabel>Language Model</InputLabel>
                    <Select
                      value="gpt-4"
                      label="Language Model"
                      disabled
                    >
                      <MenuItem value="gpt-4">GPT-4</MenuItem>
                    </Select>
                  </FormControl>
                </Paper>
              </Grid>
              
              <Grid item xs={12}>
                <Paper sx={{ p: 3 }}>
                  <Typography variant="subtitle1" gutterBottom>
                    Agent Tools
                  </Typography>
                  <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                    Selected based on agent type.
                  </Typography>
                </Paper>
              </Grid>
            </Grid>
          </Box>
        );
      case 2:
        return (
          <Box sx={{ mt: 3 }}>
            <Typography variant="h6" gutterBottom>
              Confirm Agent Details
            </Typography>
            
            <Paper sx={{ p: 3, mb: 3 }}>
              <Grid container spacing={2}>
                <Grid item xs={4}>
                  <Typography variant="subtitle2">Name:</Typography>
                </Grid>
                <Grid item xs={8}>
                  <Typography>{name || 'Not specified'}</Typography>
                </Grid>
                
                <Grid item xs={4}>
                  <Typography variant="subtitle2">Type:</Typography>
                </Grid>
                <Grid item xs={8}>
                  <Typography>{type === 'research' ? 'Research Assistant' : 
                             type === 'scheduling' ? 'Schedule Manager' : 'Life Coach'}</Typography>
                </Grid>
                
                <Grid item xs={4}>
                  <Typography variant="subtitle2">Description:</Typography>
                </Grid>
                <Grid item xs={8}>
                  <Typography>{description || 'Not provided'}</Typography>
                </Grid>
              </Grid>
            </Paper>
            
            <Typography variant="body2" color="text.secondary">
              Click "Create Agent" to finalize and create your new agent.
            </Typography>
          </Box>
        );
      default:
        return 'Unknown step';
    }
  };

  return (
    <Box>
      <Typography variant="h4" component="h1" gutterBottom>
        Create New Agent
      </Typography>
      
      <Stepper activeStep={activeStep} sx={{ mb: 4 }}>
        {steps.map((label) => (
          <Step key={label}>
            <StepLabel>{label}</StepLabel>
          </Step>
        ))}
      </Stepper>
      
      <Paper sx={{ p: 3 }}>
        {getStepContent(activeStep)}
        
        <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 3 }}>
          <Button
            disabled={activeStep === 0}
            onClick={handleBack}
          >
            Back
          </Button>
          
          <Box>
            <Button
              variant="contained"
              color="primary"
              onClick={activeStep === steps.length - 1 ? handleCreateAgent : handleNext}
              disabled={isLoading || !name}
            >
              {isLoading ? (
                <CircularProgress size={24} />
              ) : activeStep === steps.length - 1 ? (
                'Create Agent'
              ) : (
                'Next'
              )}
            </Button>
          </Box>
        </Box>
      </Paper>
    </Box>
  );
};

export default AgentBuilder; 