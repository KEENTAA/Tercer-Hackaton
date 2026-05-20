"""
Configuración de la base de datos PostgreSQL con SQLAlchemy 2.x.
Define el engine, SessionLocal y la clase Base para ORM declarativo.
"""

import logging
from typing import Generator

from sqlalchemy import create_engine, event
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import get_settings

logger = logging.getLogger(__name__)

settings = get_settings()


class Base(DeclarativeBase):
    """
    Clase base para todos los modelos ORM de SQLAlchemy.
    Hereda de aquí para que SQLAlchemy registre automáticamente los modelos.
    """

    pass


# Crear el engine de conexión a PostgreSQL
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,  # Verifica la conexión antes de usarla
    pool_size=10,
    max_overflow=20,
    echo=(settings.APP_ENV == "development"),  # Mostrar SQL solo en dev
)

# Registrar evento para verificar la conexión a BD
@event.listens_for(engine, "connect")
def receive_connect(dbapi_conn, connection_record):
    """
    Event listener que se ejecuta cuando se conecta a la BD.
    Útil para debugging y logging.
    """
    logger.debug("Conexión establecida con PostgreSQL")


# Session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    class_=Session,
)


def get_db() -> Generator[Session, None, None]:
    """
    Dependencia de FastAPI para inyectar sesiones de BD en los endpoints.
    Usa context manager para garantizar que la sesión se cierre siempre.

    Yields:
        Session: Sesión de BD para usar en el endpoint.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """
    Inicializa la base de datos: crea todas las tablas definidas en los modelos.
    Se llama una sola vez al startup de la aplicación.
    """
    try:
        # Importar modelos para que SQLAlchemy los registre en Base.metadata
        from app import models  # noqa: F401

        # Crear todas las tablas
        Base.metadata.create_all(bind=engine)
        logger.info("✓ Base de datos inicializada correctamente")
    except Exception as e:
        logger.error(f"✗ Error al inicializar la base de datos: {e}")
        raise
