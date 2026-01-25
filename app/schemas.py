from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class HabitBase(BaseModel):
    name: str
    description: Optional[str] = None

class HabitCreate(HabitBase):
    pass

class Habit(HabitBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class HabitUpdate(BaseModel):
    name: str | None = None
    description: str | None = None

class HabitLogBase(BaseModel):
    notes: Optional[str] = None

class HabitLogCreate(HabitLogBase):
    pass

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

