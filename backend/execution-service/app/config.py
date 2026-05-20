# Execution Service - Config
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    service_name: str = "Execution Service"
    service_port: int = 8005
    service_host: str = "0.0.0.0"
    database_url: str = "postgresql://user:password@execution-db:5432/execution_db"
    rabbitmq_host: str = "rabbitmq"
    rabbitmq_port: int = 5672
    rabbitmq_user: str = "guest"
    rabbitmq_password: str = "guest"
    execution_timeout: int = 30
    sandbox_enabled: bool = True
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()
