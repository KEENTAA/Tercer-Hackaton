# Plagiarism Service - Config
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    service_name: str = "Plagiarism Service"
    service_port: int = 8007
    service_host: str = "0.0.0.0"
    database_url: str = "postgresql://user:password@plagiarism-db:5432/plagiarism_db"
    rabbitmq_host: str = "rabbitmq"
    rabbitmq_port: int = 5672
    rabbitmq_user: str = "guest"
    rabbitmq_password: str = "guest"
    plagiarism_threshold: float = 0.75
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()
