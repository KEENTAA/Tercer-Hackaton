from sqlalchemy import Column, String, Integer, Text, DateTime, Float, Boolean, Enum as SQLEnum, ForeignKey, Date
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import enum

Base = declarative_base()


class AssignmentType(str, enum.Enum):
    CODING = "coding"
    QUIZ = "quiz"
    PROJECT = "project"
    ESSAY = "essay"


class AssignmentStatus(str, enum.Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    CLOSED = "closed"
    ARCHIVED = "archived"


class Assignment(Base):
    __tablename__ = "assignments"
    
    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, nullable=False, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    type = Column(SQLEnum(AssignmentType), default=AssignmentType.CODING, nullable=False)
    status = Column(SQLEnum(AssignmentStatus), default=AssignmentStatus.DRAFT, nullable=False)
    
    # Fechas
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    due_date = Column(Date, nullable=False)
    published_at = Column(DateTime, nullable=True)
    closed_at = Column(DateTime, nullable=True)
    
    # Configuración
    max_score = Column(Float, default=100.0, nullable=False)
    allow_multiple_submissions = Column(Boolean, default=True, nullable=False)
    allow_late_submission = Column(Boolean, default=False, nullable=False)
    
    # Metadata
    instructions = Column(Text, nullable=True)
    rubric = Column(Text, nullable=True)
    test_cases = Column(Text, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f"<Assignment {self.id} - {self.title}>"


class GradingCriteria(Base):
    __tablename__ = "grading_criteria"
    
    id = Column(Integer, primary_key=True, index=True)
    assignment_id = Column(Integer, ForeignKey("assignments.id"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    weight = Column(Float, default=1.0, nullable=False)
    max_points = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
