# Submission Service - Schemas

from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum
from datetime import datetime


class SubmissionStatus(str, Enum):
    """Estados de envío"""
    PENDING = "pending"
    SUBMITTED = "submitted"
    EXECUTING = "executing"
    EXECUTED = "executed"
    GRADING = "grading"
    GRADED = "graded"
    PLAGIARISM_CHECK = "plagiarism_check"
    COMPLETED = "completed"
    FAILED = "failed"


class SubmitCodeRequest(BaseModel):
    """Solicitud para enviar código"""
    assignment_id: str = Field(description="ID de la tarea")
    code_content: str = Field(description="Contenido del código")
    language: str = Field(description="Lenguaje de programación")


class SubmissionResponse(BaseModel):
    """Respuesta de envío"""
    id: str = Field(description="ID del envío")
    assignment_id: str = Field(description="ID de la tarea")
    student_id: str = Field(description="ID del estudiante")
    status: SubmissionStatus = Field(description="Estado del envío")
    language: str = Field(description="Lenguaje")
    attempt_number: int = Field(description="Número de intento")
    submitted_at: datetime = Field(description="Fecha de envío")
    execution_completed_at: Optional[datetime] = Field(None, description="Fecha de ejecución")
    grading_completed_at: Optional[datetime] = Field(None, description="Fecha de calificación")
    created_at: datetime = Field(description="Fecha de creación")

    class Config:
        from_attributes = True


class SubmissionHistoryResponse(BaseModel):
    """Historial de envíos"""
    total_attempts: int = Field(description="Total de intentos")
    submissions: List[SubmissionResponse] = Field(description="Lista de envíos")
