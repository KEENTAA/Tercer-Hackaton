from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from ..config import settings
from ..schemas.user import UserCreate, UserUpdate, UserResponse
from ..services.user_service import UserService
from ..domain.models import UserRole


router = APIRouter(prefix="/api/v1/users", tags=["users"])


def get_db() -> Session:
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    
    engine = create_engine(settings.database_url)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/", response_model=UserResponse, status_code=201)
async def create_user(user_data: UserCreate, db: Session = Depends(get_db)):
    """Crear nuevo usuario"""
    existing_user = await UserService(db).get_user_by_email(user_data.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="El usuario ya existe")
    
    service = UserService(db)
    user = await service.create_user(user_data)
    return user


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, db: Session = Depends(get_db)):
    """Obtener usuario por ID"""
    service = UserService(db)
    user = await service.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return user


@router.get("/email/{email}", response_model=UserResponse)
async def get_user_by_email(email: str, db: Session = Depends(get_db)):
    """Obtener usuario por email"""
    service = UserService(db)
    user = await service.get_user_by_email(email)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return user


@router.get("/", response_model=dict)
async def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """Listar todos los usuarios"""
    service = UserService(db)
    return await service.list_users(skip, limit)


@router.get("/role/{role}", response_model=dict)
async def list_users_by_role(
    role: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """Listar usuarios por rol"""
    try:
        UserRole(role)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Rol inválido: {role}")
    
    service = UserService(db)
    return await service.list_users_by_role(role, skip, limit)


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    db: Session = Depends(get_db)
):
    """Actualizar usuario"""
    service = UserService(db)
    user = await service.update_user(user_id, user_data)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return user


@router.delete("/{user_id}", status_code=204)
async def delete_user(user_id: int, db: Session = Depends(get_db)):
    """Eliminar usuario (soft delete)"""
    service = UserService(db)
    success = await service.delete_user(user_id)
    if not success:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return None


@router.post("/{user_id}/activate", response_model=UserResponse)
async def activate_user(user_id: int, db: Session = Depends(get_db)):
    """Activar usuario"""
    service = UserService(db)
    user = await service.activate_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return user


@router.post("/{user_id}/deactivate", response_model=UserResponse)
async def deactivate_user(user_id: int, db: Session = Depends(get_db)):
    """Desactivar usuario"""
    service = UserService(db)
    user = await service.deactivate_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return user
