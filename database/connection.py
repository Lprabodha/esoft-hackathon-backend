import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv() # Load environment variables

# Get database URL from environment variables
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")

if not SQLALCHEMY_DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable not set.")

# Create the SQLAlchemy engine
# For MySQL, charset='utf8mb4' is recommended for full Unicode support
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_pre_ping=True, # Ensures connections are still alive
    pool_recycle=3600, # Recycle connections after 1 hour
    connect_args={"charset": "utf8mb4"} # Specific for mysql-connector-python
)

# Create a SessionLocal class
# Each instance of SessionLocal will be a database session.
# The `autocommit` is set to False to allow explicit commits.
# The `autoflush` is set to False to prevent flushing until commit or explicit flush.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create a declarative base for your ORM models
Base = declarative_base()

# Dependency to get a database session for each request
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()