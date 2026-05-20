from sqlalchemy.orm import Session
from passlib.context import CryptContext
from app.models.usuarios import Usuario
from app.schemas.usuarios import UsuarioCreate, UsuarioUpdate

# Contexto para el hashing seguro de contraseñas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# --- OPERACIONES GET (READ) ---

def get_user_by_id(db: Session, user_id: int):
    """Obtiene un usuario específico por su llave primaria."""
    return db.query(Usuario).filter(Usuario.id_usuario == user_id).first()

def get_user_by_email(db: Session, email: str):
    """Busca un usuario por correo electrónico (Esencial para OAuth2/Login)."""
    return db.query(Usuario).filter(Usuario.correo == email).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    """Lista todos los usuarios registrados (Listo para paginación)."""
    return db.query(Usuario).offset(skip).limit(limit).all()

# --- OPERACIONES POST (CREATE) ---

def create_user(db: Session, user: UsuarioCreate):
    """Registra un nuevo usuario aplicando hashing a su contraseña."""
    hashed_password = get_password_hash(user.password)
    db_user = Usuario(
        codigo_universitario=user.codigo_universitario,
        nombre=user.nombre,
        correo=user.correo,
        password_hash=hashed_password,
        rol=user.rol
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# --- OPERACIONES PUT (UPDATE) ---

def update_user(db: Session, user_id: int, user_in: UsuarioUpdate):
    """Actualiza parcialmente los datos de un usuario de forma dinámica."""
    db_user = db.query(Usuario).filter(Usuario.id_usuario == user_id).first()
    if not db_user:
        return None
    
    # Convertimos el esquema a diccionario ignorando los valores no enviados (None)
    update_data = user_in.model_dump(exclude_unset=True)
    
    if "password" in update_data:
        db_user.password_hash = get_password_hash(update_data["password"])
        del update_data["password"]

    for field, value in update_data.items():
        setattr(db_user, field, value)

    db.commit()
    db.refresh(db_user)
    return db_user

# --- OPERACIONES DELETE (DELETE) ---

def delete_user(db: Session, user_id: int):
    """Elimina un usuario del sistema."""
    db_user = db.query(Usuario).filter(Usuario.id_usuario == user_id).first()
    if db_user:
        db.delete(db_user)
        db.commit()
        return True
    return False