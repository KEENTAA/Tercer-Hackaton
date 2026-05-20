from sqlalchemy import Column, String, Integer, Text, DateTime, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class LMSIntegration(Base):
    __tablename__ = "lms_integrations"
    
    id = Column(Integer, primary_key=True, index=True)
    lms_type = Column(String(50), nullable=False)  # moodle, canvas, blackboard, etc
    name = Column(String(255), nullable=False)
    base_url = Column(String(500), nullable=False)
    api_key = Column(String(500), nullable=False)
    is_active = Column(Boolean, default=True)
    configuration = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class LMSCourseMapping(Base):
    __tablename__ = "lms_course_mappings"
    
    id = Column(Integer, primary_key=True, index=True)
    lms_course_id = Column(String(100), nullable=False)
    internal_course_id = Column(Integer, nullable=False, index=True)
    lms_integration_id = Column(Integer, nullable=False)
    sync_grades = Column(Boolean, default=True)
    last_sync = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
