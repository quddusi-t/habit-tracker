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
