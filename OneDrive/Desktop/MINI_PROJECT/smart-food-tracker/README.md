# Smart Food Tracker and Nutrition Analyzer

A production-ready AI-powered food tracking system that uses image recognition to detect ingredients, classify food, and analyze nutrition values.

## Architecture
- **Frontend**: React.js with Tailwind CSS, Lucide Icons, and Recharts.
- **Backend**: FastAPI with SQLAlchemy, PostgreSQL, and OAuth2 JWT authentication.
- **AI Engine**: 
  - YOLOv8 for ingredient detection.
  - ResNet50 for food classification.
  - CNN for cooking method detection.
- **Nutrition**: USDA FoodData Central API integration.
- **Recommendation Engine**: ML-based diet suggestions.

## Features
- User registration & login (JWT auth)
- User profile (age, weight, height, diet type)
- Upload food images for analysis
- Ingredient detection with confidence scores
- Cooking method classification
- Nutrition analysis (Calories, Protein, Carbs, Fats, Fiber, Sugar)
- Personalized diet recommendations
- Daily calorie tracking dashboard

## Getting Started

### Prerequisites
- Node.js (v18+)
- Python (v3.10+)
- PostgreSQL

### Installation

1.  **Backend Setup**:
    ```bash
    cd backend
    py -m pip install -r requirements.txt
    py init_db.py # Initialize the database
    py -m uvicorn main:app --reload
    ```

2.  **Frontend Setup**:
    ```bash
    cd frontend
    npm install
    npm run dev
    ```

## Project Structure
```
smart-food-tracker/
├── frontend/             # React.js application
│   ├── components/
│   ├── pages/
│   └── services/
├── backend/              # FastAPI server
│   ├── routes/
│   ├── models/
│   └── database/
├── ai_models/            # AI model logic
├── training_scripts/     # Model training scripts
└── datasets/             # Dataset links and info
```

## AI Models
The models are modular and can be trained using the scripts in `training_scripts/`.
- `train_yolov8.py`: Ingredient detection training.
- `train_resnet50.py`: Food classification training.
- `train_food101.py`: **(Recommended)** Fine-tune ResNet50 specifically for 101 types of food.

### Improving Recognition Accuracy
The current system uses ImageNet-pretrained models which are general-purpose. To achieve production-level accuracy for food:
1.  **Use Specialized Datasets**: Train or fine-tune models on datasets like **Food-101**, **VIREO-Food172**, or **Open Images Food**.
2.  **Fine-tuning**: Use the `training_scripts/train_food101.py` template to train on food images.
3.  **Custom Weights**: After training, update `FoodAnalyzer` in `ai_models/food_analyzer.py` to load your custom `.pt` weights.

## Deployment Guide
### Backend
- Dockerize the FastAPI app using a `Dockerfile`.
- Deploy to platforms like AWS ECS, Google Cloud Run, or DigitalOcean App Platform.
- Use a managed PostgreSQL instance (e.g., AWS RDS, MongoDB Atlas).

### Frontend
- Build the React app using `npm run build`.
- Deploy the `dist` folder to Vercel, Netlify, or AWS S3 + CloudFront.

## License
MIT License
