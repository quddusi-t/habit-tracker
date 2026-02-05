from sqlalchemy.orm import Session
from app import models
from datetime import datetime, timezone

# -------------------------
# Habit utilities
# -------------------------
def get_habit_by_id(db: Session, habit_id: int):
    return db.query(models.Habit).filter(models.Habit.id == habit_id).first()

# -------------------------
# HabitLog utilities
# -------------------------
def create_log(db: Session, habit_id: int, is_manual: bool = False):
    new_log = models.HabitLog(
        habit_id=habit_id,
        start_time=datetime.now(timezone.utc),
        is_manual=is_manual
    )
    db.add(new_log)
    db.commit()
    db.refresh(new_log)
    return new_log

def get_log_by_id(db: Session, log_id: int, habit_id: int):
    return db.query(models.HabitLog).filter(
        models.HabitLog.id == log_id,
        models.HabitLog.habit_id == habit_id
    ).first()

def stop_log(db: Session, log):
    end_time = datetime.now(timezone.utc)
    duration_min = int((end_time - log.start_time).total_seconds() / 60)
    log.end_time = end_time
    log.duration_min = duration_min
    db.commit()
    db.refresh(log)
    return log

def get_logs_for_habit(db: Session, habit_id: int):
    return db.query(models.HabitLog).filter(models.HabitLog.habit_id == habit_id).all()

def get_active_log(db: Session, habit_id: int):
    return db.query(models.HabitLog).filter(
        models.HabitLog.habit_id == habit_id,
        models.HabitLog.end_time == None
    ).first()
