from app import crud, schemas

def test_create_user_success(db):
    user_data = schemas.UserCreate(email="test@example.com", password="secret123")
    new_user = crud.create_user(db, user_data)
    assert new_user is not None
    assert new_user.email == "test@example.com"
    assert hasattr(new_user, "id")
    # Password should be hashed, not equal to raw
    assert new_user.hashed_password != "secret123"

def test_create_user_duplicate_email(db):
    user_data = schemas.UserCreate(email="dup@example.com", password="secret123")
    first_user = crud.create_user(db, user_data)
    assert first_user is not None

    duplicate_user = crud.create_user(db, user_data)
    assert duplicate_user is None
    


