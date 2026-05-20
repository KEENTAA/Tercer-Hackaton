from pydantic import BaseModel, Field
from typing import Optional, Any
from datetime import datetime
from enum import Enum


class EventType(str, Enum):
    USER_CREATED = "user_created"
    USER_UPDATED = "user_updated"
    SUBMISSION_CREATED = "submission_created"
    EXECUTION_COMPLETED = "execution_completed"
    GRADING_COMPLETED = "grading_completed"
    PLAGIARISM_ANALYZED = "plagiarism_analyzed"


class AuditLogCreate(BaseModel):
    event_type: EventType
    user_id: Optional[int] = None
    resource_type: Optional[str] = None
    resource_id: Optional[int] = None
    action: str
    status: str = "success"
    description: Optional[str] = None
    metadata: Optional[dict[str, Any]] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None


class AuditLogResponse(BaseModel):
    id: int
    event_type: EventType
    user_id: Optional[int] = None
    resource_type: Optional[str] = None
    resource_id: Optional[int] = None
    action: str
    status: str
    description: Optional[str] = None
    metadata: Optional[dict[str, Any]] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    timestamp: datetime
    
    class Config:
        from_attributes = True
