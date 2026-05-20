from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql://user:password@postgres:5432/user_db"
    
    # Service info
    service_name: str = "user-service"
    service_host: str = "0.0.0.0"
    service_port: int = 8004
    
    # Logging
    log_level: str = "INFO"
    
    # Auth
    jwt_secret_key: str = "your-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    
    # RabbitMQ
    rabbitmq_url: str = "amqp://guest:guest@rabbitmq:5672/"
    
    # Redis
    redis_url: str = "redis://redis:6379"
    
    class Config:
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
