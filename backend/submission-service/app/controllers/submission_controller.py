# Submission Service - Controlador

from fastapi import APIRouter, Depends, Header
from sqlalchemy.orm import Session
from ..services.submission_service import SubmissionService
from ..schemas.submission import SubmitCodeRequest, SubmissionResponse, SubmissionHistoryResponse
from ...shared.schemas import DataResponse, ResponseBase
from ...shared.exceptions import ApplicationException
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/submissions", tags=["submissions"])


async def get_db() -> Session:
    """Obtener sesión de base de datos"""
    from sqlalchemy import create_engine
    from ..config import settings
    from ..domain.models import Submission, SubmissionFile, Base
    
    engine = create_engine(settings.database_url)
    Base.metadata.create_all(bind=engine)
    
    from sqlalchemy.orm import sessionmaker
    db_session = sessionmaker(engine)
    db = db_session()
    try:
        yield db
    finally:
        db.close()


async def get_submission_service(db: Session = Depends(get_db)) -> SubmissionService:
    """Obtener servicio de envíos"""
    return SubmissionService(db)


async def verify_token(authorization: str = Header(None)) -> str:
    """Verificar token JWT"""
    if not authorization:
        raise ApplicationException("Token requerido", "UNAUTHORIZED", 401)
    
    parts = authorization.split(" ")
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise ApplicationException("Formato de token inválido", "UNAUTHORIZED", 401)
    
    return parts[1]


@router.post(
    "/",
    response_model=DataResponse[SubmissionResponse],
    status_code=201,
    summary="Enviar código",
    description="Envía nuevo código para una tarea"
)
async def submit_code(
    request: SubmitCodeRequest,
    token: str = Depends(verify_token),
    service: SubmissionService = Depends(get_submission_service)
):
    """Enviar código"""
    try:
        # TODO: Extraer student_id desde el token JWT
        student_id = "student-123"  # Placeholder
        
        submission = await service.submit_code(student_id, request)
        
        return {
            "success": True,
            "data": submission
        }
    except ApplicationException as e:
        return {
            "success": False,
            "error": e.message,
            "code": e.code,
            "data": None
        }


@router.get(
    "/history/{assignment_id}",
    response_model=DataResponse[SubmissionHistoryResponse],
    status_code=200,
    summary="Historial de envíos",
    description="Obtiene el historial de envíos de un estudiante para una tarea"
)
async def get_submission_history(
    assignment_id: str,
    token: str = Depends(verify_token),
    service: SubmissionService = Depends(get_submission_service)
):
    """Obtener historial"""
    try:
        # TODO: Extraer student_id desde el token JWT
        student_id = "student-123"
        
        total, submissions = await service.get_submission_history(student_id, assignment_id)
        
        return {
            "success": True,
            "data": {
                "total_attempts": total,
                "submissions": submissions
            }
        }
    except ApplicationException as e:
        return {
            "success": False,
            "error": e.message,
            "code": e.code,
            "data": None
        }


@router.get(
    "/{submission_id}",
    response_model=DataResponse[SubmissionResponse],
    status_code=200,
    summary="Obtener detalles del envío",
    description="Obtiene los detalles de un envío específico"
)
async def get_submission(
    submission_id: str,
    token: str = Depends(verify_token),
    service: SubmissionService = Depends(get_submission_service)
):
    """Obtener envío"""
    try:
        submission = await service.get_submission(submission_id)
        
        return {
            "success": True,
            "data": submission
        }
    except ApplicationException as e:
        return {
            "success": False,
            "error": e.message,
            "code": e.code,
            "data": None
        }
