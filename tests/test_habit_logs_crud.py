"""
Tests for habit logging start/stop lifecycle via API endpoints
"""
from fastapi.testclient import TestClient
from main import app
import time
import uuid

client = TestClient(app)


class TestLoggingLifecycle:
    """Test the complete start -> stop logging cycle"""
    
    def test_full_logging_session_api(self):
        """Test complete logging session through API: create user, habit, start/stop log"""
        # 1. Create a unique user
        unique_email = f"log-test-{uuid.uuid4()}@example.com"
        user_response = client.post(
            "/users/",
            json={"email": unique_email, "password": "testpass123"}
        )
        assert user_response.status_code == 200
        user = user_response.json()
        user_id = user["id"]
        
        # 2. Login to get token
        login_response = client.post(
            "/auth/login",
            data={"username": unique_email, "password": "testpass123"}
        )
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # 3. Create a habit
        habit_response = client.post(
            "/habits/",
            json={
                "name": "Test Logging Habit",
                "description": "For testing start/stop",
                "is_timer": True,
                "allow_manual_override": True
            },
            headers=headers
        )
        assert habit_response.status_code in (200, 201)
        habit = habit_response.json()
        habit_id = habit["id"]
        
        # 4. Start a logging session
        start_response = client.post(
            f"/habit_logs/{habit_id}/logs/start",
            headers=headers
        )
        assert start_response.status_code in (200, 201)
        log = start_response.json()
        log_id = log["id"]
        assert log["start_time"] is not None
        assert log["end_time"] is None
        assert log["duration_min"] is None
        
        # 5. Wait a bit (simulate active logging)
        time.sleep(0.1)
        
        # 6. Stop the logging session
        stop_response = client.patch(
            f"/habit_logs/{habit_id}/logs/{log_id}/stop",
            headers=headers
        )
        assert stop_response.status_code == 200
        stopped_log = stop_response.json()
        assert stopped_log["end_time"] is not None
        assert stopped_log["duration_min"] is not None
        assert stopped_log["duration_min"] >= 0
    
    def test_get_habit_logs_after_logging(self):
        """Test fetching habit logs after creating and stopping a log"""
        # Setup
        unique_email = f"log-fetch-{uuid.uuid4()}@example.com"
        user_response = client.post(
            "/users/",
            json={"email": unique_email, "password": "testpass123"}
        )
        user = user_response.json()
        
        login_response = client.post(
            "/auth/login",
            data={"username": unique_email, "password": "testpass123"}
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        habit_response = client.post(
            "/habits/",
            json={
                "name": "Fetchable Habit",
                "is_timer": True,
                "allow_manual_override": True
            },
            headers=headers
        )
        habit_id = habit_response.json()["id"]
        
        # Create and stop a log
        start_response = client.post(
            f"/habit_logs/{habit_id}/logs/start",
            headers=headers
        )
        log_id = start_response.json()["id"]
        
        time.sleep(0.05)
        
        stop_response = client.patch(
            f"/habit_logs/{habit_id}/logs/{log_id}/stop",
            headers=headers
        )
        assert stop_response.status_code == 200
        
        # Now fetch all logs for this habit
        logs_response = client.get(
            f"/habit_logs/{habit_id}/logs",
            headers=headers
        )
        assert logs_response.status_code == 200
        logs = logs_response.json()
        
        # Should have at least the log we just created
        assert isinstance(logs, list)
        assert len(logs) >= 1
        
        # Find our log in the list
        our_log = next((l for l in logs if l["id"] == log_id), None)
        assert our_log is not None
        assert our_log["end_time"] is not None
        assert our_log["duration_min"] is not None
