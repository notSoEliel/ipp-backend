# models.py
# This file defines the SQLAlchemy models for our database tables.
from sqlalchemy import Boolean, Column, Integer, String, DateTime, Date
import database

Base = database.Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    firebase_uid = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String)
    is_admin = Column(Boolean, default=False)
class Sermon(Base):
    __tablename__ = "sermons"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    pastor = Column(String)
    bible_verse = Column(String)
    sermon_date = Column(Date)
    image_url = Column(String)
    video_url = Column(String, nullable=True)
class Event(Base):
    __tablename__ = "events"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String, nullable=True)
    event_datetime = Column(DateTime)