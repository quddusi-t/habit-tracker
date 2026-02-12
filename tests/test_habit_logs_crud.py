"""
Tests for habit logging start/stop lifecycle via API endpoints
"""
import time
from app import schemas


class TestLoggingLifecycle:
    """Test the complete start -> stop logging cycle"""
    
    def test_full_logging_session_api(self, client, auth_headers, test_habit):
        """Test complete logging session: start → stop with duration calculation"""
        habit_id = test_habit["id"]
        
        # 1. Start a logging session
        start_response = client.post(
            f"/habit_logs/{habit_id}/logs/start",
            headers=auth_headers
        )
        assert start_response.status_code == 201
        log_data = start_response.json()
        log_id = log_data["id"]
        
        # Validate response schema and fields
        log = schemas.HabitLog(**log_data)
        assert log.id == log_id
        assert log.habit_id == habit_id
        assert log.start_time is not None
        assert log.end_time is None
        assert log.duration_min is None
        assert log.is_manual is False
        
        # 2. Wait a bit (simulate active logging)
        time.sleep(0.1)
        
        # 3. Stop the logging session
        stop_response = client.patch(
            f"/habit_logs/{habit_id}/logs/{log_id}/stop",
            headers=auth_headers
        )
        assert stop_response.status_code == 200
        stopped_log_data = stop_response.json()
        
        # Validate stopped log schema and fields
        stopped_log = schemas.HabitLog(**stopped_log_data)
        assert stopped_log.id == log_id
        assert stopped_log.habit_id == habit_id
        assert stopped_log.end_time is not None
        assert stopped_log.duration_min is not None
        assert stopped_log.duration_min >= 0
        assert stopped_log.start_time < stopped_log.end_time
    
    def test_get_habit_logs_after_logging(self, client, auth_headers, test_habit):
        """Test fetching habit logs after creating and stopping a log"""
        habit_id = test_habit["id"]
        
        # 1. Create and stop a log
        start_response = client.post(
            f"/habit_logs/{habit_id}/logs/start",
            headers=auth_headers
        )
        log_id = start_response.json()["id"]
        
        time.sleep(0.05)
        
        stop_response = client.patch(
            f"/habit_logs/{habit_id}/logs/{log_id}/stop",
            headers=auth_headers
        )
        assert stop_response.status_code == 200
        
        # 2. Fetch all logs for this habit
        logs_response = client.get(
            f"/habit_logs/{habit_id}/logs",
            headers=auth_headers
        )
        assert logs_response.status_code == 200
        logs_data = logs_response.json()
        
        # 3. Verify response is a list of HabitLog objects
        assert isinstance(logs_data, list)
        assert len(logs_data) >= 1
        
        # Validate all items match schema
        validated_logs = [schemas.HabitLog(**log) for log in logs_data]
        
        # Find our log and verify it
        our_log = next((log for log in validated_logs if log.id == log_id), None)
        assert our_log is not None
        assert our_log.habit_id == habit_id
        assert our_log.end_time is not None
        assert our_log.duration_min is not None

    def test_multiple_sessions_same_day_increment_once(self, client, auth_headers, test_habit):
        """Multiple timer sessions in a day should count as one completion."""
        habit_id = test_habit["id"]

        # First session
        start_response = client.post(
            f"/habit_logs/{habit_id}/logs/start",
            headers=auth_headers
        )
        log_id = start_response.json()["id"]

        time.sleep(0.05)

        stop_response = client.patch(
            f"/habit_logs/{habit_id}/logs/{log_id}/stop",
            headers=auth_headers
        )
        assert stop_response.status_code == 200

        habit_response = client.get(f"/habits/{habit_id}", headers=auth_headers)
        habit = schemas.Habit(**habit_response.json())
        assert habit.current_streak == 1

        # Second session same day
        start_response = client.post(
            f"/habit_logs/{habit_id}/logs/start",
            headers=auth_headers
        )
        log_id = start_response.json()["id"]

        time.sleep(0.05)

        stop_response = client.patch(
            f"/habit_logs/{habit_id}/logs/{log_id}/stop",
            headers=auth_headers
        )
        assert stop_response.status_code == 200

        habit_response = client.get(f"/habits/{habit_id}", headers=auth_headers)
        habit = schemas.Habit(**habit_response.json())
        assert habit.current_streak == 1

        status_response = client.get(f"/habits/{habit_id}/status", headers=auth_headers)
        assert status_response.status_code == 200
        status = status_response.json()
        assert status["status"] == "completed"
