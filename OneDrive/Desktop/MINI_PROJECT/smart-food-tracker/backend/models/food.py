from pydantic import BaseModel
from typing import List, Optional

class Ingredient(BaseModel):
    name: str
    confidence: float

class NutritionInfo(BaseModel):
    calories: float
    protein: float
    carbs: float
    fats: float
    fiber: float
    sugar: float

class FoodAnalysisResult(BaseModel):
    food_name: str
    cooking_method: str
    ingredients: List[Ingredient]
    nutrition: NutritionInfo
    health_score: float
    diet_suggestions: List[str]

class UserProfile(BaseModel):
    age: int
    weight: float
    height: float
    diet_type: str