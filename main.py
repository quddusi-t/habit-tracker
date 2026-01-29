from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware 
from app import models, database
from app.routers import habits, habit_logs



# Create DB tables
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="Habit Tracker")

# Include routers
app.include_router(habits.router)
app.include_router(habit_logs.router)

# Set up CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"], # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Welcome to the Habit Tracker API!"}

