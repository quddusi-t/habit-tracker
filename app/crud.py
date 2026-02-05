from sqlalchemy.orm import Session
from app import models, schemas
from datetime import datetime, timezone
from app.utils import hash_password

# -------------------------
# Habit utilities
# -------------------------

def get_habit_by_id(db: Session, habit_id: int):
    return db.query(models.Habit).filter(models.Habit.id == habit_id).first()

def get_all_habits(db: Session):
    return db.query(models.Habit).all()

def create_habit(db: Session, habit: schemas.HabitCreate):
    new_habit = models.Habit(
        name=habit.name,
        description=habit.description,
        is_timer=habit.is_timer,
        allow_manual_override=habit.allow_manual_override
    )
    db.add(new_habit)
    db.commit()
    db.refresh(new_habit)
    return new_habit

def delete_habit(db: Session, habit_id: int):
    habit = get_habit_by_id(db, habit_id)
    if habit:
        db.delete(habit)
        db.commit()
    return habit

def update_habit(db: Session, habit_id: int, habit_update: schemas.HabitUpdate):
    habit = get_habit_by_id(db, habit_id)
    if habit:
        update_data = habit_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(habit, field, value)
        db.commit()
        db.refresh(habit)
    return habit

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

# -------------------------
# User utilities    
# -------------------------

def get_user_by_id(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def create_user(db: Session, user: schemas.UserCreate):
    existing_user = get_user_by_email(db, user.email)
    if existing_user:
        return None
    hashed_pw = hash_password(user.password)
    new_user = models.User(
        email=user.email,
        hashed_password=hashed_pw
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

def delete_user(db: Session, user_id: int):
    user = get_user_by_id(db, user_id)
    if user:
        db.delete(user)
        db.commit()
    return user

def update_user(db: Session, user_id: int, user_update: schemas.UserUpdate):
    user = get_user_by_id(db, user_id)
    if user:
        update_data = user_update.model_dump(exclude_unset=True)
        if "password" in update_data:
            update_data["hashed_password"] = hash_password(update_data.pop("password"))
        for field, value in update_data.items():
            setattr(user, field, value)
        db.commit()
        db.refresh(user)
    return user


