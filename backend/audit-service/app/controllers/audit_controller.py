from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from ..config import settings
from ..schemas.audit import AuditLogCreate, AuditLogResponse
from ..services.audit_service import AuditService


router = APIRouter(prefix="/api/v1/audit", tags=["audit"])


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


@router.post("/logs", response_model=AuditLogResponse, status_code=201)
async def create_log(log_data: AuditLogCreate, db: Session = Depends(get_db)):
    """Registrar evento de auditoría"""
    service = AuditService(db)
    return await service.create_log(log_data)


@router.get("/logs/{log_id}", response_model=AuditLogResponse)
async def get_log(log_id: int, db: Session = Depends(get_db)):
    """Obtener log de auditoría"""
    service = AuditService(db)
    log = await service.get_log(log_id)
    if not log:
        raise HTTPException(status_code=404, detail="Log no encontrado")
    return log


@router.get("/logs", response_model=dict)
async def list_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """Listar todos los logs"""
    service = AuditService(db)
    return await service.list_logs(skip, limit)


@router.get("/user/{user_id}", response_model=dict)
async def list_user_logs(
    user_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """Listar logs por usuario"""
    service = AuditService(db)
    return await service.list_logs_by_user(user_id, skip, limit)


@router.get("/event/{event_type}", response_model=dict)
async def list_event_logs(
    event_type: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """Listar logs por tipo de evento"""
    service = AuditService(db)
    return await service.list_logs_by_event(event_type, skip, limit)


@router.get("/resource/{resource_type}/{resource_id}", response_model=dict)
async def list_resource_logs(
    resource_type: str,
    resource_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """Listar logs por recurso"""
    service = AuditService(db)
    return await service.list_logs_by_resource(resource_type, resource_id, skip, limit)
