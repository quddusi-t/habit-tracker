# Habit Tracker API

A **production-ready** FastAPI backend for habit tracking with **JWT authentication**, **streak tracking**, and **freeze system** (Duolingo-style gamification).

## ✨ Features

- 🔐 **JWT Authentication** - Secure user registration and login
- 📊 **Habit Management** - Create, update, delete, and track habits
- ⏱️ **Session Logging** - Start/stop timed habit sessions
- 🔥 **Streak Tracking** - Earn consecutive day streaks
- ❄️ **Streak Freezes** - Earn freezes every 7 days, use max 2 in a row
- ⚠️ **Danger Windows** - Habits become "in danger" based on time of day
- 🎨 **Color Aging** - Visual feedback (yellow → orange → red) as day progresses
- ✅ **85% Test Coverage** - 36 comprehensive tests with pytest
- 🗄️ **PostgreSQL** - Production database with Alembic migrations

## 🚀 Tech Stack

- **FastAPI** - Modern async web framework
- **PostgreSQL** - Relational database
- **SQLAlchemy** - ORM for database interactions
- **Alembic** - Database migrations
- **JWT** - Secure token-based authentication
- **pytest** - Testing framework with 85% coverage
- **Pydantic** - Data validation with schemas

## 📁 Project Structure

```
habit-tracker/
├── app/
│   ├── __init__.py
│   ├── crud.py              # Database operations
│   ├── database.py          # Database connection
│   ├── models.py            # SQLAlchemy models
│   ├── schemas.py           # Pydantic schemas
│   ├── utils.py             # JWT & auth utilities
│   └── routers/
│       ├── auth.py          # Login endpoints
│       ├── habits.py        # Habit CRUD + streak/freeze
│       ├── habit_logs.py    # Session logging
│       └── users.py         # User management
├── alembic/                 # Database migrations
├── tests/                   # Test suite (36 tests)
├── main.py                  # FastAPI app entry point
├── requirements.txt
└── .env                     # Environment variables (not tracked)
```

## ⚙️ Setup

### 1. Clone & Install

```bash
git clone https://github.com/quddusi-t/habit-tracker.git
cd habit-tracker
python -m venv venv
venv\Scripts\activate       # Windows
source venv/bin/activate    # Linux/Mac
pip install -r requirements.txt
```

### 2. Configure Environment

Create a `.env` file:

```env
DATABASE_URL=postgresql://user:password@localhost/habit_tracker
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### 3. Run Migrations

```bash
alembic upgrade head
```

### 4. Start Server

```bash
uvicorn main:app --reload
```

API available at: **http://127.0.0.1:8000**  
Interactive docs: **http://127.0.0.1:8000/docs**

## 🧪 Testing

```bash
# Run all tests
pytest tests/

# With coverage report
pytest tests/ --cov=app --cov-report=term-missing
```

**Current Coverage: 85%** (440 statements, 67 missed)

## 📖 API Endpoints

### Authentication

- `POST /auth/login` - Login and get JWT token

### Users

- `POST /users/` - Register new user
- `GET /users/{id}` - Get user details

### Habits

- `GET /habits/` - List all user's habits
- `POST /habits/` - Create new habit
- `GET /habits/{id}` - Get habit by ID
- `PATCH /habits/{id}` - Update habit
- `DELETE /habits/{id}` - Delete habit
- `POST /habits/{id}/complete` - Mark habit complete (increment streak)
- `POST /habits/{id}/freeze` - Use a streak freeze
- `GET /habits/{id}/status` - Get daily status (color, danger, streak)

### Habit Logs

- `POST /habit_logs/{habit_id}/logs/start` - Start timed session
- `PATCH /habit_logs/{habit_id}/logs/{log_id}/stop` - Stop session
- `GET /habit_logs/{habit_id}/logs` - Get all logs for habit

## 🎮 Gamification Rules

### Streaks

- Complete a habit daily to maintain streak
- Streaks reset if you miss a day (unless using a freeze)

### Freezes

- Earn 1 freeze for every **7-day streak**
- Max freeze balance: **2**
- Can use max **2 freezes in a row**
- Freezes only work on habits with `is_freezable: true`

### Danger & Colors

- Habits show `in_danger: true` when past `danger_start_pct` (default 70% of day)
- Colors: **yellow** (early) → **orange** (midday) → **red** (late) → **green** (completed) → **blue** (frozen)

## 🔗 Related Repositories

- **Frontend (React):** [Habit Tracker UI](https://github.com/quddusi-t/habit-tracker-ui)

The frontend and backend work seamlessly together — just run both locally and the UI will call the API endpoints.

## 🔜 Coming Soon

- Motivation quotes API
- Daily/weekly statistics dashboard
- Mobile notifications
- Email reminders

---

Made with ☕ and late-night coding sessions
