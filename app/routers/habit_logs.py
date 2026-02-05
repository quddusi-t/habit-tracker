from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import models, schemas, database, crud
from datetime import datetime, timezone

router = APIRouter(
    prefix="/habit_logs",
    tags=["habit_logs"]
)

@router.post("/{habit_id}/logs/start", response_model=schemas.HabitLog)
def start_logging_session(habit_id: int, db: Session = Depends(database.get_db)):
    habit = crud.get_habit_by_id(db, habit_id)
    if habit is None:
        raise HTTPException(status_code=404, detail="Habit not found")
    return crud.create_log(db, habit_id)

@router.patch("/{habit_id}/logs/{log_id}/stop", response_model=schemas.HabitLog)
def stop_logging_session(habit_id: int, log_id: int, db: Session = Depends(database.get_db)):
    log = crud.get_log_by_id(db, log_id, habit_id)
    if log is None:
        raise HTTPException(status_code=404, detail="Habit log not found")
    if log.end_time is not None:
        raise HTTPException(status_code=400, detail="This session is already stopped")
    return crud.stop_log(db, log)

@router.get("/{habit_id}/logs", response_model=list[schemas.HabitLog])
def get_habit_logs(habit_id: int, db: Session = Depends(database.get_db)):
    habit = crud.get_habit_by_id(db, habit_id)
    if habit is None:
        raise HTTPException(status_code=404, detail="Habit not found")
    return crud.get_logs_for_habit(db, habit_id)

@router.get("/{habit_id}/logs/active", response_model=schemas.HabitLog | None)
def get_active_session(habit_id: int, db: Session = Depends(database.get_db)):
    habit = crud.get_habit_by_id(db, habit_id)
    if habit is None:
        raise HTTPException(status_code=404, detail="Habit not found")
    return crud.get_active_log(db, habit_id)
