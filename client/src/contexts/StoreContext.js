import React, { createContext, useContext, useState } from 'react';

// Create context
const StoreContext = createContext();

// Custom hook to use the store context
export const useStore = () => useContext(StoreContext);

export const StoreProvider = ({ children }) => {
  // Global application state
  const [agents, setAgents] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  // Function to fetch agents
  const fetchAgents = async () => {
    setIsLoading(true);
    setError(null);
    try {
      // In a real app, make an API call to your backend
      // For now, just simulate agents data
      setAgents([
        { id: '1', name: 'Research Assistant', description: 'Helps with research tasks' },
        { id: '2', name: 'Schedule Manager', description: 'Manages your schedule' },
        { id: '3', name: 'Life Coach', description: 'Provides life guidance' }
      ]);
    } catch (error) {
      console.error('Failed to fetch agents:', error);
      setError('Failed to load agents. Please try again later.');
    } finally {
      setIsLoading(false);
    }
  };

  // Function to create a new agent
  const createAgent = async (agentData) => {
    setIsLoading(true);
    setError(null);
    try {
      // In a real app, make an API call to create agent
      // For now, just simulate creating an agent
      const newAgent = {
        id: Date.now().toString(),
        ...agentData
      };
      setAgents(prev => [...prev, newAgent]);
      return newAgent;
    } catch (error) {
      console.error('Failed to create agent:', error);
      setError('Failed to create agent. Please try again later.');
      return null;
    } finally {
      setIsLoading(false);
    }
  };

  // Store context value
  const value = {
    agents,
    isLoading,
    error,
    fetchAgents,
    createAgent
  };

  return (
    <StoreContext.Provider value={value}>
      {children}
    </StoreContext.Provider>
  );
}; 