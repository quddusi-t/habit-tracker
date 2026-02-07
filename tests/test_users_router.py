from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_create_user_endpoint():
    response = client.post(
        "/users/", 
        json={"email": "clienttest3@example.com", "password": "secret123"}
        )

    # Check HTTP response status
    assert response.status_code == 200

    data = response.json()
    # Validate response data
    assert data["email"] == "clienttest3@example.com"
    assert "id" in data
    assert "created_at" in data
    assert "hashed_password" not in data  # Ensure password is not exposed


