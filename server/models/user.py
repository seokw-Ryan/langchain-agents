# User model for simple username authentication
# This file defines the SQLAlchemy ORM model for user accounts

from sqlalchemy import Column, Integer, String, Boolean, DateTime, func
from sqlalchemy.orm import relationship
from datetime import datetime

from server.models.db import Base, db_session

class User(Base):
    """SQLAlchemy model representing user accounts"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    schedules = relationship("Schedule", back_populates="user", cascade="all, delete-orphan")
    preferences = Column(String)  # JSON string for user preferences


def create_user_with_username(username, db):
    """Factory method to create new user with just a username"""
    user = User(username=username)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_user_by_username(username, db):
    """Query helper to find user by username"""
    return db.query(User).filter(User.username == username).first()


def get_user_by_id(user_id, db):
    """Query helper to find user by primary key"""
    return db.query(User).filter(User.id == user_id).first()

# The model includes:
# - Timestamps for account creation and updates
# - User preference storage
# - Account status tracking 