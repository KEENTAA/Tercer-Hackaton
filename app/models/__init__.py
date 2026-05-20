from app.db.session import Base
from app.models.usuarios import Usuario, CursoEstudiante
from app.models.cursos import Curso
from app.models.tareas import Tarea, CriterioCalificacion, Intento, CalificacionPorCriterio
from app.models.auditoria import HistorialAuditoria
# Importamos los listeners para que se registren en el ciclo de vida de SQLAlchemy
from app.utils import audit_listeners 

__all__ = [
    "Base",
    "Usuario",
    "CursoEstudiante",
    "Curso",
    "Tarea",
    "CriterioCalificacion",
    "Intento",
    "CalificacionPorCriterio",
    "HistorialAuditoria"
]