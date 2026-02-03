from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import models, schemas, database, utils
from datetime import datetime, timezone
from fastapi.security import OAuth2PasswordBearer

router = APIRouter(
    prefix="/habits",
    tags=["habits"]
)


# Define the OAuth2 scheme once
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

@router.get("/", response_model=list[schemas.Habit])
def read_habits(
    db: Session = Depends(database.get_db),
    token: str = Depends(oauth2_scheme)
):
    # Verify token
    payload = utils.verify_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    # If token is valid, continue
    habits = db.query(models.Habit).all()
    return habits

@router.post("/", response_model=schemas.Habit)
def create_habit(habit: schemas.HabitCreate, db: Session = Depends(database.get_db)):
    new_habit = models.Habit(name=habit.name, description=habit.description)
    db.add(new_habit)
    db.commit()
    db.refresh(new_habit)
    return new_habit

@router.get("/{id}", response_model=schemas.Habit)
def read_habit(id: int, db: Session = Depends(database.get_db)):
    habit = db.query(models.Habit).filter(models.Habit.id == id).first()
    if habit is None:
        raise HTTPException(status_code=404, detail="Habit not found")
    return habit

@router.delete("/{id}")
def delete_habit(id: int, db: Session = Depends(database.get_db)):
    db_habit = db.query(models.Habit).filter(models.Habit.id == id).first()
    db.delete(db_habit)
    db.commit()
    return {"message": "Habit deleted"}

@router.patch("/{id}", response_model=schemas.Habit)
def patch_habit(id: int, habit_update: schemas.HabitUpdate, db: Session = Depends(database.get_db)):
    db_habit = db.query(models.Habit).filter(models.Habit.id == id).first()
    if db_habit is None:
        raise HTTPException(status_code=404, detail="Habit not found")

    update_data = habit_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_habit, field, value)

    db.commit()
    db.refresh(db_habit)
    return db_habit


