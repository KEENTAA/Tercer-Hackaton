# Excepciones y Errores Personalizados

from typing import Any, Optional


class ApplicationException(Exception):
    """Excepción base para aplicación"""
    def __init__(
        self,
        message: str,
        code: str = "INTERNAL_ERROR",
        status_code: int = 500,
        details: Optional[dict] = None
    ):
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)

    def to_dict(self) -> dict:
        return {
            "success": False,
            "error": self.message,
            "code": self.code,
            "details": self.details
        }


class ValidationException(ApplicationException):
    """Errores de validación"""
    def __init__(self, message: str, details: Optional[dict] = None):
        super().__init__(
            message=message,
            code="VALIDATION_ERROR",
            status_code=400,
            details=details
        )


class AuthenticationException(ApplicationException):
    """Errores de autenticación"""
    def __init__(self, message: str = "Autenticación requerida"):
        super().__init__(
            message=message,
            code="AUTHENTICATION_ERROR",
            status_code=401
        )


class AuthorizationException(ApplicationException):
    """Errores de autorización"""
    def __init__(self, message: str = "No tiene permisos para acceder a este recurso"):
        super().__init__(
            message=message,
            code="AUTHORIZATION_ERROR",
            status_code=403
        )


class ResourceNotFoundException(ApplicationException):
    """Recurso no encontrado"""
    def __init__(self, resource: str, identifier: Any):
        super().__init__(
            message=f"{resource} no encontrado: {identifier}",
            code="NOT_FOUND",
            status_code=404
        )


class DuplicateResourceException(ApplicationException):
    """Recurso duplicado"""
    def __init__(self, resource: str, field: str, value: Any):
        super().__init__(
            message=f"{resource} con {field} '{value}' ya existe",
            code="DUPLICATE_RESOURCE",
            status_code=400
        )


class ConflictException(ApplicationException):
    """Conflicto en la operación"""
    def __init__(self, message: str):
        super().__init__(
            message=message,
            code="CONFLICT",
            status_code=409
        )


class ExternalServiceException(ApplicationException):
    """Error en servicio externo"""
    def __init__(self, service: str, message: str):
        super().__init__(
            message=f"Error en servicio {service}: {message}",
            code="EXTERNAL_SERVICE_ERROR",
            status_code=502
        )
