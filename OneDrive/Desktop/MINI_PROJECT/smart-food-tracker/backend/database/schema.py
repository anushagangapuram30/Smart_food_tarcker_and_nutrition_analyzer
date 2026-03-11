from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    profile = Column(JSON)  # Store age, weight, height, diet_type
    food_history = relationship("FoodHistory", back_populates="user")

class FoodImage(Base):
    __tablename__ = 'food_images'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    image_path = Column(String)
    upload_time = Column(DateTime, default=datetime.datetime.utcnow)
    food_history = relationship("FoodHistory", back_populates="food_image")

class DetectedIngredient(Base):
    __tablename__ = 'detected_ingredients'

    id = Column(Integer, primary_key=True, index=True)
    food_history_id = Column(Integer, ForeignKey('food_history.id'))
    ingredient_name = Column(String)
    confidence_score = Column(Float)

class NutritionResult(Base):
    __tablename__ = 'nutrition_results'

    id = Column(Integer, primary_key=True, index=True)
    food_history_id = Column(Integer, ForeignKey('food_history.id'))
    calories = Column(Float)
    protein = Column(Float)
    carbs = Column(Float)
    fats = Column(Float)
    fiber = Column(Float)
    sugar = Column(Float)

class DietRecommendation(Base):
    __tablename__ = 'diet_recommendations'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    recommendation_text = Column(String)
    creation_time = Column(DateTime, default=datetime.datetime.utcnow)

class FoodHistory(Base):
    __tablename__ = 'food_history'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    food_image_id = Column(Integer, ForeignKey('food_images.id'))
    food_name = Column(String)
    cooking_method = Column(String)
    creation_time = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", back_populates="food_history")
    food_image = relationship("FoodImage", back_populates="food_history")
    ingredients = relationship("DetectedIngredient")
    nutrition = relationship("NutritionResult")
