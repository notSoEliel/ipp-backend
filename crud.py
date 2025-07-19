# crud.py
# This file contains functions for database operations (Create, Read, Update, Delete).

from sqlalchemy.orm import Session
import models
import schemas
from datetime import datetime


# --- User CRUD ---
def get_user_by_firebase_uid(db: Session, firebase_uid: str):
    return (
        db.query(models.User).filter(models.User.firebase_uid == firebase_uid).first()
    )


def create_user(db: Session, user: schemas.UserCreate):
    # Set the first user as admin for testing purposes
    is_first_user = db.query(models.User).count() == 0
    db_user = models.User(
        firebase_uid=user.firebase_uid,
        email=user.email,
        full_name=user.full_name,
        is_admin=is_first_user,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


# --- Sermon CRUD ---
def get_sermon_by_id(db: Session, sermon_id: int):
    return db.query(models.Sermon).filter(models.Sermon.id == sermon_id).first()


def get_latest_sermon(db: Session):
    return db.query(models.Sermon).order_by(models.Sermon.sermon_date.desc()).first()


def get_sermons(db: Session, skip: int = 0, limit: int = 100):
    return (
        db.query(models.Sermon)
        .order_by(models.Sermon.sermon_date.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def create_sermon(db: Session, sermon: schemas.SermonCreate):
    db_sermon = models.Sermon(**sermon.model_dump())
    db.add(db_sermon)
    db.commit()
    db.refresh(db_sermon)
    return db_sermon


def update_sermon(db: Session, sermon_id: int, sermon_update: schemas.SermonUpdate):
    db_sermon = get_sermon_by_id(db, sermon_id)
    if not db_sermon:
        return None
    update_data = sermon_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_sermon, key, value)
    db.commit()
    db.refresh(db_sermon)
    return db_sermon


def delete_sermon(db: Session, sermon_id: int):
    db_sermon = get_sermon_by_id(db, sermon_id)
    if not db_sermon:
        return None
    db.delete(db_sermon)
    db.commit()
    return db_sermon


# --- Event CRUD ---
def get_event_by_id(db: Session, event_id: int):
    return db.query(models.Event).filter(models.Event.id == event_id).first()


def get_all_events(db: Session):
    """Gets all events, past and future."""
    return db.query(models.Event).order_by(models.Event.event_datetime.asc()).all()


def get_upcoming_events(db: Session, skip: int = 0, limit: int = 100):
    """Gets events from today onwards."""
    now = datetime.now()
    return (
        db.query(models.Event)
        .filter(models.Event.event_datetime >= now)
        .order_by(models.Event.event_datetime.asc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_past_events(db: Session, skip: int = 0, limit: int = 100):
    """Gets events from before today."""
    now = datetime.now()
    return (
        db.query(models.Event)
        .filter(models.Event.event_datetime < now)
        .order_by(models.Event.event_datetime.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def create_event(db: Session, event: schemas.EventCreate):
    db_event = models.Event(**event.model_dump())
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event


def update_event(db: Session, event_id: int, event_update: schemas.EventUpdate):
    db_event = get_event_by_id(db, event_id)
    if not db_event:
        return None
    update_data = event_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_event, key, value)
    db.commit()
    db.refresh(db_event)
    return db_event


def delete_event(db: Session, event_id: int):
    db_event = get_event_by_id(db, event_id)
    if not db_event:
        return None
    db.delete(db_event)
    db.commit()
    return db_event
