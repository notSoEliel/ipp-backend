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


@app.post(
    "/sermons",
    response_model=schemas.Sermon,
    status_code=status.HTTP_201_CREATED,
    tags=["Admin: Sermons"],
    summary="[Admin] Crear un Nuevo Sermón",
    description="Crea un nuevo registro de sermón en la base de datos. Requiere permisos de administrador.",
)
def create_sermon(
    sermon: schemas.SermonCreate,
    db: Session = Depends(get_db),
    admin_user: models.User = Depends(get_current_admin_user),
):
    return crud.create_sermon(db=db, sermon=sermon)


@app.put(
    "/sermons/{sermon_id}",
    response_model=schemas.Sermon,
    tags=["Admin: Sermons"],
    summary="[Admin] Actualizar un Sermón",
    description="Actualiza los datos de un sermón existente por su ID. Requiere permisos de administrador.",
)
def update_sermon(
    sermon_id: int,
    sermon_update: schemas.SermonUpdate,
    db: Session = Depends(get_db),
    admin_user: models.User = Depends(get_current_admin_user),
):
    db_sermon = crud.update_sermon(db, sermon_id, sermon_update)
    if db_sermon is None:
        raise HTTPException(status_code=404, detail="Sermon not found")
    return db_sermon


@app.delete(
    "/sermons/{sermon_id}",
    response_model=schemas.Sermon,
    tags=["Admin: Sermons"],
    summary="[Admin] Eliminar un Sermón",
    description="Elimina un sermón de la base de datos por su ID. Requiere permisos de administrador.",
)
def delete_sermon(
    sermon_id: int,
    db: Session = Depends(get_db),
    admin_user: models.User = Depends(get_current_admin_user),
):
    db_sermon = crud.delete_sermon(db, sermon_id)
    if db_sermon is None:
        raise HTTPException(status_code=404, detail="Sermon not found")
    return db_sermon


# --- Event Endpoints ---


@app.get(
    "/events",
    response_model=List[schemas.Event],
    tags=["Events"],
    summary="Obtener Todos los Eventos",
    description="Devuelve una lista de todos los eventos futuros, ordenados del más próximo al más lejano.",
)
def get_all_events(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    events = crud.get_events(db, skip=skip, limit=limit)
    return events


@app.post(
    "/events",
    response_model=schemas.Event,
    status_code=status.HTTP_201_CREATED,
    tags=["Admin: Events"],
    summary="[Admin] Crear un Nuevo Evento",
    description="Crea un nuevo evento en la base de datos. Requiere permisos de administrador.",
)
def create_event(
    event: schemas.EventCreate,
    db: Session = Depends(get_db),
    admin_user: models.User = Depends(get_current_admin_user),
):
    return crud.create_event(db=db, event=event)


@app.put(
    "/events/{event_id}",
    response_model=schemas.Event,
    tags=["Admin: Events"],
    summary="[Admin] Actualizar un Evento",
    description="Actualiza los datos de un evento existente por su ID. Requiere permisos de administrador.",
)
def update_event(
    event_id: int,
    event_update: schemas.EventUpdate,
    db: Session = Depends(get_db),
    admin_user: models.User = Depends(get_current_admin_user),
):
    db_event = crud.update_event(db, event_id, event_update)
    if db_event is None:
        raise HTTPException(status_code=404, detail="Event not found")
    return db_event


@app.delete(
    "/events/{event_id}",
    response_model=schemas.Event,
    tags=["Admin: Events"],
    summary="[Admin] Eliminar un Evento",
    description="Elimina un evento de la base de datos por su ID. Requiere permisos de administrador.",
)
def delete_event(
    event_id: int,
    db: Session = Depends(get_db),
    admin_user: models.User = Depends(get_current_admin_user),
):
    db_event = crud.delete_event(db, event_id)
    if db_event is None:
        raise HTTPException(status_code=404, detail="Event not found")
    return db_event
