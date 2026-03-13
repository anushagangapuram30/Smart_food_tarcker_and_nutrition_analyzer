from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import os
import shutil
import cv2
import numpy as np
import sys

# Add parent directory to sys.path to import ai_models
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from ai_models.food_analyzer import FoodAnalyzer

from models import food as food_models
from database import schema
from database.connection import get_db

router = APIRouter()

# Initialize FoodAnalyzer once
analyzer = FoodAnalyzer()

# Directory to save uploaded images
UPLOAD_DIR = "uploads"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

# USDA API Key Placeholder
USDA_API_KEY = "DEMO_KEY"

@router.post("/upload-food-image", response_model=food_models.FoodAnalysisResult)
async def upload_food_image(file: UploadFile = File(...), db: Session = Depends(get_db)):
    # Save the file
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        # 1. Image Preprocessing (Done inside analyzer methods)
        
        # 2. Ingredient Detection (Actual YOLOv8)
        detected_ingredients = analyzer.detect_ingredients(file_path)

        # 3. Food Classification (Actual ResNet50)
        food_name = analyzer.classify_food(file_path)

        # 4. Cooking Method Detection (Heuristic)
        cooking_method = analyzer.detect_cooking_method(file_path)

        # 5. Nutrition Data Retrieval (Enhanced mapping based on detected food)
        nutrition_map = {
            "Pizza": {"calories": 285.0, "protein": 12.0, "carbs": 36.0, "fats": 10.0, "fiber": 2.5, "sugar": 3.8},
            "Apple": {"calories": 52.0, "protein": 0.3, "carbs": 14.0, "fats": 0.2, "fiber": 2.4, "sugar": 10.4},
            "Sandwich": {"calories": 250.0, "protein": 15.0, "carbs": 30.0, "fats": 8.0, "fiber": 3.0, "sugar": 2.0},
            "Orange": {"calories": 47.0, "protein": 0.9, "carbs": 12.0, "fats": 0.1, "fiber": 2.4, "sugar": 9.4},
            "Broccoli": {"calories": 34.0, "protein": 2.8, "carbs": 7.0, "fats": 0.4, "fiber": 2.6, "sugar": 1.7},
            "Carrot": {"calories": 41.0, "protein": 0.9, "carbs": 10.0, "fats": 0.2, "fiber": 2.8, "sugar": 4.7},
            "Burger": {"calories": 354.0, "protein": 17.0, "carbs": 29.0, "fats": 18.0, "fiber": 1.1, "sugar": 5.0},
            "Hotdog": {"calories": 290.0, "protein": 10.0, "carbs": 18.0, "fats": 20.0, "fiber": 0.8, "sugar": 2.4},
            "Pasta": {"calories": 131.0, "protein": 5.0, "carbs": 25.0, "fats": 1.1, "fiber": 1.2, "sugar": 0.6},
            "Rice": {"calories": 130.0, "protein": 2.7, "carbs": 28.0, "fats": 0.3, "fiber": 0.4, "sugar": 0.1},
            "Salad": {"calories": 15.0, "protein": 1.0, "carbs": 3.0, "fats": 0.1, "fiber": 1.5, "sugar": 1.0},
            "Cake": {"calories": 257.0, "protein": 3.0, "carbs": 43.0, "fats": 9.0, "fiber": 0.6, "sugar": 30.0},
        }
        
        # Heuristic matching for nutrition lookup
        nutrition_info = None
        for key, val in nutrition_map.items():
            if key.lower() in food_name.lower():
                nutrition_info = val
                break
        
        if not nutrition_info:
            nutrition_info = {
                "calories": 150.0,
                "protein": 5.0,
                "carbs": 20.0,
                "fats": 5.0,
                "fiber": 1.0,
                "sugar": 5.0
            }

        # 6. Recommendation Engine
        diet_suggestions = [
            f"Enjoy your {food_name.lower()}!",
            "Consider adding some greens if not already present."
        ]
        health_score = 6.5 if nutrition_info["calories"] > 200 else 8.5

        return {
            "food_name": food_name,
            "cooking_method": cooking_method,
            "ingredients": detected_ingredients,
            "nutrition": nutrition_info,
            "health_score": health_score,
            "diet_suggestions": diet_suggestions
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/user-history", response_model=List[food_models.FoodAnalysisResult])
async def get_user_history(db: Session = Depends(get_db)):
    # Retrieve user's food history from the database
    # For now, return a mock list
    return []
