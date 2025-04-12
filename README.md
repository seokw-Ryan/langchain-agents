# AI Agent System with LangChain

This repository showcases the development of an advanced AI agent system using the LangChain framework with a PPRN stack (PostgreSQL, Python, React, Node.js). The system is designed to provide robust research assistance, personalized life guidance, and scheduling management through LangChain's modular approach to text retrieval, embeddings, and conversation chaining.

## Architecture

- **PostgreSQL**: Database for storing user data, profiles, schedules, and optionally vector embeddings with pgvector extension
- **Python (FastAPI/Flask)**: Backend server with LangChain for orchestrating retrieval and text generation
- **React**: Frontend user interface
- **Node.js**: Tooling for React development

## Directory Structure

```
/
├── client/                           # React frontend
│   ├── package.json                  # Frontend dependencies
│   ├── public/                       # Static assets
│   │   └── index.html                # Entry HTML file
│   └── src/                          # Frontend source code
│       ├── components/               # Reusable UI components
│       ├── pages/                    # Page-level components
│       ├── App.js                    # Main application component
│       └── index.js                  # React entry point
├── server/                           # Python backend (FastAPI/Flask)
│   ├── app.py                        # Main entry point
│   ├── requirements.txt              # Python dependencies
│   ├── routers/                      # API endpoints
│   │   ├── auth.py                   # Authentication routes
│   │   ├── agent.py                  # AI agent endpoints
│   │   └── schedule.py               # Scheduling endpoints
│   ├── services/                     # Business logic
│   │   ├── langchain_service.py      # LangChain integration
│   │   └── scheduling_service.py     # Scheduling logic
│   ├── models/                       # Database models
│   │   ├── db.py                     # Database connection
│   │   ├── user.py                   # User model
│   │   ├── document.py               # Document model
│   │   └── schedule.py               # Schedule model
├── data_embedding/                   # Vector embeddings and data processing
├── tests/                            # Test files
│   ├── backend/                      # Backend tests
│   └── frontend/                     # Frontend tests
├── docker-compose.yml                # Docker container orchestration
├── pgvector_setup.sql                # PostgreSQL vector extension setup
└── .env                              # Environment variables
```

## Features

- Advanced research assistance
- Personalized life guidance
- Scheduling management
- Retrieval-Augmented Generation (RAG)
- Conversational memory

## Setup Instructions

1. Clone the repository
2. Set up environment variables in `.env`
3. Run `docker-compose up` to start all services
4. Access the frontend at http://localhost:3000
5. API endpoints are available at http://localhost:8000/api/v1

## Technology Stack

- **Backend**: Python (FastAPI/Flask), LangChain, SQLAlchemy
- **Database**: PostgreSQL with pgvector extension
- **Frontend**: React, JavaScript/TypeScript
- **Deployment**: Docker, Docker Compose
