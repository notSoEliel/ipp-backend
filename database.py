# database.py
# This file handles the database connection and session management.

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Define the database URL for SQLite.
# The database will be a file named `church_app.db` in the same directory.
SQLALCHEMY_DATABASE_URL = "sqlite:///./church_app.db"

# Create the SQLAlchemy engine.
# The `connect_args` is needed only for SQLite to allow multithreading.
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# Create a SessionLocal class. Each instance of this class will be a database session.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create a Base class. Our ORM models will inherit from this class.
Base = declarative_base()

def init_db():
    """
    Initializes the database by creating all tables defined in the models.
    This function no longer populates data. Data should be managed
    via an external tool like DBeaver or through the API endpoints.
    """
    # Import models here to ensure they are registered with SQLAlchemy's metadata
    import models
    
    # Create all tables in the database if they don't exist.
    Base.metadata.create_all(bind=engine)
