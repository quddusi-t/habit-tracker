from sqlalchemy.orm import Session
from app import models, schemas
from datetime import datetime, timezone, timedelta
from app.utils import hash_password
from statistics import median, StatisticsError

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
    log.status = "completed"

    habit = log.habit or get_habit_by_id(db, log.habit_id)
    user = get_user_by_id(db, habit.user_id) if habit else None
    if habit and user and not has_completed_today(db, habit.id, end_time, exclude_log_id=log.id):
        habit.current_streak += 1
        if habit.is_freezable and habit.current_streak > 0 and habit.current_streak % 7 == 0:
            if user.freeze_balance < 2:
                user.freeze_balance += 1
        user.freeze_used_in_row = 0
    db.commit()
    db.refresh(log)
    return log

def create_manual_log(db: Session, habit_id: int, duration_min: int, notes: str = ""):
    """Create a manual log entry for a habit (e.g., time entered via time picker)."""
    now = datetime.now(timezone.utc)
    
    # Validate habit exists
    habit = get_habit_by_id(db, habit_id)
    if not habit:
        raise ValueError(f"Habit {habit_id} not found")
    
    # Create the manual log
    new_log = models.HabitLog(
        habit_id=habit_id,
        start_time=now,
        end_time=now,
        duration_min=duration_min,
        is_manual=True,
        notes=notes or "",
        status="completed"
    )
    db.add(new_log)
    db.flush()  # Flush to assign ID without committing
    
    # Get user for streak/freeze updates
    user = get_user_by_id(db, habit.user_id) if habit else None
    
    # Update streak and freezes if this is the first completion today
    if habit and user and not has_completed_today(db, habit.id, now, exclude_log_id=new_log.id):
        habit.current_streak += 1
        if habit.is_freezable and habit.current_streak > 0 and habit.current_streak % 7 == 0:
            if user.freeze_balance < 2:
                user.freeze_balance += 1
        user.freeze_used_in_row = 0
    
    db.commit()
    db.refresh(new_log)
    return new_log

def get_logs_for_habit(db: Session, habit_id: int):
    return db.query(models.HabitLog).filter(models.HabitLog.habit_id == habit_id).all()

def get_active_log(db: Session, habit_id: int):
    return db.query(models.HabitLog).filter(
        models.HabitLog.habit_id == habit_id,
        models.HabitLog.end_time == None
    ).first()

def get_day_bounds(target_dt: datetime | None = None) -> tuple[datetime, datetime]:
    now = target_dt or datetime.now(timezone.utc)
    day_start = datetime.combine(now.date(), datetime.min.time()).replace(tzinfo=timezone.utc)
    day_end = day_start + timedelta(days=1)
    return day_start, day_end

def get_today_logs(db: Session, habit_id: int, target_dt: datetime | None = None):
    day_start, day_end = get_day_bounds(target_dt)
    return db.query(models.HabitLog).filter(
        models.HabitLog.habit_id == habit_id,
        models.HabitLog.start_time >= day_start,
        models.HabitLog.start_time < day_end
    ).order_by(models.HabitLog.start_time.asc()).all()

def has_completed_today(db: Session, habit_id: int, target_dt: datetime | None = None, exclude_log_id: int | None = None) -> bool:
    day_start, day_end = get_day_bounds(target_dt)
    query = db.query(models.HabitLog).filter(
        models.HabitLog.habit_id == habit_id,
        models.HabitLog.start_time >= day_start,
        models.HabitLog.start_time < day_end,
        models.HabitLog.status.in_(["completed", "frozen"])
    )
    if exclude_log_id is not None:
        query = query.filter(models.HabitLog.id != exclude_log_id)
    return db.query(query.exists()).scalar()

