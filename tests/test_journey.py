"""
End-to-end user journey test: signup → login → create habit → fetch logs
"""


def test_user_journey(client, auth_headers):
    """Test complete user journey through the habit tracker"""
    
    # 1. Create a custom habit (using auth_headers from signup + login)
    habit_response = client.post(
        "/habits/",
        json={"name": "Drink Water", "description": "Stay hydrated"},
        headers=auth_headers
    )
    assert habit_response.status_code in (200, 201)
    habit = habit_response.json()
    assert habit["name"] == "Drink Water"
    habit_id = habit["id"]

    # 2. Fetch habit logs for the newly created habit
    logs_response = client.get(f"/habit_logs/{habit_id}/logs", headers=auth_headers)
    assert logs_response.status_code == 200
    logs = logs_response.json()
    assert isinstance(logs, list)
