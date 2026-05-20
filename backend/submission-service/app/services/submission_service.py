# Submission Service - Servicio de Negocio

from sqlalchemy.orm import Session
from typing import Optional, List, Tuple
from datetime import datetime
import httpx
from ..config import settings
from ..repositories.submission_repository import SubmissionRepository
from ..schemas.submission import SubmissionResponse, SubmitCodeRequest
from ..domain.models import SubmissionStatus
from ...shared.exceptions import (
    ValidationException,
    ResourceNotFoundException,
    ExternalServiceException,
    ConflictException
)
from ...shared.schemas import SubmissionCreatedEvent
import json
import pika
import logging

logger = logging.getLogger(__name__)


class SubmissionService:
    """Servicio de gestión de envíos"""
    
    def __init__(self, db: Session):
        self.db = db
        self.repo = SubmissionRepository(db)
        self.event_publisher = EventPublisher()
    
    async def submit_code(
        self,
        student_id: str,
        request: SubmitCodeRequest
    ) -> SubmissionResponse:
        """Enviar código para una tarea"""
        
        # Validar que la tarea exista
        assignment = await self._get_assignment(request.assignment_id)
        if not assignment:
            raise ResourceNotFoundException("Tarea", request.assignment_id)
        
        # Validar que el plazo no haya vencido
        deadline = datetime.fromisoformat(assignment.get("fecha_limite"))
        if datetime.utcnow() > deadline:
            raise ConflictException("El plazo para enviar esta tarea ha vencido")
        
        # Validar contenido del código
        if not request.code_content or len(request.code_content) == 0:
            raise ValidationException("El código no puede estar vacío")
        
        # Validar lenguaje
        valid_languages = ["python", "java", "cpp", "javascript", "csharp"]
        if request.language.lower() not in valid_languages:
            raise ValidationException(f"Lenguaje no soportado. Válidos: {', '.join(valid_languages)}")
        
        # Obtener número de intento
        last_submission = await self.repo.get_latest_submission(
            request.assignment_id,
            student_id
        )
        attempt_number = (last_submission.attempt_number + 1) if last_submission else 1
        
        # Crear envío
        submission = await self.repo.create_submission(
            assignment_id=request.assignment_id,
            student_id=student_id,
            code_content=request.code_content,
            language=request.language,
            attempt_number=attempt_number
        )
        
        # Publicar evento
        event = SubmissionCreatedEvent(
            aggregate_id=submission.id,
            timestamp=datetime.utcnow().isoformat(),
            data={
                "submission_id": submission.id,
                "assignment_id": request.assignment_id,
                "student_id": student_id,
                "language": request.language,
                "attempt_number": attempt_number
            },
            user_id=student_id
        )
        await self.event_publisher.publish(event)
        
        logger.info(f"Envío creado: {submission.id}")
        
        return SubmissionResponse.model_validate(submission)
    
    async def get_submission_history(
        self,
        student_id: str,
        assignment_id: str
    ) -> Tuple[int, List[SubmissionResponse]]:
        """Obtener historial de envíos"""
        submissions = await self.repo.get_submission_history(assignment_id, student_id)
        
        responses = [SubmissionResponse.model_validate(s) for s in submissions]
        
        return len(submissions), responses
    
    async def get_submission(self, submission_id: str) -> SubmissionResponse:
        """Obtener detalles de un envío"""
        submission = await self.repo.get_submission_by_id(submission_id)
        if not submission:
            raise ResourceNotFoundException("Envío", submission_id)
        
        return SubmissionResponse.model_validate(submission)
    
    async def _get_assignment(self, assignment_id: str) -> Optional[dict]:
        """Verificar que la tarea exista en assignment-service"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{settings.assignment_service_url}/api/assignments/{assignment_id}"
                )
                if response.status_code == 200:
                    return response.json().get("data")
                return None
        except Exception as e:
            logger.error(f"Error consultando assignment-service: {e}")
            raise ExternalServiceException("assignment-service", str(e))


class EventPublisher:
    """Publicador de eventos a RabbitMQ"""
    
    async def publish(self, event: SubmissionCreatedEvent) -> None:
        """Publicar evento a RabbitMQ"""
        try:
            credentials = pika.PlainCredentials(settings.rabbitmq_user, settings.rabbitmq_password)
            parameters = pika.ConnectionParameters(
                host=settings.rabbitmq_host,
                port=settings.rabbitmq_port,
                credentials=credentials
            )
            
            connection = pika.BlockingConnection(parameters)
            channel = connection.channel()
            
            channel.exchange_declare(
                exchange='code-grading',
                exchange_type='topic',
                durable=True
            )
            
            channel.basic_publish(
                exchange='code-grading',
                routing_key=f'submission.{event.event_type}',
                body=event.model_dump_json()
            )
            
            connection.close()
            logger.info(f"Evento publicado: {event.event_type}")
        except Exception as e:
            logger.error(f"Error publicando evento: {e}")
            raise ExternalServiceException("rabbitmq", str(e))