def get_today_status(db: Session, habit_id: int, target_dt: datetime | None = None) -> str:
    logs = get_today_logs(db, habit_id, target_dt)
    statuses = {log.status for log in logs}
    if "completed" in statuses:
        return "completed"
    if "frozen" in statuses:
        return "frozen"
    return "pending"

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

    if has_completed_today(db, habit_id):
        return {"success": False, "error": "Habit already completed today"}

    now = datetime.now(timezone.utc)
    completion_log = models.HabitLog(
        habit_id=habit_id,
        start_time=now,
        end_time=now,
        duration_min=0,
        is_manual=True,
        status="completed"
    )
    db.add(completion_log)
    
    # Increment streak
    habit.current_streak += 1
    
    # Check if earned a freeze (at 7 and 14 day streaks - per habit)
    if habit.is_freezable and habit.current_streak > 0:
        if habit.current_streak % 7 == 0:  # 7, 14, 21, etc.
            if habit.freezes_remaining < 2:
                habit.freezes_remaining += 1
        if habit.current_streak % 14 == 0:  # 14, 28, etc.
            if habit.freezes_remaining < 2:
                habit.freezes_remaining += 1
    
    user.freeze_used_in_row = 0  # Reset consecutive freeze counter on completion
    
    db.commit()
    db.refresh(habit)
    db.refresh(user)
    
    return {
        "success": True,
        "streak": habit.current_streak,
        "freeze_earned": habit.current_streak % 7 == 0 and habit.is_freezable,
        "freezes_remaining": habit.freezes_remaining  # Per-habit freezes remaining
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
    
    now = datetime.now(timezone.utc)
    today_logs = get_today_logs(db, habit_id, now)
    if today_logs:
        today_logs[-1].status = "frozen"
    else:
        freeze_log = models.HabitLog(
            habit_id=habit_id,
            start_time=now,
            end_time=now,
            duration_min=0,
            is_manual=True,
            status="frozen"
        )
        db.add(freeze_log)
    
    # Decrement per-habit freezes remaining
    habit.freezes_remaining -= 1
    
    db.commit()
    db.refresh(habit)
    
    return {
        "success": True,
        "freezes_remaining": habit.freezes_remaining,
        "freeze_balance": user.freeze_balance,  # Kept for backward compatibility
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
    today_status = get_today_status(db, habit.id)
    # Only show danger if NOT completed
    if today_status == "completed":
        return False
    pct_elapsed = get_percent_of_day_elapsed()
    return pct_elapsed >= habit.danger_start_pct

def get_color_for_habit(db: Session, habit: models.Habit) -> str:
    """Get color based on time of day and completion status (4 colors: green, yellow, orange, red)."""
    pct_elapsed = get_percent_of_day_elapsed()
    
    today_status = get_today_status(db, habit.id)
    if today_status == "completed":
        return "green"
    # Frozen counts as pending for color purposes (freeze was used, but still need to complete tomorrow)
    
    if pct_elapsed < 0.5:
        return "yellow"
    elif pct_elapsed < 0.85:
        return "orange"
    else:
        return "red"

def apply_automatic_freezes(db: Session, habit_id: int) -> None:
    """Apply automatic freeze consumption if user has skipped 1-2 days, or kill streak if 3+ days."""
    habit = get_habit_by_id(db, habit_id)
    if not habit:
        return
    
    # Get last completion date
    last_completion = db.query(models.HabitLog).filter(
        models.HabitLog.habit_id == habit_id,
        models.HabitLog.status.in_(["completed", "frozen"])
    ).order_by(models.HabitLog.start_time.desc()).first()
    
    if not last_completion:
        # No completions yet, nothing to do
        return
    
    # Calculate days since last completion
    now = datetime.now(timezone.utc)
    last_completion_date = last_completion.start_time.date()
    today = now.date()
    days_since = (today - last_completion_date).days
    
    if days_since >= 3:
        # HARD RULE: Streak dies on day 3, no mercy
        habit.current_streak = 0
        db.commit()
    elif days_since >= 1 and days_since <= 2:
        # Days 1-2 of skipping: try to use a freeze
        if habit.freezes_remaining > 0 and not has_completed_today(db, habit_id, now):
            # Use the freeze automatically by creating a frozen log
            habit.freezes_remaining -= 1
            freeze_log = models.HabitLog(
                habit_id=habit_id,
                start_time=now,
                end_time=now,
                duration_min=0,
                is_manual=False,  # Automatic
                status="frozen"
            )
            db.add(freeze_log)
            db.commit()

def get_habit_status(db: Session, habit_id: int, user_id: int) -> dict:
    """Get daily status of a habit."""
    habit = get_habit_by_id(db, habit_id)
    if not habit or habit.user_id != user_id:
        return None
    
    # Apply automatic freezes first (handles skipped days)
    apply_automatic_freezes(db, habit_id)
    
    status = get_today_status(db, habit_id)
    color = get_color_for_habit(db, habit)
    # Note: in_danger removed - freeze count is the main indicator of danger
    
    return {
        "habit_id": habit_id,
        "status": status,
        "current_streak": habit.current_streak,
        "color": color
    }

# -------------------------
# Statistics and Reporting
# -------------------------

def get_timer_habit_stats(db: Session, habit: models.Habit) -> dict:
    """Calculate stats for a timer habit."""
    all_logs = db.query(models.HabitLog).filter(
        models.HabitLog.habit_id == habit.id,
        models.HabitLog.status == "completed",
        models.HabitLog.end_time != None
    ).all()
    
    sessions_count = len(all_logs)
    
    if sessions_count == 0:
        return {
            "total_time_minutes": 0,
            "avg_session_minutes": 0.0,
            "sessions_count": 0,
            "best_day_minutes": 0,
            "this_week_minutes": 0,
            "this_month_minutes": 0,
            "median_session_minutes": 0.0
        }
    
    # Total time
    total_time_minutes = sum(log.duration_min or 0 for log in all_logs)
    avg_session_minutes = total_time_minutes / sessions_count
    
    # Median
    durations = [log.duration_min or 0 for log in all_logs if log.duration_min is not None]
    median_session_minutes = median(durations) if durations else 0.0
    
    # Best day
    day_totals = {}
    for log in all_logs:
        date_key = log.start_time.date()
        day_totals[date_key] = day_totals.get(date_key, 0) + (log.duration_min or 0)
    best_day_minutes = max(day_totals.values()) if day_totals else 0
    
    # This week (last 7 days)
    week_ago = datetime.now(timezone.utc) - timedelta(days=7)
    this_week_minutes = sum(
        log.duration_min or 0 for log in all_logs 
        if log.start_time >= week_ago
    )
    
    # This month (last 30 days)
    month_ago = datetime.now(timezone.utc) - timedelta(days=30)
    this_month_minutes = sum(
        log.duration_min or 0 for log in all_logs 
        if log.start_time >= month_ago
    )
    
    return {
        "total_time_minutes": total_time_minutes,
        "avg_session_minutes": round(avg_session_minutes, 2),
        "sessions_count": sessions_count,
        "best_day_minutes": best_day_minutes,
        "this_week_minutes": this_week_minutes,
        "this_month_minutes": this_month_minutes,
        "median_session_minutes": round(median_session_minutes, 2)
    }

def get_manual_habit_stats(db: Session, habit: models.Habit) -> dict:
    """Calculate stats for a manual habit."""
    # Total completions
    completed_logs = db.query(models.HabitLog).filter(
        models.HabitLog.habit_id == habit.id,
        models.HabitLog.status == "completed"
    ).all()
    total_completions = len(completed_logs)
    
    # Days since created
    days_since_created = (datetime.now(timezone.utc) - habit.created_at).days
    
    # Completion rate
    completion_rate_percent = 0.0
    if days_since_created > 0:
        completion_rate_percent = (total_completions / days_since_created) * 100
    
    # Best streak - track from completion gaps
    all_complete_dates = sorted(set(log.start_time.date() for log in completed_logs))
    best_streak = 1 if all_complete_dates else 0
    
    if len(all_complete_dates) > 1:
        current_streak_calc = 1
        for i in range(1, len(all_complete_dates)):
            if (all_complete_dates[i] - all_complete_dates[i-1]).days == 1:
                current_streak_calc += 1
                best_streak = max(best_streak, current_streak_calc)
            else:
                current_streak_calc = 1
    
    return {
        "total_completions": total_completions,
        "completion_rate_percent": round(completion_rate_percent, 2),
        "best_streak": best_streak,
        "days_since_created": days_since_created
    }

def get_habit_stats(db: Session, habit_id: int, user_id: int) -> dict | None:
    """Get comprehensive stats for a habit."""
    habit = get_habit_by_id(db, habit_id)
    if not habit or habit.user_id != user_id:
        return None
    
    user = get_user_by_id(db, user_id)
    
    # Calculate days since created
    days_since_created = (datetime.now(timezone.utc) - habit.created_at).days
    
    # Get type-specific stats
    if habit.is_timer:
        stats = get_timer_habit_stats(db, habit)
        habit_type = "timer"
    else:
        stats = get_manual_habit_stats(db, habit)
        habit_type = "manual"
    
    # Calculate best streak from logs (for now, assume it equals current_streak)
    # In future, we could track best_streak in habit table
    best_streak = habit.current_streak
    
    # Count freezes used
    freeze_logs = db.query(models.HabitLog).filter(
        models.HabitLog.habit_id == habit.id,
        models.HabitLog.status == "frozen"
    ).count()
    
    # Get streak start date (when did current streak begin?)
    streak_start_date = None
    if habit.current_streak > 0:
        all_completed = db.query(models.HabitLog).filter(
            models.HabitLog.habit_id == habit.id,
            models.HabitLog.status.in_(["completed", "frozen"])
        ).order_by(models.HabitLog.start_time.desc()).all()
        
        if all_completed:
            streak_count = 0
            for i, log in enumerate(all_completed):
                if i == 0:
                    streak_count = 1
                    continue
                prev_date = all_completed[i-1].start_time.date()
                curr_date = log.start_time.date()
                if (prev_date - curr_date).days == 1:
                    streak_count += 1
                else:
                    break
            if streak_count == habit.current_streak and len(all_completed) > 0:
                streak_start_date = all_completed[streak_count - 1].start_time
    
    return {
        "habit_id": habit_id,
        "habit_name": habit.name,
        "habit_type": habit_type,
        "stats": stats,
        "streaks": {
            "current": habit.current_streak,
            "best": best_streak
        },
        "freezes": {
            "used": freeze_logs,
            "remaining": habit.freezes_remaining  # Per-habit freezes remaining
        },
        "days_since_created": days_since_created,
        "streak_start_date": streak_start_date
    }



