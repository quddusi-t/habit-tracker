# Habit Tracker Backend

This is the **backend service** for the Habit Tracker project, built with **FastAPI**.  
It provides RESTful APIs to manage habits, track progress, and serve data to the React frontend.

## Features

- 🚀 FastAPI framework for high performance
- 📊 Endpoints to create, update, and delete habits
- ⏱️ Tracks habit progress and timing
- 🔗 Designed to integrate seamlessly with the [Habit Tracker UI](https://github.com/quddusi-t/habit-tracker-ui)

## Project Structure

habit-tracker/
├── app/
│ ├── main.py # FastAPI entry point
│ ├── models.py # Database models
│ ├── routes/ # API endpoints
│ └── ...
├── requirements.txt # Python dependencies
└── README.md

## Getting Started

### 1. Clone the repo

```bash
git clone https://github.com/quddusi-t/habit-tracker.git
cd habit-tracker

```

2. Create a virtual environment
   python -m venv venv
   source venv/bin/activate # Linux/Mac
   venv\Scripts\activate # Windows

3. Install dependencies
   pip install -r requirements.txt

4. Run the server
   uvicorn app.main:app --reload

The API will be available at:
👉 http://127.0.0.1:8000

## Related Repositories

- **Frontend (React):** [Habit Tracker UI](https://github.com/quddusi-t/habit-tracker-ui)
