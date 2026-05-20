from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from ..config import settings
from ..schemas.lms import LMSIntegrationCreate, LMSCourseMappingCreate, GradeSyncRequest
from ..services.lms_service import LMSService


router = APIRouter(prefix="/api/v1/lms", tags=["lms"])


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


@router.post("/integrations", status_code=201)
async def create_lms_integration(data: LMSIntegrationCreate, db: Session = Depends(get_db)):
    """Crear nueva integración con LMS"""
    service = LMSService(db)
    return await service.create_integration(data)


@router.get("/integrations/{integration_id}")
async def get_lms_integration(integration_id: int, db: Session = Depends(get_db)):
    """Obtener integración LMS"""
    service = LMSService(db)
    integration = await service.get_integration(integration_id)
    if not integration:
        raise HTTPException(status_code=404, detail="Integración no encontrada")
    return integration


@router.get("/integrations")
async def list_lms_integrations(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """Listar todas las integraciones LMS"""
    service = LMSService(db)
    return await service.list_integrations(skip, limit)


@router.post("/mappings", status_code=201)
async def create_course_mapping(data: LMSCourseMappingCreate, db: Session = Depends(get_db)):
    """Crear mapeo entre curso LMS y curso interno"""
    service = LMSService(db)
    return await service.create_course_mapping(data)


@router.post("/sync-grade")
async def sync_grade_to_lms(request: GradeSyncRequest, db: Session = Depends(get_db)):
    """Sincronizar calificación a LMS"""
    service = LMSService(db)
    success = await service.sync_grade_to_lms(
        "course_123",  # lms_course_id
        request.submission_id,
        request.grade,
        request.feedback
    )
    if not success:
        raise HTTPException(status_code=400, detail="Error al sincronizar calificación")
    return {"success": True, "message": "Calificación sincronizada"}
