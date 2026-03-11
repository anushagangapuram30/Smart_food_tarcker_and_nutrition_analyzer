from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import authentication, food, user

app = FastAPI(title="Smart Food Tracker and Nutrition Analyzer")

# CORS configuration
origins = [
    "http://localhost:5173", # Vite default port
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(authentication.router, prefix="/auth", tags=["Authentication"])
app.include_router(food.router, prefix="/food", tags=["Food Analysis"])
app.include_router(user.router, prefix="/user", tags=["User Profile"])

@app.get("/")
def read_root():
    return {"message": "Welcome to Smart Food Tracker API"}
