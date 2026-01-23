from fastapi import FastAPI
from app import models, database
from app.routers import habits

# Create DB tables
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="Habit Tracker")

# Include routers
app.include_router(habits.router)
