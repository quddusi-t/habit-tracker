from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import models, schemas, database, utils, crud
from datetime import datetime, timezone

router = APIRouter(
    prefix="/habits",
    tags=["habits"]
)


@router.get("/", response_model=list[schemas.Habit])
def read_habits(db: Session = Depends(database.get_db), user_id: int = Depends(utils.get_current_user_id)):
    habits = db.query(models.Habit).filter(models.Habit.user_id == user_id).all()
    return habits

@router.post("/", response_model=schemas.Habit, status_code=201)
def create_habit(habit: schemas.HabitCreate, db: Session = Depends(database.get_db), user_id: int = Depends(utils.get_current_user_id)):
    new_habit = models.Habit(
        name=habit.name,
        description=habit.description,
        is_timer=habit.is_timer,
        allow_manual_override=habit.allow_manual_override,
        is_freezable=habit.is_freezable,
        danger_start_pct=habit.danger_start_pct,
        user_id=user_id
    )
    db.add(new_habit)
    db.commit()
    db.refresh(new_habit)
    return new_habit

@router.get("/{id}", response_model=schemas.Habit)
def read_habit(id: int, db: Session = Depends(database.get_db), user_id: int = Depends(utils.get_current_user_id)):
    habit = crud.get_habit_by_id(db, id)
    if habit is None or habit.user_id != user_id:
        raise HTTPException(status_code=404, detail="Habit not found")
    return habit

@router.delete("/{id}")
def delete_habit(id: int, db: Session = Depends(database.get_db), user_id: int = Depends(utils.get_current_user_id)):
    habit = crud.get_habit_by_id(db, id)
    if habit is None or habit.user_id != user_id:
        raise HTTPException(status_code=404, detail="Habit not found")
    db.delete(habit)
    db.commit()
    return {"message": "Habit deleted"}

@router.patch("/{id}", response_model=schemas.Habit)
def patch_habit(id: int, habit_update: schemas.HabitUpdate, db: Session = Depends(database.get_db), user_id: int = Depends(utils.get_current_user_id)):
    habit = crud.get_habit_by_id(db, id)
    if habit is None or habit.user_id != user_id:
        raise HTTPException(status_code=404, detail="Habit not found")
    habit = crud.update_habit(db, id, habit_update)
    return habit

# -------------------------
# Streak and Freeze Endpoints
# -------------------------

@router.post("/{id}/complete", response_model=dict)
def complete_habit_endpoint(id: int, db: Session = Depends(database.get_db), user_id: int = Depends(utils.get_current_user_id)):
    """Mark a habit as completed for today."""
    habit = crud.get_habit_by_id(db, id)
    if habit is None or habit.user_id != user_id:
        raise HTTPException(status_code=404, detail="Habit not found")
    
    result = crud.complete_habit(db, id, user_id)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result.get("error", "Failed to complete habit"))
    return result

@router.post("/{id}/freeze", response_model=dict)
def use_freeze_endpoint(id: int, db: Session = Depends(database.get_db), user_id: int = Depends(utils.get_current_user_id)):
    """Apply a streak freeze to a habit."""
    habit = crud.get_habit_by_id(db, id)
    if habit is None or habit.user_id != user_id:
        raise HTTPException(status_code=404, detail="Habit not found")
    
    result = crud.use_freeze(db, id, user_id)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result.get("error", "Failed to use freeze"))
    return result

@router.get("/{id}/status", response_model=schemas.HabitStatus)
def get_habit_status_endpoint(id: int, db: Session = Depends(database.get_db), user_id: int = Depends(utils.get_current_user_id)):
    """Get daily status of a habit."""
    habit_status = crud.get_habit_status(db, id, user_id)
    if habit_status is None:
        raise HTTPException(status_code=404, detail="Habit not found")
    return habit_status

