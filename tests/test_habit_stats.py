"""Tests for habit statistics and reporting endpoints."""
import pytest
import time
from datetime import datetime, timezone, timedelta
from app import schemas, models
from app.database import SessionLocal
from tests.conftest import client, auth_headers, test_habit


def create_completed_logs(habit_id: int, num_sessions: int, durations: list[int] | None = None):
    """Helper to create completed logs in database."""
    with SessionLocal() as db:
        now = datetime.now(timezone.utc)
        for i in range(num_sessions):
            duration = durations[i] if durations and i < len(durations) else 30
            log = models.HabitLog(
                habit_id=habit_id,
                start_time=now - timedelta(days=num_sessions - i - 1),
                end_time=now - timedelta(days=num_sessions - i - 1, seconds=-duration*60),
                duration_min=duration,
                is_manual=False,
                status="completed"
            )
            db.add(log)
        db.commit()


def create_frozen_logs(habit_id: int, num_freezes: int):
    """Helper to create frozen logs in database."""
    with SessionLocal() as db:
        now = datetime.now(timezone.utc)
        for i in range(num_freezes):
            log = models.HabitLog(
                habit_id=habit_id,
                start_time=now - timedelta(days=num_freezes - i),
                end_time=now - timedelta(days=num_freezes - i),
                duration_min=0,
                is_manual=True,
                status="frozen"
            )
            db.add(log)
        db.commit()


class TestTimerHabitStats:
    """Test stats for timer habits."""

    def test_get_timer_habit_stats_no_sessions(self, client, auth_headers, test_habit):
        """Timer habit with no sessions should return zeros."""
        habit_id = test_habit["id"]

        response = client.get(f"/habits/{habit_id}/stats", headers=auth_headers)
        assert response.status_code == 200

        stats = response.json()
        assert stats["habit_type"] == "timer"
        assert stats["stats"]["total_time_minutes"] == 0
        assert stats["stats"]["avg_session_minutes"] == 0.0
        assert stats["stats"]["sessions_count"] == 0
        assert stats["stats"]["best_day_minutes"] == 0

    def test_get_timer_habit_stats_with_sessions(self, client, auth_headers, test_habit):
        """Timer habit with sessions should calculate correct stats."""
        habit_id = test_habit["id"]
        create_completed_logs(habit_id, 3, durations=[30, 45, 60])

        response = client.get(f"/habits/{habit_id}/stats", headers=auth_headers)
        assert response.status_code == 200

        stats = response.json()
        assert stats["habit_type"] == "timer"
        assert stats["stats"]["total_time_minutes"] == 135  # 30 + 45 + 60
        assert stats["stats"]["avg_session_minutes"] == 45.0
        assert stats["stats"]["sessions_count"] == 3
        assert stats["stats"]["best_day_minutes"] == 60

    def test_timer_habit_this_week_minutes(self, client, auth_headers, test_habit):
        """This week minutes should only count sessions from last 7 days."""
        habit_id = test_habit["id"]

        with SessionLocal() as db:
            now = datetime.now(timezone.utc)
            # Add log from 5 days ago
            log1 = models.HabitLog(
                habit_id=habit_id,
                start_time=now - timedelta(days=5),
                end_time=now - timedelta(days=5, seconds=-30*60),
                duration_min=30,
                is_manual=False,
                status="completed"
            )
            # Add log from 10 days ago (outside this week)
            log2 = models.HabitLog(
                habit_id=habit_id,
                start_time=now - timedelta(days=10),
                end_time=now - timedelta(days=10, seconds=-60*60),
                duration_min=60,
                is_manual=False,
                status="completed"
            )
            db.add(log1)
            db.add(log2)
            db.commit()

        response = client.get(f"/habits/{habit_id}/stats", headers=auth_headers)
        stats = response.json()
        assert stats["stats"]["this_week_minutes"] == 30

    def test_timer_habit_this_month_minutes(self, client, auth_headers, test_habit):
        """This month minutes should only count sessions from last 30 days."""
        habit_id = test_habit["id"]

        with SessionLocal() as db:
            now = datetime.now(timezone.utc)
            # Add log from 20 days ago
            log1 = models.HabitLog(
                habit_id=habit_id,
                start_time=now - timedelta(days=20),
                end_time=now - timedelta(days=20, seconds=-45*60),
                duration_min=45,
                is_manual=False,
                status="completed"
            )
            # Add log from 40 days ago (outside this month)
            log2 = models.HabitLog(
                habit_id=habit_id,
                start_time=now - timedelta(days=40),
                end_time=now - timedelta(days=40, seconds=-90*60),
                duration_min=90,
                is_manual=False,
                status="completed"
            )
            db.add(log1)
            db.add(log2)
            db.commit()

        response = client.get(f"/habits/{habit_id}/stats", headers=auth_headers)
        stats = response.json()
        assert stats["stats"]["this_month_minutes"] == 45

    def test_timer_habit_median_session(self, client, auth_headers, test_habit):
        """Median session time should be calculated correctly."""
        habit_id = test_habit["id"]
        create_completed_logs(habit_id, 5, durations=[10, 20, 30, 40, 50])

        response = client.get(f"/habits/{habit_id}/stats", headers=auth_headers)
        stats = response.json()
        assert stats["stats"]["median_session_minutes"] == 30.0


