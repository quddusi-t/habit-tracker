from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    habits = relationship("Habit", back_populates="owner")

class Habit(Base):
    __tablename__ = "habits"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String, nullable=True)
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

    habit_id = Column(Integer, ForeignKey("habits.id"))
    habit = relationship("Habit", back_populates="logs")
