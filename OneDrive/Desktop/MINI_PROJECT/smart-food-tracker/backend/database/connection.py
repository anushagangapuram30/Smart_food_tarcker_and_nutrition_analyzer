from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .schema import Base

DATABASE_URL = "postgresql://user:password@localhost/smart_food_tracker"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_db_and_tables():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
