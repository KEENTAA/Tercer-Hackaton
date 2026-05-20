# Execution Service - Modelos de Dominio

from enum import Enum
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, Enum as SQLEnum, Text, Float, JSON
from sqlalchemy.orm import declarative_base
import uuid

Base = declarative_base()


class ExecutionStatus(str, Enum):
    """Estados de ejecución"""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    TIMEOUT = "timeout"
    SANDBOX_ERROR = "sandbox_error"


class ExecutionLog(Base):
    """Log de ejecución"""
    __tablename__ = "execution_logs"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    submission_id = Column(String, nullable=False, index=True)
    status = Column(SQLEnum(ExecutionStatus), default=ExecutionStatus.PENDING)
    language = Column(String, nullable=False)
    code_content = Column(Text, nullable=False)
    stdout = Column(Text, nullable=True)
    stderr = Column(Text, nullable=True)
    return_code = Column(Integer, nullable=True)
    execution_time_ms = Column(Integer, nullable=True)
    memory_used_mb = Column(Float, nullable=True)
    test_results = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class TestCase(Base):
    """Caso de prueba"""
    __tablename__ = "test_cases"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    assignment_id = Column(String, nullable=False, index=True)
    name = Column(String, nullable=False)
    input_data = Column(Text, nullable=False)
    expected_output = Column(Text, nullable=False)
    timeout_seconds = Column(Integer, default=30)
    weight = Column(Float, default=1.0)
    created_at = Column(DateTime, default=datetime.utcnow)


class ExecutionResult(Base):
    """Resultado de ejecución"""
    __tablename__ = "execution_results"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    execution_log_id = Column(String, nullable=False, index=True)
    test_case_id = Column(String, nullable=False)
    passed = Column(Integer, default=0)
    output = Column(Text, nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
