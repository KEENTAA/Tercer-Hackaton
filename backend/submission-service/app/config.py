# Submission Service - Configuración

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Configuración del servicio"""
    
    service_name: str = "Submission Service"
    service_port: int = 8004
    service_host: str = "0.0.0.0"
    
    database_url: str = "postgresql://user:password@submission-db:5432/submission_db"
    
    rabbitmq_host: str = "rabbitmq"
    rabbitmq_port: int = 5672
    rabbitmq_user: str = "guest"
    rabbitmq_password: str = "guest"
    
    redis_host: str = "redis"
    redis_port: int = 6379
    redis_password: Optional[str] = None
    
    # URLs de otros servicios
    auth_service_url: str = "http://auth-service:8001"
    assignment_service_url: str = "http://assignment-service:8003"
    execution_service_url: str = "http://execution-service:8005"
    
    jwt_secret: str = "your-super-secret-jwt-key-change-in-production"
    jwt_algorithm: str = "HS256"
    
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
