# Database connection configuration
# This file sets up SQLAlchemy and PostgreSQL connection with pgvector support

from sqlalchemy import create_engine as sa_create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
import os
from contextlib import contextmanager
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# SQLAlchemy declarative base for models
Base = declarative_base()

def get_db_url():
    """Constructs database URL from environment variables"""
    db_user = os.getenv("DB_USER", "postgres")
    db_password = os.getenv("DB_PASSWORD", "postgres")
    db_host = os.getenv("DB_HOST", "localhost")
    db_port = os.getenv("DB_PORT", "5432")
    db_name = os.getenv("DB_NAME", "langchain_agents")
    
    return f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

def create_engine():
    """Creates SQLAlchemy engine with appropriate settings"""
    return sa_create_engine(
        get_db_url(),
        pool_pre_ping=True,
        pool_size=5,
        max_overflow=10,
        pool_recycle=300,
        connect_args={"options": "-c timezone=utc"}
    )

# Create engine and session factory
engine = create_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db_session = scoped_session(SessionLocal)

def get_db():
    """Dependency for FastAPI to get database session"""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()

@contextmanager
def get_db_session():
    """Context manager for database sessions"""
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

def init_db():
    """Initializes database tables and applies migrations"""
    # Enable pgvector extension if it doesn't exist
    with engine.connect() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        conn.commit()
    
    # Create all tables
    Base.metadata.create_all(bind=engine) 