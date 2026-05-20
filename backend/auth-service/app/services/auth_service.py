# Servicio de Autenticación

from datetime import datetime, timedelta
from typing import Optional, Tuple
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from ..config import settings
from ..repositories.user_repository import UserRepository, SessionRepository
from ..schemas.auth import JWTPayload, LoginRequest, RegisterRequest, TokenResponse
from ..domain.models import UserRole
from ...shared.exceptions import (
    AuthenticationException,
    ValidationException,
    ResourceNotFoundException
)

# Configurar contexto de contraseñas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthenticationService:
    """Servicio de autenticación"""
    
    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)
        self.session_repo = SessionRepository(db)
    
    def hash_password(self, password: str) -> str:
        """Hash de contraseña"""
        return pwd_context.hash(password)
    
    def verify_password(self, plain_password: str, password_hash: str) -> bool:
        """Verificar contraseña"""
        return pwd_context.verify(plain_password, password_hash)
    
    async def register(self, request: RegisterRequest) -> Tuple[str, str]:
        """Registrar nuevo usuario"""
        # Validar contraseña
        if len(request.password) < settings.password_min_length:
            raise ValidationException(
                f"La contraseña debe tener al menos {settings.password_min_length} caracteres"
            )
        
        password_hash = self.hash_password(request.password)
        
        user = await self.user_repo.create_user(
            email=request.email,
            username=request.username,
            password_hash=password_hash,
            first_name=request.first_name,
            last_name=request.last_name,
            role=request.role
        )
        
        access_token = self.create_access_token(user.id)
        refresh_token = self.create_refresh_token(user.id)
        
        expires_at = datetime.utcnow() + timedelta(
            days=settings.refresh_token_expire_days
        )
        
        await self.session_repo.create_session(
            user_id=user.id,
            refresh_token=refresh_token,
            expires_at=expires_at
        )
        
        return access_token, refresh_token
    
    async def login(self, request: LoginRequest) -> Tuple[str, str]:
        """Login de usuario"""
        user = await self.user_repo.get_user_by_username(request.username)
        
        if not user or not self.verify_password(request.password, user.password_hash):
            raise AuthenticationException("Email o contraseña incorrectos")
        
        if not user.is_active:
            raise AuthenticationException("Usuario inactivo")
        
        # Actualizar último login
        await self.user_repo.update_last_login(user.id)
        
        access_token = self.create_access_token(user.id)
        refresh_token = self.create_refresh_token(user.id)
        
        expires_at = datetime.utcnow() + timedelta(
            days=settings.refresh_token_expire_days
        )
        
        await self.session_repo.create_session(
            user_id=user.id,
            refresh_token=refresh_token,
            expires_at=expires_at
        )
        
        return access_token, refresh_token
    
    def create_access_token(self, user_id: str) -> str:
        """Crear token de acceso"""
        expire = datetime.utcnow() + timedelta(
            minutes=settings.access_token_expire_minutes
        )
        
        payload = {
            "sub": user_id,
            "exp": expire,
            "iat": datetime.utcnow()
        }
        
        encoded_jwt = jwt.encode(
            payload,
            settings.jwt_secret,
            algorithm=settings.jwt_algorithm
        )
        
        return encoded_jwt
    
    def create_refresh_token(self, user_id: str) -> str:
        """Crear token de refresco"""
        expire = datetime.utcnow() + timedelta(
            days=settings.refresh_token_expire_days
        )
        
        payload = {
            "sub": user_id,
            "exp": expire,
            "type": "refresh"
        }
        
        encoded_jwt = jwt.encode(
            payload,
            settings.jwt_secret,
            algorithm=settings.jwt_algorithm
        )
        
        return encoded_jwt
    
    def verify_token(self, token: str) -> str:
        """Verificar token y retornar user_id"""
        try:
            payload = jwt.decode(
                token,
                settings.jwt_secret,
                algorithms=[settings.jwt_algorithm]
            )
            user_id: str = payload.get("sub")
            if user_id is None:
                raise AuthenticationException("Token inválido")
            return user_id
        except JWTError:
            raise AuthenticationException("Token inválido o expirado")
    
    async def refresh_token(self, refresh_token: str) -> str:
        """Refrescar access token"""
        session = await self.session_repo.get_session_by_refresh_token(refresh_token)
        if not session:
            raise AuthenticationException("Refresh token inválido")
        
        # Verificar que no esté expirado
        if session.expires_at < datetime.utcnow():
            await self.session_repo.invalidate_session(session.id)
            raise AuthenticationException("Refresh token expirado")
        
        return self.create_access_token(session.user_id)
    
    async def logout(self, refresh_token: str) -> None:
        """Logout"""
        session = await self.session_repo.get_session_by_refresh_token(refresh_token)
        if session:
            await self.session_repo.invalidate_session(session.id)
    
    async def change_password(self, user_id: str, current_password: str, new_password: str) -> None:
        """Cambiar contraseña"""
        user = await self.user_repo.get_user_by_id(user_id)
        
        if not self.verify_password(current_password, user.password_hash):
            raise AuthenticationException("Contraseña actual incorrecta")
        
        password_hash = self.hash_password(new_password)
        await self.user_repo.update_password(user_id, password_hash)
