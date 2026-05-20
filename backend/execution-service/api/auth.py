from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db
from app.core.security import create_access_token, get_current_user
from app.crud import crud_user
from app.schemas.auth import Token
from app.schemas.usuarios import UsuarioCreate, UsuarioResponse, UsuarioUpdate
from app.models.usuarios import Usuario

router = APIRouter(prefix="/auth", tags=["Autenticación y Perfil"])

# --- POST: Login ---
@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Intercambia credenciales por un token JWT."""
    user = crud_user.get_user_by_email(db, email=form_data.username)
    if not user or not crud_user.verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Correo o contraseña incorrectos.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id_usuario), "rol": user.rol},
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

# --- POST: Registro de Usuarios ---
@router.post("/registro", response_model=UsuarioResponse, status_code=status.HTTP_201_CREATED)
def registrar_usuario(user_in: UsuarioCreate, db: Session = Depends(get_db)):
    """Registra un nuevo estudiante o profesor en el sistema."""
    user = crud_user.get_user_by_email(db, email=user_in.correo)
    if user:
        raise HTTPException(status_code=400, detail="Este correo ya está registrado.")
    
    return crud_user.create_user(db=db, user=user_in)

# --- GET: Mi Perfil ---
@router.get("/me", response_model=UsuarioResponse)
def leer_mi_perfil(current_user: Usuario = Depends(get_current_user)):
    """Retorna los datos del usuario actualmente autenticado."""
    return current_user

# --- PUT: Actualizar Mi Perfil ---
@router.put("/me", response_model=UsuarioResponse)
def actualizar_mi_perfil(
    user_in: UsuarioUpdate, 
    db: Session = Depends(get_db), 
    current_user: Usuario = Depends(get_current_user)
):
    """Permite al usuario actualizar su propio nombre, correo o contraseña."""
    return crud_user.update_user(db=db, user_id=current_user.id_usuario, user_in=user_in)