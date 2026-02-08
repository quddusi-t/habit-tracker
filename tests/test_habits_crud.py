"""
Tests for habit CRUD operations: Create, Read, Update, Delete
"""
from app import schemas


class TestHabitOperations:
    """Test habit read, update, and delete operations"""
    
    def test_get_habit_by_id(self, client, auth_headers, test_habit):
        """Test retrieving a specific habit by ID"""
        habit_id = test_habit["id"]
        
        response = client.get(
            f"/habits/{habit_id}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        habit_data = response.json()
        
        # Validate against schema
        habit = schemas.Habit(**habit_data)
        assert habit.id == habit_id
        assert habit.name == "Test Habit"
        assert habit.is_timer is True
    
    def test_get_all_habits(self, client, auth_headers, test_habit):
        """Test retrieving all habits for authenticated user"""
        response = client.get(
            "/habits/",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        habits_data = response.json()
        assert isinstance(habits_data, list)
        assert len(habits_data) >= 1
        
        # Validate all habits conform to schema
        habits = [schemas.Habit(**h) for h in habits_data]
        
        # Verify our test habit is in the list
        habit_ids = [h.id for h in habits]
        assert test_habit["id"] in habit_ids
    
    def test_update_habit_name(self, client, auth_headers, test_habit):
        """Test updating a habit's name"""
        habit_id = test_habit["id"]
        
        response = client.patch(
            f"/habits/{habit_id}",
            json={"name": "Updated Habit Name"},
            headers=auth_headers
        )
        
        assert response.status_code == 200
        updated_data = response.json()
        
        # Validate schema and fields
        updated_habit = schemas.Habit(**updated_data)
        assert updated_habit.name == "Updated Habit Name"
        assert updated_habit.id == habit_id
    
    def test_update_habit_description(self, client, auth_headers, test_habit):
        """Test updating a habit's description"""
        habit_id = test_habit["id"]
        
        response = client.patch(
            f"/habits/{habit_id}",
            json={"description": "New description for testing"},
            headers=auth_headers
        )
        
        assert response.status_code == 200
        updated_habit = response.json()
        assert updated_habit["description"] == "New description for testing"
    
    def test_update_habit_is_timer(self, client, auth_headers, test_habit):
        """Test updating a habit's is_timer flag"""
        habit_id = test_habit["id"]
        
        # Original is_timer is True, change to False
        response = client.patch(
            f"/habits/{habit_id}",
            json={"is_timer": False},
            headers=auth_headers
        )
        
        assert response.status_code == 200
        updated_habit = response.json()
        assert updated_habit["is_timer"] is False
    
    def test_update_habit_allow_manual_override(self, client, auth_headers, test_habit):
        """Test updating a habit's allow_manual_override flag"""
        habit_id = test_habit["id"]
        
        response = client.patch(
            f"/habits/{habit_id}",
            json={"allow_manual_override": False},
            headers=auth_headers
        )
        
        assert response.status_code == 200
        updated_habit = response.json()
        assert updated_habit["allow_manual_override"] is False
    
    def test_update_multiple_fields(self, client, auth_headers, test_habit):
        """Test updating multiple fields at once"""
        habit_id = test_habit["id"]
        
        response = client.patch(
            f"/habits/{habit_id}",
            json={
                "name": "Complete Update",
                "description": "All fields updated",
                "is_timer": False,
                "allow_manual_override": False
            },
            headers=auth_headers
        )
        
        assert response.status_code == 200
        updated_habit = response.json()
        assert updated_habit["name"] == "Complete Update"
        assert updated_habit["description"] == "All fields updated"
        assert updated_habit["is_timer"] is False
        assert updated_habit["allow_manual_override"] is False
    
    def test_delete_habit(self, client, auth_headers, test_habit):
        """Test deleting a habit"""
        habit_id = test_habit["id"]
        
        # Delete the habit
        response = client.delete(
            f"/habits/{habit_id}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        
        # Verify it's deleted by trying to fetch it
        get_response = client.get(
            f"/habits/{habit_id}",
            headers=auth_headers
        )
        
        # Should return 404 or similar
        assert get_response.status_code != 200
    
    def test_create_habit_defaults(self, client, auth_headers):
        """Test creating a habit with minimal fields uses proper defaults"""
        response = client.post(
            "/habits/",
            json={"name": "Minimal Habit"},
            headers=auth_headers
        )
        
        assert response.status_code in (200, 201)
        habit_data = response.json()
        
        # Validate schema
        habit = schemas.Habit(**habit_data)
        assert habit.name == "Minimal Habit"
        assert habit.id is not None
        assert habit.created_at is not None
        assert habit.is_timer is True  # Check default
        assert habit.allow_manual_override is True  # Check default
    
    def test_get_nonexistent_habit(self, client, auth_headers):
        """Test fetching a habit that doesn't exist"""
        response = client.get(
            "/habits/99999",
            headers=auth_headers
        )
        
        assert response.status_code == 404
    
    def test_delete_nonexistent_habit(self, client, auth_headers):
        """Test deleting a habit that doesn't exist"""
        response = client.delete(
            "/habits/99999",
            headers=auth_headers
        )
        
        assert response.status_code == 404
    
    def test_update_nonexistent_habit(self, client, auth_headers):
        """Test updating a habit that doesn't exist"""
        response = client.patch(
            "/habits/99999",
            json={"name": "Updated"},
            headers=auth_headers
        )
        
        assert response.status_code == 404
