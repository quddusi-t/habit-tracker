import pytest
from app.database import Base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from fastapi.testclient import TestClient
from main import app
import uuid

# In-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db():
    # Create the database tables
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        # Drop the database tables
        Base.metadata.drop_all(bind=engine)


# ============================================================================
# API Testing Fixtures (for endpoint tests with FastAPI TestClient)
# ============================================================================

@pytest.fixture
def client():
    """FastAPI TestClient for making HTTP requests in tests"""
    return TestClient(app)


@pytest.fixture
def auth_headers(client):
    """Create a test user, login, and return Authorization headers"""
    unique_email = f"test-user-{uuid.uuid4()}@example.com"
    
    # Create user
    client.post(
        "/users/",
        json={"email": unique_email, "password": "testpass123"}
    )
    
    # Login
    login_response = client.post(
        "/auth/login",
        data={"username": unique_email, "password": "testpass123"}
    )
    
    token = login_response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def test_habit(client, auth_headers):
    """Create a test habit for the authenticated user"""
    response = client.post(
        "/habits/",
        json={
            "name": "Test Habit",
            "description": "A test habit for unit tests",
            "is_timer": True,
            "allow_manual_override": True
        },
        headers=auth_headers
    )
    return response.json()

