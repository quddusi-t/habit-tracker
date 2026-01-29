from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app import models, database

def seed_habits():
    db: Session = database.SessionLocal()

    # Check if habits already exist
    if db.query(models.Habit).count() > 0:
        print("Habits already seeded.")
        db.close()
        return

    # Create or get user
    user = db.query(models.User).filter(models.User.email == "user@example.com").first()
    if not user:
        user = models.User(
            email="user@example.com",
            created_at=datetime.now(timezone.utc)
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        print(f"Created user with ID: {user.id}")

    habits = [
        models.Habit(
            name="Learn Programming",
            description="Daily coding practice",
            is_timer=True,
            allow_manual_override=True,
            created_at=datetime.now(timezone.utc),
            user_id=user.id
        ),
        models.Habit(
            name="Meditation",
            description="Mindfulness session",
            is_timer=False,
            allow_manual_override=True,
            created_at=datetime.now(timezone.utc),
            user_id=user.id
        ),
        models.Habit(
            name="Sports Session",
            description="Quick workout",
            is_timer=False,
            allow_manual_override=True,
            created_at=datetime.now(timezone.utc),
            user_id=user.id
        ),
        models.Habit(
            name="Duolingo German",
            description="Learn German on Duolingo",
            is_timer=True,
            allow_manual_override=True,
            created_at=datetime.now(timezone.utc),
            user_id=user.id
        ),
        models.Habit(
            name="Duolingo Spanish",
            description="Learn Spanish on Duolingo",
            is_timer=True,
            allow_manual_override=True,
            created_at=datetime.now(timezone.utc),
            user_id=user.id
        ),
        models.Habit(
            name="Audiobooks Walk",
            description="Listen to audiobooks while walking",
            is_timer=True,
            allow_manual_override=True,
            created_at=datetime.now(timezone.utc),
            user_id=user.id
        ),
    ]

    db.add_all(habits)
    db.commit()
    db.close()
    print("Habits seeded successfully!")

if __name__ == "__main__":
    seed_habits()
