"""
Configuración de la aplicación usando Pydantic Settings.
Carga variables desde archivo .env en el directorio raíz.
"""

from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Configuración centralizada del MS2 - Motor de Ejecución y Evaluación.
    Todas las variables se cargan desde el archivo .env
    """

    # Información de la aplicación
    APP_NAME: str = "MS2 - Motor de Ejecución y Evaluación"
    APP_VERSION: str = "1.0.0"
    APP_ENV: str = "development"
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000

    # Configuración de base de datos PostgreSQL
    DATABASE_URL: str = (
        "postgresql://runner_user:runner_pass@localhost:5432/db_code_runner"
    )

    # Límites del sandbox
    SANDBOX_MAX_TIMEOUT_MS: int = 10000
    SANDBOX_MAX_MEMORY_KB: int = 65536

    class Config:
        """Carga variables desde .env"""

        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """
    Obtiene las configuraciones (cacheadas).
    Usar esta función en lugar de instanciar Settings directamente.

    Returns:
        Settings: Objeto con la configuración de la aplicación.
    """
    return Settings()
