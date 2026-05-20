from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql://user:password@postgres:5432/audit_db"
    service_name: str = "audit-service"
    service_host: str = "0.0.0.0"
    service_port: int = 8007
    log_level: str = "INFO"
    jwt_secret_key: str = "your-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    rabbitmq_url: str = "amqp://guest:guest@rabbitmq:5672/"
    redis_url: str = "redis://redis:6379"
    
    class Config:
        env_file = ".env"


settings = Settings()
