from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Importación de la base de datos
from app.db.session import engine
from app.db.base import Base

# Importación de los Routers
from app.api import auth, profesores, estudiantes, runner_callback

# 1. Creación de las tablas en PostgreSQL (Incluye los triggers de auditoría si los configuraste en la BD)
Base.metadata.create_all(bind=engine)

# 2. Inicialización de la aplicación FastAPI
app = FastAPI(
    title="LMS API - Sistema de Evaluación Académica",
    description="Plataforma de gestión de tareas, calificación automática y auditoría inmutable.",
    version="1.0.0"
)

# 3. Configuración de CORS (Cross-Origin Resource Sharing)
# Esto es vital para que el frontend (Angular/React) no reciba bloqueos del navegador.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, cambiar "*" por los dominios reales (ej. "http://localhost:4200")
    allow_credentials=True,
    allow_methods=["*"],  # Permite GET, POST, PUT, DELETE, etc.
    allow_headers=["*"],
)

# 4. Inclusión de los Routers (Centralización)
app.include_router(auth.router, prefix="/api")
app.include_router(profesores.router, prefix="/api")
app.include_router(estudiantes.router, prefix="/api")
app.include_router(runner_callback.router, prefix="/api")

@app.get("/", tags=["Health Check"])
def root():
    """Ruta base para verificar que la API está viva."""
    return {
        "estado": "Online", 
        "mensaje": "Bienvenido al LMS API. Visita /docs para la documentación interactiva."
    }