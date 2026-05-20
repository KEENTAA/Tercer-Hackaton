from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from typing import List

from app.db.session import get_db
from app.core.security import RoleChecker
from app.models.usuarios import Usuario
from app.models.tareas import Intento
from app.crud import crud_task, crud_attempt
from app.schemas.intentos import IntentoCreate, IntentoResponse
from app.schemas.tareas import TareaResponse
from app.schemas.matriculas import MatriculaCreate, MatriculaResponse

router = APIRouter(prefix="/estudiante", tags=["Panel de Estudiantes"])
require_estudiante = RoleChecker(["ESTUDIANTE"])

# --- GET: Listar Tareas Disponibles ---
@router.get("/tareas/{id_curso}", response_model=List[TareaResponse])
def ver_tareas_del_curso(
    id_curso: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, le=100),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_estudiante)
):
    """Lista las tareas pendientes y pasadas de un curso específico."""
    return crud_task.get_tareas_by_curso(db, curso_id=id_curso, skip=skip, limit=limit)


# --- GET: Historial de Intentos ---
@router.get("/intentos", response_model=List[IntentoResponse])
def ver_mis_intentos(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, le=100),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_estudiante)
):
    """Recupera el historial completo de envíos del alumno logueado."""
    return crud_attempt.get_intentos_by_estudiante(db, id_estudiante=current_user.id_usuario, skip=skip, limit=limit)


# --- POST: Subir un nuevo Intento (PUNTO DE CONTROL CRÍTICO) ---
@router.post("/intentos", response_model=IntentoResponse, status_code=status.HTTP_201_CREATED)
def enviar_tarea(
    intento: IntentoCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_estudiante)
):
    """Sube el código fuente validando estrictamente la fecha límite de la tarea."""
    tarea = crud_task.get_tarea_by_id(db, tarea_id=intento.id_tarea)
    if not tarea:
        raise HTTPException(status_code=404, detail="La tarea especificada no existe.")

    # PUNTO DE CONTROL CRÍTICO: Validación de tiempo real
    # Aseguramos que ambas fechas tengan la misma zona horaria (tz-aware o tz-naive)
    ahora = datetime.now()
    if ahora > tarea.fecha_limite:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Plazo vencido. La fecha límite era {tarea.fecha_limite.strftime('%Y-%m-%d %H:%M:%S')}."
        )

    return crud_attempt.create_intento(db=db, intento_in=intento, id_estudiante=current_user.id_usuario)


# --- PUT: Corregir el enlace del código enviado ---
@router.put("/intentos/{id_intento}", response_model=IntentoResponse)
def actualizar_envio(
    id_intento: int,
    nueva_url: str = Query(..., description="Nueva URL del repositorio o archivo"),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_estudiante)
):
    """Permite corregir el enlace enviado SOLO si aún no ha sido procesado ni ha vencido el plazo."""
    intento_db = crud_attempt.get_intento_by_id(db, id_intento)
    if not intento_db or intento_db.id_estudiante != current_user.id_usuario:
        raise HTTPException(status_code=404, detail="Intento no encontrado.")
    
    if intento_db.estado != "ENVIADO":
        raise HTTPException(status_code=400, detail="No puedes modificar un intento que ya está en procesamiento o calificado.")

    tarea = crud_task.get_tarea_by_id(db, tarea_id=intento_db.id_tarea)
    if datetime.now() > tarea.fecha_limite:
        raise HTTPException(status_code=403, detail="Plazo vencido. Ya no puedes modificar esta entrega.")

    intento_db.url_codigo_fuente = nueva_url
    db.commit()
    db.refresh(intento_db)
    return intento_db


# --- DELETE: Retirar una entrega ---
@router.delete("/intentos/{id_intento}", status_code=status.HTTP_204_NO_CONTENT)
def retirar_envio(
    id_intento: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_estudiante)
):
    """Elimina el envío, útil si el estudiante se equivocó de archivo (Sujeto a reglas de estado)."""
    intento_db = crud_attempt.get_intento_by_id(db, id_intento)
    if not intento_db or intento_db.id_estudiante != current_user.id_usuario:
        raise HTTPException(status_code=404, detail="Intento no encontrado.")
        
    if intento_db.estado != "ENVIADO":
        raise HTTPException(status_code=400, detail="Imposible eliminar. El intento ya fue tomado por el motor de calificación.")

    db.delete(intento_db)
    db.commit()
    return None

# --- POST: Inscribirse a un curso ---
@router.post("/cursos/inscribirse", response_model=MatriculaResponse, status_code=status.HTTP_201_CREATED)
def inscribirse_a_curso(
    matricula_in: MatriculaCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_estudiante)
):
    """Permite al estudiante matricularse en un curso usando el id_curso."""
    curso = crud_task.get_curso_by_id(db, curso_id=matricula_in.id_curso)
    if not curso:
        raise HTTPException(status_code=404, detail="El curso no existe.")
        
    return crud_task.inscribir_estudiante_en_curso(
        db=db, id_estudiante=current_user.id_usuario, id_curso=matricula_in.id_curso
    )

from app.models.cursos import Matricula
# --- GET: Ver Tareas (AHORA PROTEGIDO POR MATRÍCULA) ---
@router.get("/cursos/{id_curso}/tareas", response_model=List[TareaResponse])
def ver_tareas_del_curso(
    id_curso: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, le=100),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_estudiante)
):
    """Lista las tareas SOLO si el estudiante está formalmente inscrito en el curso."""
    # Validación de seguridad: Verificar matrícula activa
    inscrito = db.query(Matricula).filter(
        Matricula.id_estudiante == current_user.id_usuario,
        Matricula.id_curso == id_curso
    ).first()
    
    if not inscrito:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="No tienes acceso a las tareas de este curso porque no estás inscrito."
        )
        
    return crud_task.get_tareas_by_curso(db, curso_id=id_curso, skip=skip, limit=limit)