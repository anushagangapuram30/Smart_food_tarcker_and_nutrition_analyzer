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

        # 4. Cooking Method Detection (Heuristic + Context)
        cooking_method = analyzer.detect_cooking_method(file_path, food_name=food_name)

        # 5. Nutrition Data Retrieval (Comprehensive mapping based on USDA FoodData logic)
        nutrition_map = {
            "Pizza": {"calories": 285.0, "protein": 12.0, "carbs": 36.0, "fats": 10.0, "fiber": 2.5, "sugar": 3.8, "category": "Fast Food"},
            "Apple": {"calories": 52.0, "protein": 0.3, "carbs": 14.0, "fats": 0.2, "fiber": 2.4, "sugar": 10.4, "category": "Fruit"},
            "Sandwich": {"calories": 250.0, "protein": 15.0, "carbs": 30.0, "fats": 8.0, "fiber": 3.0, "sugar": 2.0, "category": "Lunch"},
            "Orange": {"calories": 47.0, "protein": 0.9, "carbs": 12.0, "fats": 0.1, "fiber": 2.4, "sugar": 9.4, "category": "Fruit"},
            "Broccoli": {"calories": 34.0, "protein": 2.8, "carbs": 7.0, "fats": 0.4, "fiber": 2.6, "sugar": 1.7, "category": "Vegetable"},
            "Carrot": {"calories": 41.0, "protein": 0.9, "carbs": 10.0, "fats": 0.2, "fiber": 2.8, "sugar": 4.7, "category": "Vegetable"},
            "Burger": {"calories": 354.0, "protein": 17.0, "carbs": 29.0, "fats": 18.0, "fiber": 1.1, "sugar": 5.0, "category": "Fast Food"},
            "Cheeseburger": {"calories": 450.0, "protein": 25.0, "carbs": 35.0, "fats": 25.0, "fiber": 1.5, "sugar": 6.0, "category": "Fast Food"},
            "Hotdog": {"calories": 290.0, "protein": 10.0, "carbs": 18.0, "fats": 20.0, "fiber": 0.8, "sugar": 2.4, "category": "Fast Food"},
            "Pasta": {"calories": 131.0, "protein": 5.0, "carbs": 25.0, "fats": 1.1, "fiber": 1.2, "sugar": 0.6, "category": "Grains"},
            "Rice": {"calories": 130.0, "protein": 2.7, "carbs": 28.0, "fats": 0.3, "fiber": 0.4, "sugar": 0.1, "category": "Grains"},
            "Salad": {"calories": 15.0, "protein": 1.0, "carbs": 3.0, "fats": 0.1, "fiber": 1.5, "sugar": 1.0, "category": "Vegetable"},
            "Cake": {"calories": 257.0, "protein": 3.0, "carbs": 43.0, "fats": 9.0, "fiber": 0.6, "sugar": 30.0, "category": "Dessert"},
            "Bread": {"calories": 265.0, "protein": 9.0, "carbs": 49.0, "fats": 3.2, "fiber": 2.7, "sugar": 5.0, "category": "Grains"},
            "Egg": {"calories": 155.0, "protein": 13.0, "carbs": 1.1, "fats": 11.0, "fiber": 0.0, "sugar": 1.1, "category": "Protein"},
            "Chicken": {"calories": 239.0, "protein": 27.0, "carbs": 0.0, "fats": 14.0, "fiber": 0.0, "sugar": 0.0, "category": "Protein"},
            "Banana": {"calories": 89.0, "protein": 1.1, "carbs": 23.0, "fats": 0.3, "fiber": 2.6, "sugar": 12.0, "category": "Fruit"},
            "Cookie": {"calories": 502.0, "protein": 4.8, "carbs": 68.0, "fats": 24.0, "fiber": 1.0, "sugar": 33.0, "category": "Dessert"},
            "Soup": {"calories": 36.0, "protein": 1.2, "carbs": 7.0, "fats": 0.5, "fiber": 0.5, "sugar": 1.5, "category": "Meal"},
            "Noodle": {"calories": 138.0, "protein": 4.5, "carbs": 25.0, "fats": 2.1, "fiber": 1.0, "sugar": 0.4, "category": "Grains"},
            "Cheese": {"calories": 402.0, "protein": 25.0, "carbs": 1.3, "fats": 33.0, "fiber": 0.0, "sugar": 0.5, "category": "Dairy"},
            "Potato": {"calories": 77.0, "protein": 2.0, "carbs": 17.0, "fats": 0.1, "fiber": 2.2, "sugar": 0.8, "category": "Vegetable"},
            "Sushi": {"calories": 350.0, "protein": 15.0, "carbs": 50.0, "fats": 5.0, "fiber": 2.0, "sugar": 4.0, "category": "Meal"},
            "Steak": {"calories": 271.0, "protein": 25.0, "carbs": 0.0, "fats": 19.0, "fiber": 0.0, "sugar": 0.0, "category": "Protein"},
            "Taco": {"calories": 226.0, "protein": 13.0, "carbs": 20.0, "fats": 11.0, "fiber": 3.0, "sugar": 1.0, "category": "Meal"},
            "Ice cream": {"calories": 207.0, "protein": 3.5, "carbs": 24.0, "fats": 11.0, "fiber": 0.7, "sugar": 21.0, "category": "Dessert"},
        }
        
        # Heuristic matching for nutrition lookup
        nutrition_info = None
        for key, val in nutrition_map.items():
            if key.lower() in food_name.lower():
                nutrition_info = val.copy()
                break
        
        if not nutrition_info:
            nutrition_info = {
                "calories": 150.0, "protein": 5.0, "carbs": 20.0, "fats": 5.0, "fiber": 1.0, "sugar": 5.0, "category": "General"
            }

        # 6. Recommendation Engine (Healthy Additions Logic)
        diet_suggestions = [f"This looks like {food_name}!"]
        
        # Specific healthy additions based on category and nutrients
        if nutrition_info["category"] == "Fast Food" or nutrition_info["fats"] > 15:
            diet_suggestions.append("Add a fresh side salad or some steamed broccoli to balance the fats.")
            diet_suggestions.append("Try adding a squeeze of lemon to aid digestion.")
        
        if nutrition_info["protein"] < 10 and nutrition_info["category"] not in ["Fruit", "Dessert"]:
            diet_suggestions.append("To make this more filling, add a protein source like a boiled egg, grilled chicken, or chickpeas.")
        
        if nutrition_info["fiber"] < 2:
            diet_suggestions.append("Boost the fiber by adding flaxseeds, chia seeds, or a side of leafy greens.")
        
        if nutrition_info["category"] == "Dessert" or nutrition_info["sugar"] > 15:
            diet_suggestions.append("Add some nuts (walnuts or almonds) to slow down sugar absorption.")
            diet_suggestions.append("Pair this with some plain Greek yogurt for added protein.")
            
        if nutrition_info["category"] == "Grains":
            diet_suggestions.append("Add colorful vegetables like bell peppers or spinach to increase micronutrients.")

        if "Fruit" in nutrition_info["category"]:
            diet_suggestions.append("Add some almond butter or Greek yogurt to make it a more balanced snack.")

        health_score = 10.0
        if nutrition_info["calories"] > 400: health_score -= 2.0
        if nutrition_info["sugar"] > 20: health_score -= 2.0
        if nutrition_info["fats"] > 20: health_score -= 1.5
        if nutrition_info["fiber"] > 3: health_score += 1.0
        if nutrition_info["protein"] > 15: health_score += 1.0
        health_score = max(min(health_score, 10.0), 1.0) # Keep between 1 and 10

        # Remove category from return to match model
        nutrition_display = {k: v for k, v in nutrition_info.items() if k != "category"}

        return {
            "food_name": food_name,
            "cooking_method": cooking_method,
            "ingredients": detected_ingredients,
            "nutrition": nutrition_display,
            "health_score": round(health_score, 1),
            "diet_suggestions": diet_suggestions
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/user-history", response_model=List[food_models.FoodAnalysisResult])
async def get_user_history(db: Session = Depends(get_db)):
    # Retrieve user's food history from the database
    # For now, return a mock list
    return []
