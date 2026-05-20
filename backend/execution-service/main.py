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
"""
Punto de entrada de la aplicación FastAPI.
Configura lifespan, CORS, middleware, manejadores de excepciones y rutas.

MS2 - Motor de Ejecución y Evaluación
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text

from app.core.config import get_settings
from app.database import get_db, init_db
from app.routes import runner
from app.schemas import HealthResponse, HealthDatabaseStatus

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

settings = get_settings()


# ══════════════════════════════════════════════════════════════════
# LIFESPAN: Startup y Shutdown
# ══════════════════════════════════════════════════════════════════


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Context manager para manejar el ciclo de vida de la aplicación.
    - Startup: Inicializar BD
    - Shutdown: Logging de cierre
    """
    # Startup
    logger.info("=" * 80)
    logger.info(f"🚀 Iniciando {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"   Entorno: {settings.APP_ENV}")
    logger.info(f"   Host: {settings.APP_HOST}:{settings.APP_PORT}")
    logger.info(f"   Base de datos: {settings.DATABASE_URL.split('@')[1] if '@' in settings.DATABASE_URL else '???'}")
    logger.info("=" * 80)

    try:
        init_db()
        logger.info("✓ Base de datos inicializada")
    except Exception as e:
        logger.error(f"✗ Error al inicializar BD: {e}")
        raise

    yield

    # Shutdown
    logger.info("=" * 80)
    logger.info("🛑 Deteniendo aplicación")
    logger.info("=" * 80)


# ══════════════════════════════════════════════════════════════════
# CREAR APLICACIÓN FASTAPI
# ══════════════════════════════════════════════════════════════════

app = FastAPI(
    title=settings.APP_NAME,
    description="Motor de Ejecución y Evaluación para sistema de calificación automática",
    version=settings.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# ══════════════════════════════════════════════════════════════════
# MIDDLEWARE CORS
# ══════════════════════════════════════════════════════════════════

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Para hackathon/desarrollo
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ══════════════════════════════════════════════════════════════════
# MANEJADOR GLOBAL DE EXCEPCIONES
# ══════════════════════════════════════════════════════════════════


@app.exception_handler(Exception)
async def exception_handler(request: Request, exc: Exception):
    """
    Manejador global de excepciones no capturadas.
    """
    logger.error(f"Excepción no manejada: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Error interno del servidor",
            "type": type(exc).__name__,
        },
    )


# ══════════════════════════════════════════════════════════════════
# ENDPOINTS DEL SISTEMA
# ══════════════════════════════════════════════════════════════════


@app.get(
    "/",
    tags=["Sistema"],
    summary="Información del servicio",
    description="Retorna información básica del microservicio",
)
async def root():
    """
    Endpoint raíz con información del servicio.
    """
    return {
        "servicio": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "entorno": settings.APP_ENV,
        "documentacion": "/docs",
    }


@app.get(
    "/health",
    response_model=HealthResponse,
    tags=["Sistema"],
    summary="Health check",
    description="Verifica el estado del servicio y la conexión a BD",
)
async def health_check() -> HealthResponse:
    """
    Verificar salud del servicio.
    Intenta conectarse a la BD para validar la conexión.
    """
    try:
        # Obtener sesión de BD
        db_gen = get_db()
        db = next(db_gen)

        # Verificar conexión con SELECT 1
        db.execute(text("SELECT 1"))

        # Cerrar sesión
        try:
            next(db_gen)
        except StopIteration:
            pass
        finally:
            db.close()

        return HealthResponse(
            status="ok",
            servicio=settings.APP_NAME,
            version=settings.APP_VERSION,
            entorno=settings.APP_ENV,
            base_de_datos=HealthDatabaseStatus(
                conectado=True,
                motor="PostgreSQL",
                version="16+",
            ),
        )

    except Exception as e:
        logger.error(f"Health check falló: {e}")
        return HealthResponse(
            status="degraded",
            servicio=settings.APP_NAME,
            version=settings.APP_VERSION,
            entorno=settings.APP_ENV,
            base_de_datos=HealthDatabaseStatus(
                conectado=False,
                motor="PostgreSQL",
                version=None,
            ),
        )


# ══════════════════════════════════════════════════════════════════
# INCLUIR ROUTERS
# ══════════════════════════════════════════════════════════════════

app.include_router(runner.router)

logger.info("✓ Routers incluidos correctamente")
