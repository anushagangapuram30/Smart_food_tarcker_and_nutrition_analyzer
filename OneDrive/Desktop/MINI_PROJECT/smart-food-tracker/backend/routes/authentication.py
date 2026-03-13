from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from models import user as user_models
from database import schema
from database.connection import get_db
from security import create_access_token, verify_password, get_password_hash

router = APIRouter()

@router.post("/register", response_model=user_models.UserOut)
def register(user: user_models.UserCreate, db: Session = Depends(get_db)):
    # Check if email is already registered
    db_user_email = db.query(schema.User).filter(schema.User.email == user.email).first()
    if db_user_email:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Check if username is already taken
    db_user_username = db.query(schema.User).filter(schema.User.username == user.username).first()
    if db_user_username:
        raise HTTPException(status_code=400, detail="Username already taken")
    
    hashed_password = get_password_hash(user.password)
    db_user = schema.User(email=user.email, hashed_password=hashed_password, username=user.username)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@router.post("/login", response_model=user_models.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(schema.User).filter(schema.User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(
        data={"sub": user.username}
    )
    return {"access_token": access_token, "token_type": "bearer"}
