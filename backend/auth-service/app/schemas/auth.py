# Schemas Pydantic para Auth Service

from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class UserRole(str, Enum):
    """Roles de usuario"""
    STUDENT = "student"
    TEACHER = "teacher"
    ADMIN = "admin"


# Request Schemas
class RegisterRequest(BaseModel):
    """Solicitud de registro"""
    email: EmailStr = Field(description="Email del usuario")
    username: str = Field(min_length=3, max_length=50, description="Usuario")
    password: str = Field(min_length=8, description="Contraseña")
    first_name: str = Field(description="Nombre")
    last_name: str = Field(description="Apellido")
    role: UserRole = Field(default=UserRole.STUDENT, description="Rol del usuario")


class LoginRequest(BaseModel):
    """Solicitud de login"""
    username: str = Field(description="Usuario o email")
    password: str = Field(description="Contraseña")


class RefreshTokenRequest(BaseModel):
    """Solicitud para refrescar token"""
    refresh_token: str = Field(description="Token de refresco")


class ChangePasswordRequest(BaseModel):
    """Solicitud para cambiar contraseña"""
    current_password: str = Field(description="Contraseña actual")
    new_password: str = Field(min_length=8, description="Nueva contraseña")


# Response Schemas
class TokenResponse(BaseModel):
    """Respuesta con tokens"""
    access_token: str = Field(description="Token de acceso JWT")
    refresh_token: str = Field(description="Token de refresco")
    token_type: str = Field(default="bearer")
    expires_in: int = Field(description="Tiempo de expiración en segundos")


class UserResponse(BaseModel):
    """Respuesta de usuario"""
    id: str = Field(description="ID del usuario")
    email: str = Field(description="Email")
    username: str = Field(description="Usuario")
    first_name: str = Field(description="Nombre")
    last_name: str = Field(description="Apellido")
    role: UserRole = Field(description="Rol")
    is_active: bool = Field(description="Estado activo")
    created_at: datetime = Field(description="Fecha de creación")
    last_login: Optional[datetime] = Field(None, description="Último login")

    class Config:
        from_attributes = True


class LoginResponse(BaseModel):
    """Respuesta de login"""
    user: UserResponse = Field(description="Datos del usuario")
    access_token: str = Field(description="Token de acceso")
    refresh_token: str = Field(description="Token de refresco")
    token_type: str = Field(default="bearer")
    expires_in: int = Field(description="Tiempo de expiración")


class JWTPayload(BaseModel):
    """Payload del JWT"""
    sub: str = Field(description="User ID")
    email: str = Field(description="Email del usuario")
    username: str = Field(description="Username")
    role: UserRole = Field(description="Rol del usuario")
    exp: int = Field(description="Tiempo de expiración")