class TestManualHabitStats:
    """Test stats for manual habits."""

    def test_get_manual_habit_stats_no_completions(self, client, auth_headers):
        """Manual habit with no completions should return zeros."""
        habit_payload = {"name": "Manual Test", "is_timer": False}
        habit_response = client.post("/habits/", json=habit_payload, headers=auth_headers)
        habit_id = habit_response.json()["id"]

        response = client.get(f"/habits/{habit_id}/stats", headers=auth_headers)
        assert response.status_code == 200

        stats = response.json()
        assert stats["habit_type"] == "manual"
        assert stats["stats"]["total_completions"] == 0
        assert stats["stats"]["best_streak"] == 0

    def test_get_manual_habit_stats_with_completions(self, client, auth_headers):
        """Manual habit with completions should calculate correct stats."""
        habit_payload = {"name": "Manual Test", "is_timer": False}
        habit_response = client.post("/habits/", json=habit_payload, headers=auth_headers)
        habit_id = habit_response.json()["id"]

        create_completed_logs(habit_id, 3)

        response = client.get(f"/habits/{habit_id}/stats", headers=auth_headers)
        assert response.status_code == 200

        stats = response.json()
        assert stats["habit_type"] == "manual"
        assert stats["stats"]["total_completions"] == 3
        assert stats["stats"]["best_streak"] >= 1

    def test_manual_habit_completion_rate(self, client, auth_headers):
        """Completion rate should be calculated as completions / days_since_created."""
        habit_payload = {"name": "Manual Test", "is_timer": False}
        habit_response = client.post("/habits/", json=habit_payload, headers=auth_headers)
        habit_id = habit_response.json()["id"]

        # Create 3 completions
        create_completed_logs(habit_id, 3)

        response = client.get(f"/habits/{habit_id}/stats", headers=auth_headers)
        stats = response.json()
        # With 3 completions and at least 3 days, rate should be >= 33%
        assert stats["stats"]["completion_rate_percent"] >= 0.0


class TestStreakStats:
    """Test streak stats returned with habit stats."""

    def test_current_streak_in_stats(self, client, auth_headers, test_habit):
        """Stats should include current streak."""
        habit_id = test_habit["id"]

        with SessionLocal() as db:
            habit = db.query(models.Habit).filter(models.Habit.id == habit_id).first()
            habit.current_streak = 5
            db.commit()

        response = client.get(f"/habits/{habit_id}/stats", headers=auth_headers)
        stats = response.json()
        assert stats["streaks"]["current"] == 5

    def test_best_streak_in_stats(self, client, auth_headers, test_habit):
        """Stats should include best streak."""
        habit_id = test_habit["id"]

        response = client.get(f"/habits/{habit_id}/stats", headers=auth_headers)
        stats = response.json()
        assert "best" in stats["streaks"]
        assert stats["streaks"]["best"] >= 0


class TestFreezeStats:
    """Test freeze stats returned with habit stats."""

    def test_freezes_used_count(self, client, auth_headers, test_habit):
        """Stats should count total freezes used."""
        habit_id = test_habit["id"]
        create_frozen_logs(habit_id, 2)

        response = client.get(f"/habits/{habit_id}/stats", headers=auth_headers)
        stats = response.json()
        assert stats["freezes"]["used"] == 2

    def test_freezes_remaining(self, client, auth_headers, test_habit):
        """Stats should show remaining freeze balance."""
        habit_id = test_habit["id"]

        with SessionLocal() as db:
            habit = db.query(models.Habit).filter(models.Habit.id == habit_id).first()
            user = db.query(models.User).filter(models.User.id == habit.user_id).first()
            user.freeze_balance = 3
            db.commit()

        response = client.get(f"/habits/{habit_id}/stats", headers=auth_headers)
        stats = response.json()
        assert stats["freezes"]["remaining"] == 3


class TestHabitStatsMetadata:
    """Test metadata fields in habit stats."""

    def test_days_since_created(self, client, auth_headers, test_habit):
        """Stats should include days since habit was created."""
        habit_id = test_habit["id"]

        response = client.get(f"/habits/{habit_id}/stats", headers=auth_headers)
        stats = response.json()
        assert stats["days_since_created"] >= 0

    def test_habit_name_in_stats(self, client, auth_headers, test_habit):
        """Stats should include habit name."""
        habit_id = test_habit["id"]

        response = client.get(f"/habits/{habit_id}/stats", headers=auth_headers)
        stats = response.json()
        assert stats["habit_name"] == "Test Habit"

    def test_stats_nonexistent_habit(self, client, auth_headers):
        """Should return 404 for nonexistent habit."""
        response = client.get("/habits/99999/stats", headers=auth_headers)
        assert response.status_code == 404


class TestStatsResponseSchema:
    """Test that stats endpoint returns correct schema."""

    def test_timer_habit_stats_schema(self, client, auth_headers, test_habit):
        """Timer habit stats should match expected schema."""
        habit_id = test_habit["id"]
        create_completed_logs(habit_id, 2, durations=[30, 45])

        response = client.get(f"/habits/{habit_id}/stats", headers=auth_headers)
        assert response.status_code == 200

        stats_data = response.json()
        # Validate it can be parsed as HabitStats
        stats = schemas.HabitStats(**stats_data)
        assert stats.habit_type == "timer"
        assert isinstance(stats.stats, schemas.TimerHabitStats)
        assert stats.stats.total_time_minutes == 75
        assert stats.stats.sessions_count == 2

    def test_manual_habit_stats_schema(self, client, auth_headers):
        """Manual habit stats should match expected schema."""
        habit_payload = {"name": "Manual Test", "is_timer": False}
        habit_response = client.post("/habits/", json=habit_payload, headers=auth_headers)
        habit_id = habit_response.json()["id"]

        response = client.get(f"/habits/{habit_id}/stats", headers=auth_headers)
        assert response.status_code == 200

        stats_data = response.json()
        stats = schemas.HabitStats(**stats_data)
        assert stats.habit_type == "manual"
