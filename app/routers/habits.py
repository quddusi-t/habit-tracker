from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import models, schemas, database, utils, crud
from datetime import datetime, timezone
from fastapi.security import OAuth2PasswordBearer

router = APIRouter(
    prefix="/habits",
    tags=["habits"]
)


# Define the OAuth2 scheme once
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


@router.get("/", response_model=list[schemas.Habit])
def read_habits(db: Session = Depends(database.get_db), token: str = Depends(oauth2_scheme)):
    payload = utils.verify_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return crud.get_all_habits(db)

@router.post("/", response_model=schemas.Habit)
def create_habit(habit: schemas.HabitCreate, db: Session = Depends(database.get_db)):
    return crud.create_habit(db, habit)

@router.get("/{id}", response_model=schemas.Habit)
def read_habit(id: int, db: Session = Depends(database.get_db)):
    habit = crud.get_habit_by_id(db, id)
    if habit is None:
        raise HTTPException(status_code=404, detail="Habit not found")
    return habit

@router.delete("/{id}")
def delete_habit(id: int, db: Session = Depends(database.get_db)):
    habit = crud.delete_habit(db, id)
    if habit is None:
        raise HTTPException(status_code=404, detail="Habit not found")
    return {"message": "Habit deleted"}

@router.patch("/{id}", response_model=schemas.Habit)
def patch_habit(id: int, habit_update: schemas.HabitUpdate, db: Session = Depends(database.get_db)):
    habit = crud.update_habit(db, id, habit_update)
    if habit is None:
        raise HTTPException(status_code=404, detail="Habit not found")
    return habit
