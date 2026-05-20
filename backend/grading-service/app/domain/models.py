# Grading Service - Modelos de Dominio

from enum import Enum
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, Enum as SQLEnum, Text, Float, JSON
from sqlalchemy.orm import declarative_base
import uuid

Base = declarative_base()


class GradingStatus(str, Enum):
    """Estados de calificación"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class Grade(Base):
    """Calificación"""
    __tablename__ = "grades"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    submission_id = Column(String, nullable=False, index=True)
    assignment_id = Column(String, nullable=False)
    student_id = Column(String, nullable=False)
    score = Column(Float, nullable=False)
    max_score = Column(Float, default=100.0)
    percentage = Column(Float, nullable=False)
    status = Column(SQLEnum(GradingStatus), default=GradingStatus.PENDING)
    feedback = Column(Text, nullable=True)
    rubric_scores = Column(JSON, nullable=True)
    execution_score = Column(Float, nullable=True)
    code_quality_score = Column(Float, nullable=True)
    graded_at = Column(DateTime, nullable=True)
    graded_by = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class Rubric(Base):
    """Rúbrica de calificación"""
    __tablename__ = "grade_rubrics"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    assignment_id = Column(String, nullable=False, index=True)
    name = Column(String, nullable=False)
    criteria = Column(JSON, nullable=False)  # {criterio: {description, max_points}}
    total_points = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
