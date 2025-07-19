# main.py
# This is the main entry point for the FastAPI application.

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List

import crud
import models
import schemas
import auth
import database
from auth import get_current_user, get_current_admin_user

# Initialize the database and populate it with initial data
database.init_db()

# Create the FastAPI app instance
app = FastAPI(
    title="Conexión IPP API",
    description="API para la aplicación móvil de la Iglesia Presbiteriana de Panamá.",
    version="1.0.0",
)

# --- CORS Middleware ---
# This allows your FlutterFlow app to communicate with the API.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Dependency to get a database session
get_db = auth.get_db

# --- API Endpoints ---


@app.get("/", tags=["General"])
def read_root():
    """A root endpoint to check if the API is running."""
    return {"message": "Bienvenido a la API de Conexión IPP"}


# --- User Endpoints ---


@app.post(
    "/sync-user",
    response_model=schemas.User,
    tags=["Users"],
    summary="Sincronizar Usuario de Firebase",
    description="Verifica un token de ID de Firebase, y crea un perfil de usuario en la base de datos local si no existe. Debe llamarse después de cada inicio de sesión o registro en la app cliente.",
)
async def sync_user(
    token: str = Depends(auth.oauth2_scheme), db: Session = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
    )
    try:
        decoded_token = auth.firebase_auth.verify_id_token(token)
        firebase_uid = decoded_token.get("uid")
        email = decoded_token.get("email")
        full_name = decoded_token.get("name", "Usuario")

        if not firebase_uid or not email:
            raise credentials_exception

        db_user = crud.get_user_by_firebase_uid(db, firebase_uid=firebase_uid)

        if db_user:
            return db_user
        else:
            user_in = schemas.UserCreate(
                firebase_uid=firebase_uid, email=email, full_name=full_name
            )
            return crud.create_user(db=db, user=user_in)

    except Exception as e:
        print(f"Error during user sync: {e}")
        raise credentials_exception


# --- Sermon Endpoints ---


@app.get(
    "/sermons/latest",
    response_model=schemas.Sermon,
    tags=["Sermons"],
    summary="Obtener el Último Sermón",
    description="Devuelve el sermón más reciente basado en la fecha de predicación. Ideal para la pantalla de inicio de la app.",
)
def get_latest_sermon(
    db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)
):
    sermon = crud.get_latest_sermon(db)
    if sermon is None:
        raise HTTPException(status_code=404, detail="No sermons found")
    return sermon


@app.get(
    "/sermons",
    response_model=List[schemas.Sermon],
    tags=["Sermons"],
    summary="Obtener Todos los Sermones",
    description="Devuelve una lista de todos los sermones, ordenados del más reciente al más antiguo.",
)
def get_all_sermons(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    sermons = crud.get_sermons(db, skip=skip, limit=limit)
    return sermons


# ... (Admin endpoints for sermons remain the same) ...

# --- Event Endpoints ---


@app.get(
    "/events/upcoming",
    response_model=List[schemas.Event],
    tags=["Events"],
    summary="Obtener Eventos Próximos",
    description="Devuelve una lista de todos los eventos futuros, ordenados del más próximo al más lejano.",
)
def get_upcoming_events(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    events = crud.get_upcoming_events(db, skip=skip, limit=limit)
    return events


@app.get(
    "/events/past",
    response_model=List[schemas.Event],
    tags=["Events"],
    summary="Obtener Eventos Pasados",
    description="Devuelve una lista de todos los eventos que ya ocurrieron, ordenados del más reciente al más antiguo.",
)
def get_past_events(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    events = crud.get_past_events(db, skip=skip, limit=limit)
    return events


# ... (Admin endpoints for events remain the same) ...
