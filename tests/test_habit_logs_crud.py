"""
Tests for habit logging start/stop lifecycle via API endpoints
"""
import time


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
        assert start_response.status_code in (200, 201)
        log = start_response.json()
        log_id = log["id"]
        assert log["start_time"] is not None
        assert log["end_time"] is None
        assert log["duration_min"] is None
        
        # 2. Wait a bit (simulate active logging)
        time.sleep(0.1)
        
        # 3. Stop the logging session
        stop_response = client.patch(
            f"/habit_logs/{habit_id}/logs/{log_id}/stop",
            headers=auth_headers
        )
        assert stop_response.status_code == 200
        stopped_log = stop_response.json()
        assert stopped_log["end_time"] is not None
        assert stopped_log["duration_min"] is not None
        assert stopped_log["duration_min"] >= 0
    
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
        logs = logs_response.json()
        
        # 3. Verify the log is there with correct data
        assert isinstance(logs, list)
        assert len(logs) >= 1
        
        our_log = next((l for l in logs if l["id"] == log_id), None)
        assert our_log is not None
        assert our_log["end_time"] is not None
        assert our_log["duration_min"] is not None
