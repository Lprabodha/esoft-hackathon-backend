import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database.connection import engine, Base
from database import models # Import models to ensure they are registered with Base

def create_tables():
    """Creates all defined tables in the database."""
    print("Attempting to connect to the database and create tables...")
    try:
        # Base.metadata.create_all creates all tables defined in Base
        Base.metadata.create_all(bind=engine)
        print("All tables created successfully (or already existed).")
    except Exception as e:
        print(f"Error creating tables: {e}")
        print("Please ensure your MySQL server is running and database credentials in .env are correct.")
        print("Also, ensure the database specified in DATABASE_URL (e.g., 'cognitive_navigator_db') exists.")

if __name__ == "__main__":
    create_tables()