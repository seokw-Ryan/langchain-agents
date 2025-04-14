import axios from 'axios';

// Create API client instance
const apiClient = axios.create({
  baseURL: process.env.REACT_APP_API_URL || 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add response interceptor to handle errors consistently
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error.response || error);
    return Promise.reject(error);
  }
);

// Helper to get username from localStorage
const getUsername = () => localStorage.getItem('username');

// API service functions
const apiService = {
  // Chat with the agent
  chat: async (query, conversationId = null) => {
    const username = getUsername();
    const response = await apiClient.post('/api/v1/agent/chat', {
      query,
      conversation_id: conversationId,
      username
    });
    return response.data;
  },

  // Research using RAG
  research: async (query) => {
    const username = getUsername();
    const response = await apiClient.post('/api/v1/agent/research', {
      query,
      username
    });
    return response.data;
  },

  // Upload document for knowledge base
  uploadDocument: async (file, title) => {
    const username = getUsername();
    const formData = new FormData();
    formData.append('file', file);
    formData.append('title', title);
    formData.append('username', username);

    const response = await apiClient.post('/api/v1/agent/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  // Get conversation history
  getHistory: async () => {
    const username = getUsername();
    const response = await apiClient.get(`/api/v1/agent/history?username=${username}`);
    return response.data;
  }
};

export default apiService; 