import os
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """
    Configuración centralizada de la aplicación.
    Todas las variables se cargan desde el archivo .env
    """

    # --- Información de la aplicación ---
    APP_NAME: str = "MS2 - Motor de Ejecución y Evaluación"
    APP_VERSION: str = "1.0.0"
    APP_ENV: str = "development"
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000

    # --- Seguridad y Base de Datos ---
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    # --- Límites del sandbox (Motor de ejecución) ---
    SANDBOX_MAX_TIMEOUT_MS: int = 10000
    SANDBOX_MAX_MEMORY_KB: int = 65536

    # Busca el archivo .env en la raíz del proyecto (Sintaxis moderna Pydantic V2)
    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".env"),
        extra="ignore",
        case_sensitive=False
    )

# Instancia global para mantener compatibilidad con las importaciones actuales
settings = Settings()

@lru_cache()
def get_settings() -> Settings:
    """
    Obtiene las configuraciones (cacheadas).
    Usar esta función en las inyecciones de dependencias de FastAPI (Depends).
    """
    return settings