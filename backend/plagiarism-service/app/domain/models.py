# Plagiarism Service - Modelos de Dominio

from enum import Enum
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, Enum as SQLEnum, Text, Float
from sqlalchemy.orm import declarative_base
import uuid

Base = declarative_base()


class PlagiarismStatus(str, Enum):
    """Estados del análisis de plagio"""
    PENDING = "pending"
    ANALYZING = "analyzing"
    COMPLETED = "completed"
    FAILED = "failed"


class CodeSignature(Base):
    """Firma de código para comparación"""
    __tablename__ = "code_signatures"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    submission_id = Column(String, nullable=False, index=True)
    student_id = Column(String, nullable=False)
    assignment_id = Column(String, nullable=False)
    fingerprint = Column(Text, nullable=False)  # Hash normalizado
    source_hash = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class PlagiarismReport(Base):
    """Reporte de plagio"""
    __tablename__ = "plagiarism_reports"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    submission_id = Column(String, nullable=False, index=True)
    assignment_id = Column(String, nullable=False)
    student_id = Column(String, nullable=False)
    status = Column(SQLEnum(PlagiarismStatus), default=PlagiarismStatus.PENDING)
    plagiarism_percentage = Column(Float, default=0.0)
    analysis_details = Column(Text, nullable=True)
    analyzed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class PlagiarismMatch(Base):
    """Coincidencias en plagio"""
    __tablename__ = "plagiarism_matches"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    report_id = Column(String, nullable=False, index=True)
    submission_id_1 = Column(String, nullable=False)
    submission_id_2 = Column(String, nullable=False)
    student_id_1 = Column(String, nullable=False)
    student_id_2 = Column(String, nullable=False)
    similarity_percentage = Column(Float, nullable=False)
    matched_lines = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
