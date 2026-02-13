from pydantic import BaseModel, EmailStr, ConfigDict
from datetime import datetime
from typing import Optional, Union

# -------------------------
# Habit Schemas
# -------------------------

class HabitBase(BaseModel):
    name: str
    description: Optional[str] = None

class HabitCreate(HabitBase):
    is_timer: bool = True
    allow_manual_override: bool = True
    is_freezable: bool = True
    danger_start_pct: float = 0.7

class Habit(HabitBase):
    id: int
    created_at: datetime
    is_timer: bool
    allow_manual_override: bool
    is_freezable: bool
    danger_start_pct: float
    current_streak: int

    model_config = ConfigDict(from_attributes=True)

class HabitUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_timer: Optional[bool] = None
    allow_manual_override: Optional[bool] = None
    is_freezable: Optional[bool] = None
    danger_start_pct: Optional[float] = None

# -------------------------
# HabitLog Schemas
# -------------------------

class HabitLogBase(BaseModel):
    notes: Optional[str] = None

class HabitLogCreate(HabitLogBase):
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    duration_min: Optional[int] = None
    habit_id: int
    is_manual: bool = False

class ManualLogCreate(HabitLogBase):
    duration_min: int
    notes: Optional[str] = None
    is_manual: bool = True

class HabitLogStop(BaseModel):
    end_time: datetime

class HabitLog(HabitLogBase):
    id: int
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_min: Optional[int] = None
    habit_id: int
    is_manual: bool
    status: str  # pending, completed, missed, frozen

    model_config = ConfigDict(from_attributes=True)

class HabitStatus(BaseModel):
    """Daily status of a habit"""
    habit_id: int
    status: str  # pending, completed, missed, frozen
    current_streak: int
    in_danger: bool
    color: str  # yellow, orange, red, green, blue

# -------------------------
# Habit Stats Schemas
# -------------------------

class TimerHabitStats(BaseModel):
    total_time_minutes: int
    avg_session_minutes: float
    sessions_count: int
    best_day_minutes: int
    this_week_minutes: int
    this_month_minutes: int
    median_session_minutes: float

class ManualHabitStats(BaseModel):
    total_completions: int
    completion_rate_percent: float
    best_streak: int
    days_since_created: int

class HabitStreaks(BaseModel):
    current: int
    best: int

class HabitFreezes(BaseModel):
    used: int
    remaining: int

class HabitStats(BaseModel):
    """Comprehensive stats for a habit"""
    habit_id: int
    habit_name: str
    habit_type: str  # "timer" or "manual"
    stats: Union[TimerHabitStats, ManualHabitStats]
    streaks: HabitStreaks
    freezes: HabitFreezes
    days_since_created: int
    streak_start_date: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

# -------------------------
# User Schemas
# -------------------------

# For creating a user (signup request)
class UserCreate(BaseModel):
    email: EmailStr
    password: str

# For returning user info (excluding password)
class User(BaseModel):
    id: int
    email: EmailStr
    created_at: datetime
    freeze_balance: int
    freeze_used_in_row: int

    model_config = ConfigDict(from_attributes=True)

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    password: Optional[str] = None

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"





