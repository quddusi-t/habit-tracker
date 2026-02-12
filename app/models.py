from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean, Float
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    freeze_balance = Column(Integer, default=0)  # Number of streak freezes available
    freeze_used_in_row = Column(Integer, default=0)  # Consecutive freezes used

    habits = relationship("Habit", back_populates="owner")

class Habit(Base):
    __tablename__ = "habits"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String, nullable=True)
    is_timer = Column(Boolean, default=True) # True = timed habit, False = instant streak 
    allow_manual_override = Column(Boolean, default=True)
    is_freezable = Column(Boolean, default=True)  # Whether streak freezes can be used
    danger_start_pct = Column(Float, default=0.7)  # Percentage of day when habit becomes "in danger"
    current_streak = Column(Integer, default=0)  # Current active streak count
    freezes_remaining = Column(Integer, default=2)  # Freezes available for this habit (per-habit)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    user_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="habits")

    logs = relationship("HabitLog", back_populates="habit")

class HabitLog(Base):
    __tablename__ = "habit_logs"

    id = Column(Integer, primary_key=True, index=True)
    start_time = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    end_time = Column(DateTime(timezone=True), nullable=True)
    duration_min = Column(Integer, nullable=True)
    notes = Column(String, nullable=True)
    is_manual = Column(Boolean, default=False)
    status = Column(String, default='pending')  # pending, completed, missed, frozen

    habit_id = Column(Integer, ForeignKey("habits.id"))
    habit = relationship("Habit", back_populates="logs")
