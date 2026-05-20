from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.tareas import Intento, CalificacionPorCriterio
from app.schemas.intentos import IntentoCreate, IntentoUpdateEstado

# ==============================================================================
# --- SECCIÓN: LECTURA DE INTENTOS ---
# ==============================================================================

def get_intento_by_id(db: Session, id_intento: int):
    """Obtiene una entrega específica con todas sus notas por criterio."""
    return db.query(Intento).filter(Intento.id_intento == id_intento).first()

def get_intentos_by_estudiante(db: Session, id_estudiante: int, skip: int = 0, limit: int = 100):
    """Historial completo de entregas de un estudiante (Soporta paginación)."""
    return db.query(Intento).filter(Intento.id_estudiante == id_estudiante).offset(skip).limit(limit).all()

def get_intentos_by_tarea(db: Session, id_tarea: int, skip: int = 0, limit: int = 100):
    """Lista todas las entregas de una tarea específica (Útil para el panel del Profesor)."""
    return db.query(Intento).filter(Intento.id_tarea == id_tarea).offset(skip).limit(limit).all()


# ==============================================================================
# --- SECCIÓN: CREACIÓN Y CALIFICACIÓN ---
# ==============================================================================

def create_intento(db: Session, intento_in: IntentoCreate, id_estudiante: int):
    """
    Registra una nueva entrega calculando el 'numero_intento' en tiempo real.
    Nota: El listener de auditoría guardará el log de forma automática tras el commit.
    """
    # Consulta atómica: Busca el intento máximo actual de este alumno en esta tarea y le suma 1.
    # Si es su primera entrega, func.coalesce se encarga de transformarlo en 0.
    proximo_numero_intento = db.query(
        func.coalesce(func.max(Intento.numero_intento), 0)
    ).filter(
        Intento.id_tarea == intento_in.id_tarea,
        Intento.id_estudiante == id_estudiante
    ).scalar() + 1

    db_intento = Intento(
        id_tarea=intento_in.id_tarea,
        id_estudiante=id_estudiante,
        numero_intento=proximo_numero_intento,
        url_codigo_fuente=intento_in.url_codigo_fuente,
        estado="ENVIADO" # Estado por defecto al subir el archivo
    )
    
    db.add(db_intento)
    db.commit()
    db.refresh(db_intento)
    return db_intento


def registrar_calificacion_intento(db: Session, id_intento: int, calificacion_in: IntentoUpdateEstado):
    """
    Actualiza el estado de la entrega, calcula la nota global y guarda el desglose 
    por cada criterio de evaluación dentro de una misma transacción.
    """
    db_intento = db.query(Intento).filter(Intento.id_intento == id_intento).first()
    if not db_intento:
        return None

    # 1. Actualizar datos de la cabecera (Estado final y Nota acumulada)
    db_intento.estado = calificacion_in.estado
    if calificacion_in.nota_total is not None:
        db_intento.nota_total = calificacion_in.nota_total

    # 2. Si la petición incluye desglose detallado (Viene del Code Runner o rúbrica manual)
    if calificacion_in.calificaciones:
        # Limpieza preventiva: Si por alguna razón se está re-calificando, borramos el detalle anterior
        db.query(CalificacionPorCriterio).filter(CalificacionPorCriterio.id_intento == id_intento).delete()
        
        # Insertar los nuevos puntajes asignados por cada criterio
        for calif_criterio in calificacion_in.calificaciones:
            db_detalle = CalificacionPorCriterio(
                id_intento=id_intento,
                id_criterio=calif_criterio.id_criterio,
                nota_obtenida=calif_criterio.nota_obtenida,
                comentarios=calif_criterio.comentarios
            )
            db.add(db_detalle)

    db.commit()
    db.refresh(db_intento) # El listener 'after_update' se dispara aquí automáticamente detectando el cambio
    return db_intento