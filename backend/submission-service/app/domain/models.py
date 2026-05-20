# Submission Service - Modelos de Dominio

from enum import Enum
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, Enum as SQLEnum, Text, Float
from sqlalchemy.orm import declarative_base
import uuid

Base = declarative_base()


class SubmissionStatus(str, Enum):
    """Estados de un envío"""
    PENDING = "pending"
    SUBMITTED = "submitted"
    EXECUTING = "executing"
    EXECUTED = "executed"
    GRADING = "grading"
    GRADED = "graded"
    PLAGIARISM_CHECK = "plagiarism_check"
    COMPLETED = "completed"
    FAILED = "failed"


class Submission(Base):
    """Envío de código"""
    __tablename__ = "submissions"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    assignment_id = Column(String, nullable=False, index=True)
    student_id = Column(String, nullable=False, index=True)
    status = Column(SQLEnum(SubmissionStatus), default=SubmissionStatus.PENDING)
    code_content = Column(Text, nullable=False)
    language = Column(String, nullable=False)  # python, java, cpp, etc
    attempt_number = Column(Integer, default=1)
    submitted_at = Column(DateTime, default=datetime.utcnow)
    execution_completed_at = Column(DateTime, nullable=True)
    grading_completed_at = Column(DateTime, nullable=True)
    is_immutable = Column(Integer, default=0)  # No puede modificarse
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class SubmissionFile(Base):
    """Archivos de un envío"""
    __tablename__ = "submission_files"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    submission_id = Column(String, nullable=False, index=True)
    filename = Column(String, nullable=False)
    file_content = Column(Text, nullable=False)
    file_size = Column(Integer)
    mime_type = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
