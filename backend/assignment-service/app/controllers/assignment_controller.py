from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from ..config import settings
from ..schemas.assignment import AssignmentCreate, AssignmentUpdate, AssignmentResponse
from ..services.assignment_service import AssignmentService


router = APIRouter(prefix="/api/v1/assignments", tags=["assignments"])


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


@router.post("/", response_model=AssignmentResponse, status_code=201)
async def create_assignment(assignment_data: AssignmentCreate, db: Session = Depends(get_db)):
    """Crear nueva tarea"""
    service = AssignmentService(db)
    return await service.create_assignment(assignment_data)


@router.get("/{assignment_id}", response_model=AssignmentResponse)
async def get_assignment(assignment_id: int, db: Session = Depends(get_db)):
    """Obtener tarea por ID"""
    service = AssignmentService(db)
    assignment = await service.get_assignment(assignment_id)
    if not assignment:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    return assignment


@router.get("/course/{course_id}", response_model=dict)
async def get_course_assignments(
    course_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """Obtener tareas de un curso"""
    service = AssignmentService(db)
    return await service.get_course_assignments(course_id, skip, limit)


@router.get("/", response_model=dict)
async def list_assignments(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """Listar todas las tareas"""
    service = AssignmentService(db)
    return await service.list_assignments(skip, limit)


@router.put("/{assignment_id}", response_model=AssignmentResponse)
async def update_assignment(
    assignment_id: int,
    assignment_data: AssignmentUpdate,
    db: Session = Depends(get_db)
):
    """Actualizar tarea"""
    service = AssignmentService(db)
    assignment = await service.update_assignment(assignment_id, assignment_data)
    if not assignment:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    return assignment


@router.post("/{assignment_id}/publish", response_model=AssignmentResponse)
async def publish_assignment(assignment_id: int, db: Session = Depends(get_db)):
    """Publicar tarea"""
    service = AssignmentService(db)
    assignment = await service.publish_assignment(assignment_id)
    if not assignment:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    return assignment


@router.post("/{assignment_id}/close", response_model=AssignmentResponse)
async def close_assignment(assignment_id: int, db: Session = Depends(get_db)):
    """Cerrar tarea"""
    service = AssignmentService(db)
    assignment = await service.close_assignment(assignment_id)
    if not assignment:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    return assignment
