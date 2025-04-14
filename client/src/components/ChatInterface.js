import React, { useState, useEffect, useRef } from 'react';
import { 
  Box, 
  TextField, 
  Button, 
  Typography, 
  Paper, 
  List, 
  ListItem, 
  CircularProgress 
} from '@mui/material';
import SendIcon from '@mui/icons-material/Send';
import apiService from '../services/api';
import { useAuth } from '../contexts/AuthContext';

const ChatInterface = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [conversationId, setConversationId] = useState(null);
  const messagesEndRef = useRef(null);
  const { user } = useAuth();

  // Scroll to bottom of messages
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Send message to API
  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;

    // Add user message to chat
    const userMessage = { text: input, sender: 'user', timestamp: new Date() };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      // Call API with user query
      const response = await apiService.chat(input, conversationId);
      
      // Add response to chat
      const botMessage = { 
        text: response.response, 
        sender: 'bot',
        timestamp: new Date(),
        sources: response.sources || [] 
      };
      
      setMessages(prev => [...prev, botMessage]);
      
      // Store conversation ID for context
      if (response.conversation_id) {
        setConversationId(response.conversation_id);
      }
    } catch (error) {
      console.error('Chat error:', error);
      // Add error message
      const errorMessage = { 
        text: 'Sorry, I encountered an error processing your request.', 
        sender: 'bot',
        timestamp: new Date(),
        isError: true
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', height: '70vh' }}>
      <Typography variant="h6" sx={{ mb: 2 }}>
        Chat with AI Assistant
      </Typography>
      
      {/* Messages area */}
      <Paper 
        elevation={1} 
        sx={{ 
          flexGrow: 1, 
          mb: 2, 
          p: 2, 
          overflow: 'auto',
          bgcolor: 'background.default'
        }}
      >
        {messages.length === 0 ? (
          <Box sx={{ 
            display: 'flex', 
            flexDirection: 'column', 
            alignItems: 'center', 
            justifyContent: 'center', 
            height: '100%' 
          }}>
            <Typography color="text.secondary">
              Start a conversation with your AI assistant
            </Typography>
          </Box>
        ) : (
          <List>
            {messages.map((message, index) => (
              <ListItem 
                key={index} 
                sx={{ 
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: message.sender === 'user' ? 'flex-end' : 'flex-start',
                  mb: 2
                }}
              >
                <Paper 
                  elevation={1} 
                  sx={{
                    p: 2,
                    maxWidth: '80%',
                    bgcolor: message.sender === 'user' ? 'primary.light' : 'background.paper',
                    color: message.sender === 'user' ? 'primary.contrastText' : 'text.primary',
                    borderRadius: 2
                  }}
                >
                  <Typography variant="body1">
                    {message.text}
                  </Typography>
                  
                  {message.sources && message.sources.length > 0 && (
                    <Box sx={{ mt: 1 }}>
                      <Typography variant="caption" sx={{ fontWeight: 'bold' }}>
                        Sources:
                      </Typography>
                      {message.sources.map((source, idx) => (
                        <Typography key={idx} variant="caption" display="block">
                          {source}
                        </Typography>
                      ))}
                    </Box>
                  )}
                </Paper>
                <Typography variant="caption" sx={{ mt: 0.5 }}>
                  {message.sender === 'user' ? user?.name || 'You' : 'AI Assistant'} • {
                    new Date(message.timestamp).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})
                  }
                </Typography>
              </ListItem>
            ))}
            <div ref={messagesEndRef} />
          </List>
        )}
      </Paper>
      
      {/* Input area */}
      <Box 
        component="form" 
        onSubmit={handleSendMessage}
        sx={{ 
          display: 'flex',
          alignItems: 'center'
        }}
      >
        <TextField
          fullWidth
          placeholder="Type your message..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          disabled={isLoading}
          variant="outlined"
          size="medium"
          autoComplete="off"
          sx={{ mr: 1 }}
        />
        <Button 
          type="submit"
          variant="contained" 
          color="primary"
          disabled={isLoading || !input.trim()}
          endIcon={isLoading ? <CircularProgress size={20} color="inherit" /> : <SendIcon />}
        >
          Send
        </Button>
      </Box>
    </Box>
  );
};

export default ChatInterface; 