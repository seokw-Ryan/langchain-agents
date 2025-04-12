# User model for authentication and profile data
# This file defines the SQLAlchemy ORM model for user accounts

from sqlalchemy import Column, Integer, String, Boolean, DateTime, func
from sqlalchemy.orm import relationship
from passlib.context import CryptContext
from datetime import datetime

from server.models.db import Base, db_session

# Password hashing setup
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class User(Base):
    """SQLAlchemy model representing user accounts"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    schedules = relationship("Schedule", back_populates="user", cascade="all, delete-orphan")
    preferences = Column(String)  # JSON string for user preferences
    
    def verify_password(self, password):
        """Instance method to check password against hash"""
        return pwd_context.verify(password, self.password_hash)


def get_password_hash(password):
    """Hash user passwords for secure storage"""
    return pwd_context.hash(password)


def create_user(username, email, password):
    """Factory method to create new user with hashed password"""
    hashed_password = get_password_hash(password)
    user = User(
        username=username,
        email=email,
        password_hash=hashed_password
    )
    return user


def get_user_by_email(email):
    """Query helper to find user by email address"""
    return db_session.query(User).filter(User.email == email).first()


def get_user_by_id(user_id):
    """Query helper to find user by primary key"""
    return db_session.query(User).filter(User.id == user_id).first()

# The model includes:
# - Password hashing with secure algorithms
# - Timestamps for account creation and updates
# - User preference storage
# - Account status tracking 