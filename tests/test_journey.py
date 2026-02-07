from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_user_journey():
    # 1. Create user
    response = client.post(
        "/users/",
        json={"email": "journey2@example.com", "password": "secret123"}
    )
    assert response.status_code in (200, 201)
    user = response.json()
    assert "id" in user
    assert user["email"] == "journey2@example.com"

    # 2. Log in (FastAPI OAuth2PasswordRequestForm expects form data)
    login_response = client.post(
        "/auth/login",
        data={"username": "journey2@example.com", "password": "secret123"}
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]

    # 3. Create habit (authorized)
    headers = {"Authorization": f"Bearer {token}"}
    habit_response = client.post(
        "/habits/",
        json={"name": "Drink Water"},
        headers=headers
    )
    assert habit_response.status_code in (200, 201)
    habit = habit_response.json()
    assert habit["name"] == "Drink Water"

    habit_id = habit["id"]

    # 4. Fetch habit logs
    logs_response = client.get(f"/habit_logs/{habit_id}/logs", headers=headers)
    assert logs_response.status_code == 200
    logs = logs_response.json()
    assert isinstance(logs, list)
