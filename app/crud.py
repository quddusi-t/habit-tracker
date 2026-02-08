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

# -------------------------
# Streak and Freeze utilities
# -------------------------

def complete_habit(db: Session, habit_id: int, user_id: int) -> dict:
    """Mark habit as completed today, increment streak, possibly earn freeze."""
    habit = get_habit_by_id(db, habit_id)
    if not habit or habit.user_id != user_id:
        return {"success": False, "error": "Habit not found"}
    
    user = get_user_by_id(db, user_id)
    
    # Increment streak
    habit.current_streak += 1
    
    # Check if earned a freeze (every 7 days)
    if habit.is_freezable and habit.current_streak > 0 and habit.current_streak % 7 == 0:
        if user.freeze_balance < 2:
            user.freeze_balance += 1
    
    # Update today's log status
    today_log = get_active_log(db, habit_id)
    if today_log:
        today_log.status = "completed"
        user.freeze_used_in_row = 0  # Reset consecutive freeze counter on completion
    
    db.commit()
    db.refresh(habit)
    db.refresh(user)
    
    return {
        "success": True,
        "streak": habit.current_streak,
        "freeze_earned": habit.current_streak % 7 == 0 and habit.is_freezable,
        "freeze_balance": user.freeze_balance
    }

def use_freeze(db: Session, habit_id: int, user_id: int) -> dict:
    """Apply a streak freeze if available and allowed."""
    habit = get_habit_by_id(db, habit_id)
    user = get_user_by_id(db, user_id)
    
    if not habit or habit.user_id != user_id:
        return {"success": False, "error": "Habit not found"}
    
    if not habit.is_freezable:
        return {"success": False, "error": "This habit cannot use freezes"}
    
    if user.freeze_balance <= 0:
        return {"success": False, "error": "No freezes available"}
    
    if user.freeze_used_in_row >= 2:
        return {"success": False, "error": "Cannot use more than 2 freezes in a row"}
    
    # Apply freeze
    user.freeze_balance -= 1
    user.freeze_used_in_row += 1
    
    today_log = get_active_log(db, habit_id)
    if today_log:
        today_log.status = "frozen"
    
    db.commit()
    db.refresh(user)
    
    return {
        "success": True,
        "freeze_balance": user.freeze_balance,
        "freeze_used_in_row": user.freeze_used_in_row
    }

def get_percent_of_day_elapsed() -> float:
    """Get percentage of day elapsed (0.0 to 1.0)."""
    now = datetime.now(timezone.utc)
    midnight = datetime.combine(now.date(), datetime.min.time()).replace(tzinfo=timezone.utc)
    next_midnight = midnight.replace(day=midnight.day+1) if midnight.day < 28 else midnight.replace(month=midnight.month+1, day=1)
    elapsed = (now - midnight).total_seconds()
    total = (next_midnight - midnight).total_seconds()
    return elapsed / total

def is_habit_in_danger(db: Session, habit: models.Habit) -> bool:
    """Check if habit is in danger (late in day and not completed)."""
    pct_elapsed = get_percent_of_day_elapsed()
    return pct_elapsed >= habit.danger_start_pct

def get_color_for_habit(db: Session, habit: models.Habit) -> str:
    """Get color based on time of day and completion status."""
    pct_elapsed = get_percent_of_day_elapsed()
    
    today_log = get_active_log(db, habit.id)
    if today_log and today_log.status == "completed":
        return "green"
    if today_log and today_log.status == "frozen":
        return "blue"
    
    if pct_elapsed < 0.5:
        return "yellow"
    elif pct_elapsed < 0.85:
        return "orange"
    else:
        return "red"

def get_habit_status(db: Session, habit_id: int, user_id: int) -> dict:
    """Get daily status of a habit."""
    habit = get_habit_by_id(db, habit_id)
    if not habit or habit.user_id != user_id:
        return None
    
    today_log = get_active_log(db, habit_id)
    status = today_log.status if today_log else "pending"
    in_danger = is_habit_in_danger(db, habit)
    color = get_color_for_habit(db, habit)
    
    return {
        "habit_id": habit_id,
        "status": status,
        "current_streak": habit.current_streak,
        "in_danger": in_danger,
        "color": color
    }


