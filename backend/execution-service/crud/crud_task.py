from sqlalchemy.orm import Session
from app.models.cursos import Curso
from app.models.tareas import Tarea, CriterioCalificacion
from app.schemas.cursos import CursoCreate, CursoUpdate
from app.schemas.tareas import TareaCreate, TareaUpdate

# ==============================================================================
# --- SECCIÓN: GESTIÓN DE CURSOS ---
# ==============================================================================

def get_curso_by_id(db: Session, curso_id: int):
    return db.query(Curso).filter(Curso.id_curso == curso_id).first()

def get_cursos(db: Session, skip: int = 0, limit: int = 100):
    """Lista todos los cursos del sistema."""
    return db.query(Curso).offset(skip).limit(limit).all()

def get_cursos_by_profesor(db: Session, profesor_id: int):
    """Filtra las aulas virtuales asignadas a un docente."""
    return db.query(Curso).filter(Curso.id_profesor == profesor_id).all()

def create_curso(
    db: Session,
    curso: CursoCreate,
    id_profesor: int
):
    db_curso = Curso(
        codigo_curso=curso.codigo_curso,
        nombre=curso.nombre,
        gestion=curso.gestion,
        id_profesor=id_profesor
    )

    db.add(db_curso)
    db.commit()
    db.refresh(db_curso)

    return db_curso

def update_curso(db: Session, curso_id: int, curso_in: CursoUpdate):
    db_curso = db.query(Curso).filter(Curso.id_curso == curso_id).first()
    if not db_curso:
        return None
    
    update_data = curso_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_curso, field, value)
        
    db.commit()
    db.refresh(db_curso)
    return db_curso

def delete_curso(db: Session, curso_id: int):
    db_curso = db.query(Curso).filter(Curso.id_curso == curso_id).first()
    if db_curso:
        db.delete(db_curso)
        db.commit()
        return True
    return False


# ==============================================================================
# --- SECCIÓN: GESTIÓN DE TAREAS Y CRITERIOS ---
# ==============================================================================

def get_tarea_by_id(db: Session, tarea_id: int):
    """Obtiene una tarea incluyendo la carga automática de sus criterios."""
    return db.query(Tarea).filter(Tarea.id_tarea == tarea_id).first()

def get_tareas_by_curso(db: Session, curso_id: int, skip: int = 0, limit: int = 100):
    """Lista las tareas de un curso para el panel del estudiante."""
    return db.query(Tarea).filter(Tarea.id_curso == curso_id).offset(skip).limit(limit).all()

def create_tarea_con_criterios(db: Session, tarea: TareaCreate):
    """Crea una tarea junto con sus criterios de evaluación de forma atómica."""
    # 1. Insertar Cabecera de la Tarea
    db_tarea = Tarea(
        id_curso=tarea.id_curso,
        titulo=tarea.titulo,
        descripcion=tarea.descripcion,
        fecha_limite=tarea.fecha_limite
    )
    db.add(db_tarea)
    db.commit()
    db.refresh(db_tarea)

    # 2. Insertar los Criterios asociados en bloque
    for criterio in tarea.criterios:
        db_criterio = CriterioCalificacion(
            id_tarea=db_tarea.id_tarea,
            descripcion=criterio.descripcion,
            ponderacion=criterio.ponderacion
        )
        db.add(db_criterio)
    
    db.commit()
    db.refresh(db_tarea)
    return db_tarea

def update_tarea(db: Session, tarea_id: int, tarea_in: TareaUpdate):
    """Modifica datos de la tarea (como postergar la fecha límite)."""
    db_tarea = db.query(Tarea).filter(Tarea.id_tarea == tarea_id).first()
    if not db_tarea:
        return None
    
    update_data = tarea_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_tarea, field, value)
        
    db.commit()
    db.refresh(db_tarea)
    return db_tarea

def delete_tarea(db: Session, tarea_id: int):
    """
    Elimina una tarea del sistema.
    Gracias al cascade='all, delete-orphan' definido en el Modelo, 
    eliminará automáticamente criterios e intentos vinculados en cascada.
    """
    db_tarea = db.query(Tarea).filter(Tarea.id_tarea == tarea_id).first()
    if db_tarea:
        db.delete(db_tarea)
        db.commit()
        return True
    return False

#
from app.models.cursos import Matricula
from app.schemas.matriculas import MatriculaCreate

def inscribir_estudiante_en_curso(db: Session, id_estudiante: int, id_curso: int):
    """Verifica duplicados e inscribe a un estudiante en un curso."""
    # Control preventivo: ¿Ya está inscrito?
    existe = db.query(Matricula).filter(
        Matricula.id_estudiante == id_estudiante,
        Matricula.id_curso == id_curso  # Nota: Verifica si tu columna se llama id_curso o id_cur según tus modelos previos
    ).first()
    
    if existe:
        return existe

    db_matricula = Matricula(id_estudiante=id_estudiante, id_curso=id_curso)
    db.add(db_matricula)
    db.commit()
    db.refresh(db_matricula)
    return db_matricula

def get_cursos_inscritos_by_estudiante(db: Session, id_estudiante: int):
    """Retorna los cursos a los que el estudiante se ha matriculado."""
    return db.query(Curso).join(Matricula, Curso.id_curso == Matricula.id_curso).filter(
        Matricula.id_estudiante == id_estudiante
    ).all()