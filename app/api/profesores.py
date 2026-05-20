from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.core.security import RoleChecker
from app.models.usuarios import Usuario
from app.models.auditoria import HistorialAuditoria
from app.crud import crud_task, crud_user
from app.schemas.cursos import CursoCreate, CursoResponse, CursoUpdate
from app.schemas.tareas import TareaCreate, TareaResponse, TareaUpdate
from app.schemas.usuarios import UsuarioResponse

router = APIRouter(prefix="/profesor", tags=["Panel de Profesores"])

# Restricción global para este router
require_profesor = RoleChecker(["PROFESOR"])


# ==========================================
# GESTIÓN DE ALUMNOS
# ==========================================

@router.get("/estudiantes", response_model=List[UsuarioResponse])
def listar_todos_los_estudiantes(
    skip: int = 0, limit: int = 100,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_profesor)
):
    """Obtiene la lista de todos los estudiantes registrados en el sistema."""
    usuarios = crud_user.get_users(db, skip=skip, limit=limit)
    # Filtramos solo los que tienen rol ESTUDIANTE
    return [u for u in usuarios if u.rol == "ESTUDIANTE"]


# ==========================================
# CRUD DE CURSOS
# ==========================================

@router.get("/cursos", response_model=List[CursoResponse])
def listar_mis_cursos(
    db: Session = Depends(get_db), 
    current_user: Usuario = Depends(require_profesor)
):
    """Lista todos los cursos creados por el profesor autenticado."""
    return crud_task.get_cursos_by_profesor(db, profesor_id=current_user.id_usuario)

@router.post("/cursos", response_model=CursoResponse, status_code=status.HTTP_201_CREATED)
def crear_nuevo_curso(
    curso: CursoCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_profesor)
):
    """Crea una nueva aula virtual."""
    return crud_task.create_curso(
        db=db,
        curso=curso,
        id_profesor=current_user.id_usuario
    )

@router.put("/cursos/{id_curso}", response_model=CursoResponse)
def actualizar_curso(
    id_curso: int, 
    curso_in: CursoUpdate, 
    db: Session = Depends(get_db), 
    current_user: Usuario = Depends(require_profesor)
):
    """Edita el nombre o gestión de un curso existente."""
    curso_db = crud_task.get_curso_by_id(db, curso_id=id_curso)
    if not curso_db or curso_db.id_profesor != current_user.id_usuario:
        raise HTTPException(status_code=403, detail="No puedes editar un curso que no te pertenece.")
    return crud_task.update_curso(db=db, curso_id=id_curso, curso_in=curso_in)

@router.delete("/cursos/{id_curso}", status_code=status.HTTP_204_NO_CONTENT)
def borrar_curso(
    id_curso: int, 
    db: Session = Depends(get_db), 
    current_user: Usuario = Depends(require_profesor)
):
    """Elimina un curso y todo su contenido en cascada (Tareas, Criterios, Intentos)."""
    curso_db = crud_task.get_curso_by_id(db, curso_id=id_curso)
    if not curso_db or curso_db.id_profesor != current_user.id_usuario:
        raise HTTPException(status_code=403, detail="No tienes permiso para borrar este curso.")
    crud_task.delete_curso(db=db, curso_id=id_curso)
    return None


# ==========================================
# CRUD DE TAREAS Y CRITERIOS
# ==========================================

@router.get("/cursos/{id_curso}/tareas", response_model=List[TareaResponse])
def listar_tareas_de_curso(
    id_curso: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_profesor)
):
    """Ve todas las tareas asignadas a un curso específico."""
    curso_db = crud_task.get_curso_by_id(db, curso_id=id_curso)
    if not curso_db or curso_db.id_profesor != current_user.id_usuario:
        raise HTTPException(status_code=403, detail="No tienes acceso a este curso.")
    return crud_task.get_tareas_by_curso(db, curso_id=id_curso)

@router.post("/tareas", response_model=TareaResponse, status_code=status.HTTP_201_CREATED)
def asignar_tarea_con_criterios(
    tarea: TareaCreate, 
    db: Session = Depends(get_db), 
    current_user: Usuario = Depends(require_profesor)
):
    """Crea una tarea con su rúbrica (suma de criterios debe ser 100)."""
    curso_db = crud_task.get_curso_by_id(db, curso_id=tarea.id_curso)
    if not curso_db or curso_db.id_profesor != current_user.id_usuario:
        raise HTTPException(status_code=403, detail="No tienes autorización en este curso.")
        
    if sum(c.ponderacion for c in tarea.criterios) != 100:
        raise HTTPException(status_code=400, detail="La suma de los criterios debe ser exactamente 100.00.")
        
    return crud_task.create_tarea_con_criterios(db=db, tarea=tarea)

@router.put("/tareas/{id_tarea}", response_model=TareaResponse)
def extender_o_modificar_tarea(
    id_tarea: int,
    tarea_in: TareaUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_profesor)
):
    """Útil para extender fechas límite o corregir descripciones."""
    tarea_db = crud_task.get_tarea_by_id(db, tarea_id=id_tarea)
    if not tarea_db:
        raise HTTPException(status_code=404, detail="Tarea no encontrada.")
        
    # Verificar propiedad a través del curso
    curso_db = crud_task.get_curso_by_id(db, curso_id=tarea_db.id_curso)
    if curso_db.id_profesor != current_user.id_usuario:
        raise HTTPException(status_code=403, detail="No puedes modificar tareas de otros profesores.")
        
    return crud_task.update_tarea(db=db, tarea_id=id_tarea, tarea_in=tarea_in)

@router.delete("/tareas/{id_tarea}", status_code=status.HTTP_204_NO_CONTENT)
def anular_tarea(
    id_tarea: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_profesor)
):
    """Elimina una tarea de la plataforma."""
    tarea_db = crud_task.get_tarea_by_id(db, tarea_id=id_tarea)
    if not tarea_db:
        raise HTTPException(status_code=404, detail="Tarea no encontrada.")
        
    curso_db = crud_task.get_curso_by_id(db, curso_id=tarea_db.id_curso)
    if curso_db.id_profesor != current_user.id_usuario:
        raise HTTPException(status_code=403, detail="No puedes borrar esta tarea.")
        
    crud_task.delete_tarea(db=db, tarea_id=id_tarea)
    return None


# ==========================================
# REPORTES Y AUDITORÍA
# ==========================================

@router.get("/auditoria", status_code=status.HTTP_200_OK)
def ver_reporte_auditoria(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_profesor)
):
    """Historial inmutable de cambios (Paginado)."""
    logs = db.query(HistorialAuditoria)\
             .order_by(HistorialAuditoria.fecha_cambio.desc())\
             .offset(skip).limit(limit).all()
    total_logs = db.query(HistorialAuditoria).count()
    
    return {
        "total_registros": total_logs,
        "skip": skip,
        "limit": limit,
        "data": logs
    }