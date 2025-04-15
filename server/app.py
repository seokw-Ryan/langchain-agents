# Main entry point for the FastAPI application
# This file initializes the API server and includes all routes

# Functions:
# - create_app(): Creates and configures the FastAPI application
# - setup_routes(): Registers all API routes from the routers directory
# - setup_middleware(): Configures CORS, authentication, and other middleware
# - configure_db(): Initializes database connection
# - main(): Entry point when the script is run directly

# The application uses dependency injection for database sessions,
# authentication, and other shared resources 

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
import uvicorn
from dotenv import load_dotenv

from models.db import init_db
from routers import auth, agent, schedule

def create_app() -> FastAPI:
    """Creates and configures the FastAPI application"""
    load_dotenv()
    app = FastAPI(title="AI Agent System", 
                  description="API for LangChain-powered AI assistant",
                  version="1.0.0")
    
    setup_routes(app)
    setup_middleware(app)
    configure_db()
    
    return app

def setup_routes(app: FastAPI):
    """Registers all API routes from the routers directory"""
    app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
    app.include_router(agent.router, prefix="/api/v1/agent", tags=["AI Agent"])
    app.include_router(schedule.router, prefix="/api/v1/schedule", tags=["Scheduling"])

def setup_middleware(app: FastAPI):
    """Configures CORS, authentication, and other middleware"""
    app.add_middleware(
        CORSMiddleware,
        allow_origins=os.getenv("CORS_ORIGINS", "http://localhost:3000").split(","),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

def configure_db():
    """Initializes database connection"""
    init_db()

app = create_app()

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True) 