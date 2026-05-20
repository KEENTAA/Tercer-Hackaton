# Schemas compartidos para respuestas

from typing import Any, Generic, List, Optional, TypeVar
from pydantic import BaseModel, Field

T = TypeVar("T")


class ResponseBase(BaseModel):
    """Respuesta base para todos los endpoints"""
    success: bool = Field(True, description="Indica si la operación fue exitosa")
    error: Optional[str] = Field(None, description="Mensaje de error si aplica")
    code: Optional[str] = Field(None, description="Código de error técnico")


class DataResponse(ResponseBase, Generic[T]):
    """Respuesta con datos genéricos"""
    data: Optional[T] = Field(None, description="Datos de la respuesta")

    class Config:
        json_encoders = {
            Any: str
        }


class PaginationData(BaseModel):
    """Datos de paginación"""
    total: int = Field(description="Total de registros")
    page: int = Field(description="Página actual")
    size: int = Field(description="Tamaño de página")
    pages: int = Field(description="Total de páginas")


class PaginatedResponse(ResponseBase, Generic[T]):
    """Respuesta paginada"""
    data: List[T] = Field(default_factory=list, description="Lista de datos")
    pagination: Optional[PaginationData] = Field(None, description="Información de paginación")


class ErrorResponse(ResponseBase):
    """Respuesta de error"""
    success: bool = Field(False)


# Event Schemas
class Event(BaseModel):
    """Evento de dominio"""
    event_type: str = Field(description="Tipo de evento")
    aggregate_id: str = Field(description="ID del agregado")
    timestamp: str = Field(description="Timestamp del evento")
    data: dict = Field(default_factory=dict, description="Datos del evento")
    user_id: Optional[str] = Field(None, description="Usuario que generó el evento")


class SubmissionCreatedEvent(Event):
    """Evento: Envío de código creado"""
    event_type: str = "submissionCreated"


class ExecutionCompletedEvent(Event):
    """Evento: Ejecución completada"""
    event_type: str = "executionCompleted"


class GradingCompletedEvent(Event):
    """Evento: Calificación completada"""
    event_type: str = "gradingCompleted"


class PlagiarismAnalyzedEvent(Event):
    """Evento: Análisis de plagio completado"""
    event_type: str = "plagiarismAnalyzed"
