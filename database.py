# database.py
# This file handles the database connection and session management.

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime, date

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
    Initializes the database and creates tables if they don't exist.
    It also populates the database with some initial data for testing.
    """
    # Import models here to avoid circular imports
    import models

    # Create all tables in the database.
    Base.metadata.create_all(bind=engine)

    # Populate with initial data
    db = SessionLocal()
    try:
        # Check if sermons exist to avoid re-populating
        if not db.query(models.Sermon).first():
            print("Populating database with initial data...")

            # Add Sermons
            sermons_data = [
                models.Sermon(
                    title="¿Quién es tu Señor?",
                    pastor="Pr. Paulo Oliveira",
                    bible_verse="Mateo 6:24",
                    sermon_date=date.fromisoformat("2025-07-13"),
                    image_url="https://placehold.co/600x400?text=Serm%C3%B3n+1&font=roboto",
                    video_url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",  # El Rickroll :)
                ),
                models.Sermon(
                    title="El Amor Inagotable",
                    pastor="Pr. Paulo Oliveira",
                    bible_verse="1 Juan 4:8",
                    sermon_date=date.fromisoformat("2025-07-06"),
                    image_url="https://placehold.co/600x400?text=Serm%C3%B3n+2&font=roboto",
                    video_url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                ),
                models.Sermon(
                    title="Fundamentos de la Fe",
                    pastor="Pr. Invitado",
                    bible_verse="Hebreos 11:1",
                    sermon_date=date.fromisoformat("2025-06-29"),
                    image_url="https://placehold.co/600x400?text=Serm%C3%B3n+3&font=roboto",
                    video_url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                ),
            ]
            db.add_all(sermons_data)

            # Add Events
            events_data = [
                models.Event(
                    title="Culto Dominical",
                    description="Servicio principal de la semana.",
                    event_datetime=datetime.fromisoformat("2025-07-20T10:00:00"),
                ),
                models.Event(
                    title="Reunión de Jóvenes",
                    description="Encuentro semanal del grupo de jóvenes.",
                    event_datetime=datetime.fromisoformat("2025-07-25T19:30:00"),
                ),
                models.Event(
                    title="Estudio Bíblico",
                    description="Estudio del libro de Romanos.",
                    event_datetime=datetime.fromisoformat("2025-07-23T19:00:00"),
                ),
            ]
            db.add_all(events_data)

            db.commit()
            print("Database populated successfully.")
    finally:
        db.close()
