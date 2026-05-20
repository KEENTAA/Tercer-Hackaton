from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql://user:password@postgres:5432/lms_db"
    service_name: str = "lms-integration-service"
    service_host: str = "0.0.0.0"
    service_port: int = 8008
    log_level: str = "INFO"
    jwt_secret_key: str = "your-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    rabbitmq_url: str = "amqp://guest:guest@rabbitmq:5672/"
    redis_url: str = "redis://redis:6379"
    
    # LMS Configuration
    lms_base_url: str = "https://lms.example.com"
    lms_api_key: str = "your-lms-api-key"
    lms_secret: str = "your-lms-secret"
    
    class Config:
        env_file = ".env"


settings = Settings()
