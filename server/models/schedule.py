# Schedule model for storing user calendar events and tasks
# This file defines the SQLAlchemy ORM model for scheduling data

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime, timedelta
import enum
import pytz
import uuid

from models.db import Base, db_session

class AttendeeStatus(enum.Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    DECLINED = "declined"
    TENTATIVE = "tentative"

class NotificationType(enum.Enum):
    EMAIL = "email"
    PUSH = "push"
    SMS = "sms"

class Schedule(Base):
    """SQLAlchemy model for calendar events"""
    __tablename__ = "schedules"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String, nullable=False)
    description = Column(Text)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    location = Column(String)
    is_all_day = Column(Boolean, default=False)
    recurrence_rule = Column(String)  # iCalendar RRULE format
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="schedules")
    reminders = relationship("Reminder", back_populates="schedule", cascade="all, delete-orphan")
    attendees = relationship("Attendee", back_populates="schedule", cascade="all, delete-orphan")


class Reminder(Base):
    """SQLAlchemy model for schedule reminders"""
    __tablename__ = "reminders"
    
    id = Column(Integer, primary_key=True, index=True)
    schedule_id = Column(Integer, ForeignKey("schedules.id"))
    reminder_time = Column(DateTime, nullable=False)
    notification_type = Column(Enum(NotificationType), default=NotificationType.EMAIL)
    
    # Relationships
    schedule = relationship("Schedule", back_populates="reminders")


class Attendee(Base):
    """SQLAlchemy model for event attendees"""
    __tablename__ = "attendees"
    
    id = Column(Integer, primary_key=True, index=True)
    schedule_id = Column(Integer, ForeignKey("schedules.id"))
    name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    status = Column(Enum(AttendeeStatus), default=AttendeeStatus.PENDING)
    
    # Relationships
    schedule = relationship("Schedule", back_populates="attendees")


def create_schedule_item(user_id, title, start_time, end_time, **kwargs):
    """Factory method to create new schedule entry"""
    schedule = Schedule(
        user_id=user_id,
        title=title,
        start_time=start_time,
        end_time=end_time,
        **kwargs
    )
    return schedule


def get_user_schedule(user_id, start_date=None, end_date=None):
    """Query helper to fetch user's schedule"""
    query = db_session.query(Schedule).filter(Schedule.user_id == user_id)
    
    if start_date:
        query = query.filter(Schedule.end_time >= start_date)
    if end_date:
        query = query.filter(Schedule.start_time <= end_date)
        
    return query.order_by(Schedule.start_time).all()


def check_conflicts(user_id, start_time, end_time):
    """Checks for scheduling conflicts"""
    conflicts = db_session.query(Schedule).filter(
        Schedule.user_id == user_id,
        Schedule.start_time < end_time,
        Schedule.end_time > start_time
    ).all()
    
    return conflicts


def generate_recurring_events(schedule, start_date, end_date):
    """Expands recurring events for a date range"""
    # This would use the rrule module to expand recurring events
    # based on the recurrence_rule field
    # For complex recurrence patterns, a library like dateutil.rrule would be used
    
    # Simplified example for daily recurrence:
    if not schedule.recurrence_rule:
        return [schedule]
        
    expanded_events = []
    current_date = schedule.start_time
    
    # Simple daily recurrence example
    if "DAILY" in schedule.recurrence_rule:
        while current_date <= end_date:
            if current_date >= start_date:
                event_duration = schedule.end_time - schedule.start_time
                new_event = Schedule(
                    user_id=schedule.user_id,
                    title=schedule.title,
                    description=schedule.description,
                    start_time=current_date,
                    end_time=current_date + event_duration,
                    location=schedule.location,
                    is_all_day=schedule.is_all_day
                )
                expanded_events.append(new_event)
            current_date += timedelta(days=1)
            
    return expanded_events 