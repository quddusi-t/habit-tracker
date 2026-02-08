from fastapi.testclient import TestClient
from main import app
import uuid

client = TestClient(app)

def test_create_user_endpoint():
    # Use unique email to avoid conflicts on repeated test runs
    unique_email = f"clienttest-{uuid.uuid4()}@example.com"
    
    response = client.post(
        "/users/", 
        json={"email": unique_email, "password": "secret123"}
        )

    # Check HTTP response status
    assert response.status_code == 201

    data = response.json()
    # Validate response data
    assert data["email"] == unique_email
    assert "id" in data
    assert "created_at" in data
    assert "hashed_password" not in data  # Ensure password is not exposed


