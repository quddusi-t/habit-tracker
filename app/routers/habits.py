from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app import models, schemas, database

router = APIRouter(
    prefix="/habits",
    tags=["habits"]
)

@router.post("/", response_model=schemas.Habit)
def create_habit(habit: schemas.HabitCreate, db: Session = Depends(database.get_db)):
    new_habit = models.Habit(name=habit.name, description=habit.description)
    db.add(new_habit)
    db.commit()
    db.refresh(new_habit)
    return new_habit
