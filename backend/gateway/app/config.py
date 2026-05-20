from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # API Gateway
    service_name: str = "api-gateway"
    service_host: str = "0.0.0.0"
    service_port: int = 8000
    log_level: str = "INFO"
    
    # JWT
    jwt_secret_key: str = "your-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expiration_hours: int = 24
    
    # Services URLs
    auth_service_url: str = "http://auth-service:8001"
    user_service_url: str = "http://user-service:8004"
    assignment_service_url: str = "http://assignment-service:8005"
    submission_service_url: str = "http://submission-service:8002"
    execution_service_url: str = "http://execution-service:8003"
    grading_service_url: str = "http://grading-service:8006"
    plagiarism_service_url: str = "http://plagiarism-service:8009"
    audit_service_url: str = "http://audit-service:8007"
    lms_service_url: str = "http://lms-service:8008"
    
    # Rate Limiting
    rate_limit_enabled: bool = True
    rate_limit_requests: int = 100
    rate_limit_period: int = 60  # seconds
    
    class Config:
        env_file = ".env"


settings = Settings()
