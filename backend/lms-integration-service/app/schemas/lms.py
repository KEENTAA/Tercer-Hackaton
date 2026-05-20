from pydantic import BaseModel, HttpUrl
from typing import Optional, Any
from datetime import datetime


class LMSIntegrationCreate(BaseModel):
    lms_type: str
    name: str
    base_url: str
    api_key: str
    configuration: Optional[dict[str, Any]] = None


class LMSIntegrationResponse(LMSIntegrationCreate):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class LMSCourseMappingCreate(BaseModel):
    lms_course_id: str
    internal_course_id: int
    lms_integration_id: int
    sync_grades: bool = True


class LMSCourseMappingResponse(LMSCourseMappingCreate):
    id: int
    last_sync: Optional[datetime] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class GradeSyncRequest(BaseModel):
    submission_id: int
    grade: float
    feedback: Optional[str] = None
