from sqlalchemy import Column, String, Integer, Text, DateTime, Enum as SQLEnum, JSON
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import enum

Base = declarative_base()


class EventType(str, enum.Enum):
    USER_CREATED = "user_created"
    USER_UPDATED = "user_updated"
    USER_DELETED = "user_deleted"
    ASSIGNMENT_CREATED = "assignment_created"
    ASSIGNMENT_PUBLISHED = "assignment_published"
    SUBMISSION_CREATED = "submission_created"
    EXECUTION_STARTED = "execution_started"
    EXECUTION_COMPLETED = "execution_completed"
    GRADING_COMPLETED = "grading_completed"
    PLAGIARISM_ANALYZED = "plagiarism_analyzed"
    LOGIN_SUCCESS = "login_success"
    LOGIN_FAILED = "login_failed"


class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    event_type = Column(SQLEnum(EventType), nullable=False, index=True)
    user_id = Column(Integer, nullable=True, index=True)
    resource_type = Column(String(100), nullable=True, index=True)
    resource_id = Column(Integer, nullable=True, index=True)
    action = Column(String(100), nullable=False)
    status = Column(String(50), default="success", nullable=False)
    description = Column(Text, nullable=True)
    metadata = Column(JSON, nullable=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    def __repr__(self):
        return f"<AuditLog {self.id} - {self.event_type}>"
