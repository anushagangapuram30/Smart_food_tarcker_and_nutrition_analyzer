from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import models, schema
from ..database.connection import get_db

router = APIRouter()

@router.get("/profile", response_model=models.food.UserProfile)
async def get_profile(db: Session = Depends(get_db)):
    # Retrieve user profile from the database
    # For now, return a mock profile
    return {
        "age": 25,
        "weight": 70.0,
        "height": 175.0,
        "diet_type": "Vegetarian"
    }

@router.put("/profile", response_model=models.food.UserProfile)
async def update_profile(profile: models.food.UserProfile, db: Session = Depends(get_db)):
    # Update user profile in the database
    # Return the updated profile
    return profile
