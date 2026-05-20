# app/db/base.py
# Importamos la clase Base declarativa desde la configuración de tu sesión
from app.db.session import Base

# Importamos todos los modelos del sistema.
# IMPORTANTE: No quites ninguno; esto garantiza que Base.metadata.create_all() 
# detecte las estructuras y cree las tablas automáticamente al arrancar uvicorn.
from app.models.usuarios import Usuario
from app.models.cursos import Curso
from app.models.tareas import Tarea, CriterioCalificacion, Intento, CalificacionPorCriterio
from app.models.auditoria import HistorialAuditoria
from app.models.cursos import Matricula