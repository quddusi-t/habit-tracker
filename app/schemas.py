from pydantic import BaseModel
from datetime import datetime
from typing import Optional

# -------------------------
# Habit Schemas
# -------------------------

class HabitBase(BaseModel):
    name: str
    description: Optional[str] = None

class HabitCreate(HabitBase):
    is_timer: bool = True
    allow_manual_override: bool = True

class Habit(HabitBase):
    id: int
    created_at: datetime
    is_timer: bool
    allow_manual_override: bool

    class Config:
        from_attributes = True

class HabitUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_timer: Optional[bool] = None
    allow_manual_override: Optional[bool] = None

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

class HabitLogStop(BaseModel):
    end_time: datetime

class HabitLog(HabitLogBase):
    id: int
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_min: Optional[int] = None
    habit_id: int

    class Config:
        from_attributes = True
