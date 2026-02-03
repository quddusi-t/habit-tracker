from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app import models, schemas, utils
from app.database import get_db

router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

@router.post("/login", response_model=schemas.Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(), 
    db: Session = Depends(get_db)
    ):
    # 1. Find user by email
    # form_data.username is used even if the field is technically an email
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            # This header is the 'cherry on top' for HTTP standards
            headers={"WWW-Authenticate": "Bearer"}
        )

    # 2. Verify password
    if not utils.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"}
        )

    # 3. Create token
    access_token = utils.create_access_token(
        data={"sub": str(user.id)}
    )

    # 4. Return token
    return {"access_token": access_token, "token_type": "bearer"}


