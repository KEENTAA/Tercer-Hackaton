# Repositorios para Auth Service

from abc import ABC, abstractmethod
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from ..domain.models import User, Session as SessionModel, UserRole
from ...shared.exceptions import ResourceNotFoundException, DuplicateResourceException
import uuid


class UserRepository:
    """Repositorio para gestionar usuarios"""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def create_user(
        self,
        email: str,
        username: str,
        password_hash: str,
        first_name: str,
        last_name: str,
        role: UserRole = UserRole.STUDENT
    ) -> User:
        """Crear nuevo usuario"""
        # Verificar que no exista
        existing = self.db.query(User).filter(
            (User.email == email) | (User.username == username)
        ).first()
        
        if existing:
            if existing.email == email:
                raise DuplicateResourceException("Usuario", "email", email)
            else:
                raise DuplicateResourceException("Usuario", "username", username)
        
        user = User(
            id=str(uuid.uuid4()),
            email=email,
            username=username,
            password_hash=password_hash,
            first_name=first_name,
            last_name=last_name,
            role=role
        )
        
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user
    
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Obtener usuario por email"""
        return self.db.query(User).filter(User.email == email).first()
    
    async def get_user_by_username(self, username: str) -> Optional[User]:
        """Obtener usuario por username"""
        return self.db.query(User).filter(User.username == username).first()
    
    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Obtener usuario por ID"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ResourceNotFoundException("Usuario", user_id)
        return user
    
    async def update_last_login(self, user_id: str) -> User:
        """Actualizar último login"""
        from datetime import datetime
        user = await self.get_user_by_id(user_id)
        user.last_login = datetime.utcnow()
        self.db.commit()
        self.db.refresh(user)
        return user
    
    async def update_password(self, user_id: str, password_hash: str) -> User:
        """Actualizar contraseña"""
        user = await self.get_user_by_id(user_id)
        user.password_hash = password_hash
        self.db.commit()
        self.db.refresh(user)
        return user


class SessionRepository:
    """Repositorio para gestionar sesiones"""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def create_session(
        self,
        user_id: str,
        refresh_token: str,
        expires_at,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> SessionModel:
        """Crear nueva sesión"""
        session = SessionModel(
            id=str(uuid.uuid4()),
            user_id=user_id,
            refresh_token=refresh_token,
            expires_at=expires_at,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        return session
    
    async def get_session_by_refresh_token(self, refresh_token: str) -> Optional[SessionModel]:
        """Obtener sesión por refresh token"""
        return self.db.query(SessionModel).filter(
            SessionModel.refresh_token == refresh_token,
            SessionModel.is_active == True
        ).first()
    
    async def invalidate_session(self, session_id: str) -> None:
        """Invalidar una sesión"""
        session = self.db.query(SessionModel).filter(SessionModel.id == session_id).first()
        if session:
            session.is_active = False
            self.db.commit()
    
    async def invalidate_user_sessions(self, user_id: str) -> None:
        """Invalidar todas las sesiones de un usuario"""
        self.db.query(SessionModel).filter(
            SessionModel.user_id == user_id,
            SessionModel.is_active == True
        ).update({"is_active": False})
        self.db.commit()
