import os
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Import database connection and models
from database.connection import engine, Base, get_db
from database import models

# Import routers
from routers.auth import router as auth_router
from routers.users import router as users_router
from routers.students import router as students_router
from routers.opportunities import router as opportunities_router
from routers.recommendations import router as recommendations_router

# Create tables if they don't exist (for development/hackathon convenience)
# In production, you'd typically use Alembic for migrations.
# Base.metadata.create_all(bind=engine) # This line will be used by create_db_schema.py

app = FastAPI(
    title="Cognitive Navigator Backend",
    description="API for the Private University Talent Connect Platform with AI-powered recommendations.",
    version="1.0.0",
)

# Configure CORS (Cross-Origin Resource Sharing)
# Adjust origins as needed for your frontend URL in production
origins = [
    "http://localhost:3000",  # Your Next.js frontend
    "http://localhost:8000",  # If your backend runs on a different port for testing
    # Add production frontend URL here later
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router, prefix="/api/auth", tags=["Authentication"])
app.include_router(users_router, prefix="/api/users", tags=["Users"])
app.include_router(students_router, prefix="/api/students", tags=["Students"])
app.include_router(opportunities_router, prefix="/api/opportunities", tags=["Opportunities"])
app.include_router(recommendations_router, prefix="/api/recommendations", tags=["Recommendations"])


@app.get("/")
def read_root():
    return {"message": "Welcome to the Cognitive Navigator API!"}

# Example of a simple health check endpoint
@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    try:
        # Try to query the database to ensure connection is active
        db.execute("SELECT 1")
        return {"status": "ok", "database": "connected"}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database connection error: {e}")