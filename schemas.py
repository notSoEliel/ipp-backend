# schemas.py
# This file defines the Pydantic models for data validation and serialization.

from pydantic import BaseModel
from datetime import datetime, date

# --- User Schemas ---
class UserBase(BaseModel):
    email: str
    full_name: str | None = None

class UserCreate(UserBase):
    firebase_uid: str

class User(UserBase):
    id: int
    firebase_uid: str
    is_admin: bool

    class Config:
        from_attributes = True

# --- Sermon Schemas ---
class SermonBase(BaseModel):
    title: str
    pastor: str
    bible_verse: str
    sermon_date: date
    image_url: str
    video_url: str | None = None

class SermonCreate(SermonBase):
    pass

class SermonUpdate(BaseModel):
    title: str | None = None
    pastor: str | None = None
    bible_verse: str | None = None
    sermon_date: date | None = None
    image_url: str | None = None
    video_url: str | None = None

class Sermon(SermonBase):
    id: int

    class Config:
        from_attributes = True

# --- Event Schemas ---
class EventBase(BaseModel):
    title: str
    description: str | None = None
    event_datetime: datetime

class EventCreate(EventBase):
    pass

class EventUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    event_datetime: datetime | None = None

class Event(EventBase):
    id: int

    class Config:
        from_attributes = True
