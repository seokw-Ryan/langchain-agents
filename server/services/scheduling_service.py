# Scheduling service for the AI Agent System
# This file implements business logic for scheduling operations and calendar integration

from typing import List, Optional
from datetime import datetime, timedelta
import pytz
import requests
import json
from dataclasses import dataclass

from models.schedule import Schedule, get_user_schedule, check_conflicts

@dataclass
class ScheduleRecommendation:
    suggestion: str
    reason: str
    impact: float  # Score to quantify the positive impact of the suggestion

class ScheduleManager:
    """Core class for managing schedule operations"""
    
    def get_schedule(self, user_id: int, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None):
        """Get user schedule items within a date range"""
        return get_user_schedule(user_id, start_date, end_date)
    
    def has_conflicts(self, user_id: int, start_time: datetime, end_time: datetime, exclude_id: Optional[int] = None):
        """Check if a time slot has conflicts with existing schedule items"""
        conflicts = check_conflicts(user_id, start_time, end_time)
        
        if exclude_id:
            conflicts = [item for item in conflicts if item.id != exclude_id]
            
        return len(conflicts) > 0
    
    def get_busy_times(self, user_id: int, date: datetime):
        """Get time slots when the user is busy for a specific date"""
        start_of_day = datetime(date.year, date.month, date.day, 0, 0, 0, tzinfo=pytz.UTC)
        end_of_day = start_of_day + timedelta(days=1)
        
        schedule_items = get_user_schedule(user_id, start_of_day, end_of_day)
        
        busy_times = []
        for item in schedule_items:
            busy_times.append({
                'start': item.start_time,
                'end': item.end_time
            })
            
        return busy_times
    
    def get_free_slots(self, user_id: int, date: datetime, min_duration_minutes: int = 30):
        """Get available time slots for a specific date"""
        busy_times = self.get_busy_times(user_id, date)
        
        # Sort busy times by start time
        busy_times.sort(key=lambda x: x['start'])
        
        # Define working hours (9 AM to 5 PM)
        start_of_day = datetime(date.year, date.month, date.day, 9, 0, 0, tzinfo=pytz.UTC)
        end_of_day = datetime(date.year, date.month, date.day, 17, 0, 0, tzinfo=pytz.UTC)
        
        # Find free slots
        free_slots = []
        current_time = start_of_day
        
        for busy in busy_times:
            if current_time < busy['start']:
                duration = (busy['start'] - current_time).total_seconds() / 60
                if duration >= min_duration_minutes:
                    free_slots.append({
                        'start': current_time,
                        'end': busy['start'],
                        'duration_minutes': duration
                    })
            current_time = max(current_time, busy['end'])
        
        # Add final free slot if there's time after the last busy slot
        if current_time < end_of_day:
            duration = (end_of_day - current_time).total_seconds() / 60
            if duration >= min_duration_minutes:
                free_slots.append({
                    'start': current_time,
                    'end': end_of_day,
                    'duration_minutes': duration
                })
        
        return free_slots


class CalendarIntegration:
    """Handles integration with external calendar systems"""
    
    def __init__(self, provider: str = 'google'):
        self.provider = provider
        
    def sync_events(self, user_id: int, external_events: List[dict]):
        """Import events from external calendar to the system"""
        # Implementation would depend on the calendar provider API
        pass
    
    def export_events(self, user_id: int, start_date: datetime, end_date: datetime):
        """Export events from the system to external calendar"""
        # Implementation would depend on the calendar provider API
        pass
    
    def get_auth_url(self):
        """Get OAuth URL for calendar authorization"""
        # Implementation would depend on the calendar provider
        if self.provider == 'google':
            return "https://accounts.google.com/o/oauth2/auth?scope=https://www.googleapis.com/auth/calendar&response_type=code"
        return None


class ScheduleOptimizer:
    """AI-powered schedule optimization algorithms"""
    
    def analyze_schedule(self, schedule_items: List[Schedule]):
        """Analyze schedule for patterns and optimization opportunities"""
        # Analyze the schedule for various metrics
        analysis = {
            'total_items': len(schedule_items),
            'meeting_hours': sum((item.end_time - item.start_time).total_seconds() / 3600 
                                for item in schedule_items if "meeting" in item.title.lower()),
            'focus_blocks': sum(1 for item in schedule_items if "focus" in item.title.lower()),
            'after_hours_work': sum(1 for item in schedule_items 
                                  if item.start_time.hour >= 17 or item.start_time.hour < 9)
        }
        
        return analysis
    
    def generate_recommendations(self, schedule_items: List[Schedule]) -> List[ScheduleRecommendation]:
        """Generate recommendations for schedule optimization"""
        analysis = self.analyze_schedule(schedule_items)
        recommendations = []
        
        # Check for too many meetings
        if analysis['meeting_hours'] > 20:
            recommendations.append(ScheduleRecommendation(
                suggestion="Consider reducing meeting time by 20%",
                reason="You have more than 20 hours of meetings scheduled, which can limit productivity",
                impact=0.8
            ))
        
        # Check for lack of focus time
        if analysis['focus_blocks'] < 3:
            recommendations.append(ScheduleRecommendation(
                suggestion="Add at least 3 focus blocks of 90+ minutes to your week",
                reason="Insufficient dedicated focus time for deep work",
                impact=0.9
            ))
        
        # Check for work-life balance
        if analysis['after_hours_work'] > 3:
            recommendations.append(ScheduleRecommendation(
                suggestion="Move after-hours work to regular work hours",
                reason="Working outside regular hours may lead to burnout",
                impact=0.7
            ))
        
        return recommendations


class ReminderService:
    """Manages notifications and reminders"""
    
    def send_reminder(self, reminder_id: int):
        """Send a reminder notification"""
        # Implementation would depend on notification mechanisms
        pass
    
    def schedule_reminders(self, schedule_id: int):
        """Schedule reminders for a schedule item"""
        # Implementation would depend on scheduling mechanism (e.g., Celery)
        pass


class ConflictResolver:
    """Detects and resolves scheduling conflicts"""
    
    def detect_conflicts(self, schedule_item: Schedule, user_id: int):
        """Detect conflicts with existing schedule items"""
        conflicts = check_conflicts(user_id, schedule_item.start_time, schedule_item.end_time)
        return [c for c in conflicts if c.id != schedule_item.id]
    
    def suggest_alternative_times(self, schedule_item: Schedule, user_id: int, num_suggestions: int = 3):
        """Suggest alternative times for a schedule item with conflicts"""
        # Get the current day and next 5 days
        suggestions = []
        current_date = schedule_item.start_time.date()
        
        # Initialize ScheduleManager
        schedule_manager = ScheduleManager()
        
        # Check the next 5 days for available slots
        for day_offset in range(5):
            check_date = current_date + timedelta(days=day_offset)
            free_slots = schedule_manager.get_free_slots(
                user_id, 
                datetime(check_date.year, check_date.month, check_date.day, tzinfo=pytz.UTC)
            )
            
            # Calculate required duration
            required_duration = (schedule_item.end_time - schedule_item.start_time).total_seconds() / 60
            
            # Find slots with sufficient duration
            valid_slots = [slot for slot in free_slots if slot['duration_minutes'] >= required_duration]
            
            # Add suggestions
            for slot in valid_slots[:num_suggestions - len(suggestions)]:
                suggestions.append({
                    'date': check_date,
                    'start_time': slot['start'],
                    'end_time': slot['start'] + timedelta(minutes=required_duration)
                })
                
                if len(suggestions) >= num_suggestions:
                    break
            
            if len(suggestions) >= num_suggestions:
                break
                
        return suggestions 