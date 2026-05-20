# Controladores para Auth Service

from fastapi import APIRouter, Depends, Header
from sqlalchemy.orm import Session
from ..services.auth_service import AuthenticationService
from ..schemas.auth import (
    RegisterRequest,
    LoginRequest,
    LoginResponse,
    TokenResponse,
    UserResponse,
    RefreshTokenRequest,
    ChangePasswordRequest
)
from ...shared.schemas import DataResponse, ResponseBase
from ...shared.exceptions import ApplicationException
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/auth", tags=["auth"])


async def get_db() -> Session:
    """Obtener sesión de base de datos"""
    from sqlalchemy import create_engine
    from ..config import settings
    from ..domain.models import Base
    
    engine = create_engine(settings.database_url)
    Base.metadata.create_all(bind=engine)
    db = Session(engine)
    try:
        yield db
    finally:
        db.close()


async def get_auth_service(db: Session = Depends(get_db)) -> AuthenticationService:
    """Obtener servicio de autenticación"""
    return AuthenticationService(db)


@router.post(
    "/register",
    response_model=DataResponse[LoginResponse],
    status_code=201,
    summary="Registrar nuevo usuario",
    description="Registra un nuevo usuario en el sistema"
)
async def register(
    request: RegisterRequest,
    auth_service: AuthenticationService = Depends(get_auth_service)
):
    """Registrar nuevo usuario"""
    try:
        access_token, refresh_token = await auth_service.register(request)
        
        user = await auth_service.user_repo.get_user_by_username(request.username)
        
        return {
            "success": True,
            "data": {
                "user": UserResponse.model_validate(user),
                "access_token": access_token,
                "refresh_token": refresh_token,
                "token_type": "bearer",
                "expires_in": 3600
            }
        }
    except ApplicationException as e:
        return {
            "success": False,
            "error": e.message,
            "code": e.code,
            "data": None
        }


@router.post(
    "/login",
    response_model=DataResponse[LoginResponse],
    status_code=200,
    summary="Login de usuario",
    description="Autentica un usuario y retorna tokens"
)
async def login(
    request: LoginRequest,
    auth_service: AuthenticationService = Depends(get_auth_service)
):
    """Login de usuario"""
    try:
        access_token, refresh_token = await auth_service.login(request)
        
        # Obtener usuario
        user = await auth_service.user_repo.get_user_by_username(request.username)
        
        return {
            "success": True,
            "data": {
                "user": UserResponse.model_validate(user),
                "access_token": access_token,
                "refresh_token": refresh_token,
                "token_type": "bearer",
                "expires_in": 3600
            }
        }
    except ApplicationException as e:
        return {
            "success": False,
            "error": e.message,
            "code": e.code,
            "data": None
        }


@router.post(
    "/refresh",
    response_model=DataResponse[TokenResponse],
    status_code=200,
    summary="Refrescar token",
    description="Genera un nuevo access token"
)
async def refresh(
    request: RefreshTokenRequest,
    auth_service: AuthenticationService = Depends(get_auth_service)
):
    """Refrescar token de acceso"""
    try:
        access_token = await auth_service.refresh_token(request.refresh_token)
        
        return {
            "success": True,
            "data": {
                "access_token": access_token,
                "refresh_token": request.refresh_token,
                "token_type": "bearer",
                "expires_in": 3600
            }
        }
    except ApplicationException as e:
        return {
            "success": False,
            "error": e.message,
            "code": e.code,
            "data": None
        }


@router.post(
    "/logout",
    response_model=ResponseBase,
    status_code=200,
    summary="Logout",
    description="Cierra la sesión del usuario"
)
async def logout(
    request: RefreshTokenRequest,
    auth_service: AuthenticationService = Depends(get_auth_service)
):
    """Logout"""
    try:
        await auth_service.logout(request.refresh_token)
        return {"success": True}
    except ApplicationException as e:
        return {
            "success": False,
            "error": e.message,
            "code": e.code
        }


@router.post(
    "/change-password",
    response_model=ResponseBase,
    status_code=200,
    summary="Cambiar contraseña",
    description="Cambia la contraseña del usuario autenticado"
)
async def change_password(
    request: ChangePasswordRequest,
    authorization: str = Header(None),
    auth_service: AuthenticationService = Depends(get_auth_service)
):
    """Cambiar contraseña"""
    try:
        # Extraer user_id del token
        token = authorization.split(" ")[1] if authorization else None
        if not token:
            return {
                "success": False,
                "error": "Authorization requerida",
                "code": "UNAUTHORIZED"
            }
        
        user_id = auth_service.verify_token(token)
        await auth_service.change_password(user_id, request.current_password, request.new_password)
        
        return {"success": True}
    except ApplicationException as e:
        return {
            "success": False,
            "error": e.message,
            "code": e.code
        }


@router.get(
    "/me",
    response_model=DataResponse[UserResponse],
    status_code=200,
    summary="Obtener usuario actual",
    description="Retorna los datos del usuario autenticado"
)
async def get_current_user(
    authorization: str = Header(None),
    auth_service: AuthenticationService = Depends(get_auth_service)
):
    """Obtener usuario actual"""
    try:
        token = authorization.split(" ")[1] if authorization else None
        if not token:
            return {
                "success": False,
                "error": "Authorization requerida",
                "code": "UNAUTHORIZED",
                "data": None
            }
        
        user_id = auth_service.verify_token(token)
        user = await auth_service.user_repo.get_user_by_id(user_id)
        
        return {
            "success": True,
            "data": UserResponse.model_validate(user)
        }
    except ApplicationException as e:
        return {
            "success": False,
            "error": e.message,
            "code": e.code,
            "data": None
        }
