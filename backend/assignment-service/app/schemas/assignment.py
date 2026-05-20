from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, date
from enum import Enum


class AssignmentType(str, Enum):
    CODING = "coding"
    QUIZ = "quiz"
    PROJECT = "project"
    ESSAY = "essay"


class AssignmentStatus(str, Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    CLOSED = "closed"
    ARCHIVED = "archived"


class AssignmentBase(BaseModel):
    course_id: int
    title: str = Field(..., min_length=5, max_length=255)
    description: str = Field(..., min_length=10)
    type: AssignmentType = AssignmentType.CODING
    due_date: date
    max_score: float = Field(default=100.0, ge=0)
    allow_multiple_submissions: bool = True
    allow_late_submission: bool = False
    instructions: Optional[str] = None


class AssignmentCreate(AssignmentBase):
    pass


class AssignmentUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    due_date: Optional[date] = None
    max_score: Optional[float] = None
    status: Optional[AssignmentStatus] = None
    instructions: Optional[str] = None


class AssignmentResponse(AssignmentBase):
    id: int
    status: AssignmentStatus
    created_at: datetime
    updated_at: datetime
    published_at: Optional[datetime] = None
    closed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
