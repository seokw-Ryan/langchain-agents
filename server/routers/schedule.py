# Scheduling endpoints for the AI Agent System
# This file handles creating, retrieving, and managing user schedules

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime, date, timedelta

from server.models.db import get_db
from server.models.user import User
from server.models.schedule import Schedule, create_schedule_item, get_user_schedule, check_conflicts
from server.services.scheduling_service import ScheduleOptimizer
from server.routers.auth import get_current_user

router = APIRouter()

# Pydantic models for request/response
class ScheduleBase(BaseModel):
    title: str
    description: Optional[str] = None
    start_time: datetime
    end_time: datetime
    location: Optional[str] = None
    is_all_day: Optional[bool] = False
    recurrence_rule: Optional[str] = None

class ScheduleCreate(ScheduleBase):
    pass

class ScheduleResponse(ScheduleBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class ScheduleRecommendation(BaseModel):
    suggestion: str
    reason: str
    impact: float  # Score to quantify the positive impact of the suggestion

@router.post("", response_model=ScheduleResponse)
async def create_schedule_item_endpoint(
    schedule_data: ScheduleCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new task or appointment"""
    # Check for scheduling conflicts
    conflicts = check_conflicts(
        current_user.id, schedule_data.start_time, schedule_data.end_time
    )
    
    if conflicts:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This schedule conflicts with existing appointments"
        )
    
    # Create the schedule item
    schedule_item = create_schedule_item(
        user_id=current_user.id,
        title=schedule_data.title,
        start_time=schedule_data.start_time,
        end_time=schedule_data.end_time,
        description=schedule_data.description,
        location=schedule_data.location,
        is_all_day=schedule_data.is_all_day,
        recurrence_rule=schedule_data.recurrence_rule
    )
    
    db.add(schedule_item)
    db.commit()
    db.refresh(schedule_item)
    
    return schedule_item

@router.get("", response_model=List[ScheduleResponse])
async def get_user_schedule_endpoint(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve all schedule items for a user"""
    schedule_items = get_user_schedule(
        user_id=current_user.id,
        start_date=start_date,
        end_date=end_date
    )
    
    return schedule_items

@router.put("/{schedule_id}", response_model=ScheduleResponse)
async def update_schedule_item(
    schedule_id: int,
    schedule_data: ScheduleBase,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Modify an existing schedule item"""
    # Get the schedule item
    schedule_item = db.query(Schedule).filter(
        Schedule.id == schedule_id,
        Schedule.user_id == current_user.id
    ).first()
    
    if schedule_item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Schedule item not found"
        )
    
    # Check for scheduling conflicts (excluding this item)
    conflicts = db.query(Schedule).filter(
        Schedule.user_id == current_user.id,
        Schedule.id != schedule_id,
        Schedule.start_time < schedule_data.end_time,
        Schedule.end_time > schedule_data.start_time
    ).all()
    
    if conflicts:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This schedule conflicts with existing appointments"
        )
    
    # Update the schedule item
    for key, value in schedule_data.dict().items():
        setattr(schedule_item, key, value)
    
    db.commit()
    db.refresh(schedule_item)
    
    return schedule_item

@router.delete("/{schedule_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_schedule_item(
    schedule_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Remove a schedule item"""
    # Get the schedule item
    schedule_item = db.query(Schedule).filter(
        Schedule.id == schedule_id,
        Schedule.user_id == current_user.id
    ).first()
    
    if schedule_item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Schedule item not found"
        )
    
    # Delete the schedule item
    db.delete(schedule_item)
    db.commit()
    
    return None

@router.get("/recommendations", response_model=List[ScheduleRecommendation])
async def get_schedule_recommendations(
    days: int = Query(7, ge=1, le=30),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate AI-based suggestions for schedule improvements"""
    # Get the schedule items for the specified days
    start_date = datetime.utcnow().date()
    end_date = start_date + timedelta(days=days)
    
    schedule_items = get_user_schedule(
        user_id=current_user.id,
        start_date=start_date,
        end_date=end_date
    )
    
    # Use the ScheduleOptimizer to generate recommendations
    optimizer = ScheduleOptimizer()
    recommendations = optimizer.generate_recommendations(schedule_items)
    
    return recommendations 