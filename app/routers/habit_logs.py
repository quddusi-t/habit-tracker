from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import models, schemas, database
from datetime import datetime, timezone

router = APIRouter(
    prefix="/habit_logs",
    tags=["habit_logs"]
)

@router.post("/{habit_id}/logs/start", response_model=schemas.HabitLog)
def start_logging_session(habit_id: int, db: Session = Depends(database.get_db)):
    """Start a new logging session for a habit (start timer)"""
    habit = db.query(models.Habit).filter(models.Habit.id == habit_id).first()
    if habit is None:
        raise HTTPException(status_code=404, detail="Habit not found")
    
    new_log = models.HabitLog(habit_id=habit_id, start_time=datetime.now(timezone.utc))
    db.add(new_log)
    db.commit()
    db.refresh(new_log)
    return new_log


@router.patch("/{habit_id}/logs/{log_id}/stop", response_model=schemas.HabitLog)
def stop_logging_session(habit_id: int, log_id: int, db: Session = Depends(database.get_db)):
    """Stop a logging session (stop timer and calculate duration)"""
    log = db.query(models.HabitLog).filter(
        models.HabitLog.id == log_id,
        models.HabitLog.habit_id == habit_id
    ).first()
    
    if log is None:
        raise HTTPException(status_code=404, detail="Habit log not found")
    
    if log.end_time is not None:
        raise HTTPException(status_code=400, detail="This session is already stopped")
    
    # Calculate duration in minutes
    end_time = datetime.now(timezone.utc)
    duration_min = int((end_time - log.start_time).total_seconds() / 60)
    
    log.end_time = end_time
    log.duration_min = duration_min
    db.commit()
    db.refresh(log)
    return log


@router.get("/{habit_id}/logs", response_model=list[schemas.HabitLog])
def get_habit_logs(habit_id: int, db: Session = Depends(database.get_db)):
    """Get all logs for a habit"""
    habit = db.query(models.Habit).filter(models.Habit.id == habit_id).first()
    if habit is None:
        raise HTTPException(status_code=404, detail="Habit not found")
    
    logs = db.query(models.HabitLog).filter(models.HabitLog.habit_id == habit_id).all()
    return logs


@router.get("/{habit_id}/logs/active", response_model=schemas.HabitLog | None)
def get_active_session(habit_id: int, db: Session = Depends(database.get_db)):
    """Get the currently active logging session (if any)"""
    habit = db.query(models.Habit).filter(models.Habit.id == habit_id).first()
    if habit is None:
        raise HTTPException(status_code=404, detail="Habit not found")
    
    active_log = db.query(models.HabitLog).filter(
        models.HabitLog.habit_id == habit_id,
        models.HabitLog.end_time == None
    ).first()
    
    return active_log

