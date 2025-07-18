# auth.py
# This file handles Firebase authentication and user dependency injection.

import os
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import firebase_admin
from firebase_admin import credentials, auth as firebase_auth
from sqlalchemy.orm import Session

import crud
import models
from database import SessionLocal

# --- Firebase Initialization ---
# The path to your Firebase service account key file.
# IMPORTANT: Download this file from your Firebase project settings.
SERVICE_ACCOUNT_FILE = os.path.join(
    os.path.dirname(__file__), "firebase-credentials.json"
)

try:
    cred = credentials.Certificate(SERVICE_ACCOUNT_FILE)
    firebase_admin.initialize_app(cred)
    print("Firebase Admin SDK initialized successfully.")
except Exception as e:
    print(f"Error initializing Firebase Admin SDK: {e}")
    print("Please ensure 'firebase-credentials.json' is in the correct path and valid.")


# OAuth2 scheme to extract the token from the Authorization header.
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="token"
)  # tokenUrl is not used directly but required


# --- Dependency to get DB session ---
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# --- Dependency to get current user ---
async def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> models.User:
    """
    Dependency to verify Firebase ID token and get the user from our database.
    This function will be used to protect our API endpoints.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # Verify the ID token while checking for revocation.
        decoded_token = firebase_auth.verify_id_token(token, check_revoked=True)
        firebase_uid = decoded_token["uid"]

        # Get user from our database
        user = crud.get_user_by_firebase_uid(db, firebase_uid=firebase_uid)
        if user is None:
            # This case should ideally not happen if sync-user is called after login.
            # However, it's a good safeguard.
            raise credentials_exception

        return user

    except firebase_auth.RevokedIdTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has been revoked"
        )
    except firebase_auth.InvalidIdTokenError:
        raise credentials_exception
    except Exception as e:
        # Catch any other exceptions during token verification
        print(f"An unexpected error occurred during token verification: {e}")
        raise credentials_exception


# --- Dependency to get current ADMIN user ---
async def get_current_admin_user(
    current_user: models.User = Depends(get_current_user),
) -> models.User:
    """
    Dependency that checks if the current user is an admin.
    """
    if not current_user.is_admin: # type: ignore
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user doesn't have enough privileges",
        )
    return current_user
