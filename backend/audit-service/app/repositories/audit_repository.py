from sqlalchemy.orm import Session
from sqlalchemy import and_, desc
from ..domain.models import AuditLog, EventType
from ..schemas.audit import AuditLogCreate
from datetime import datetime
from typing import Optional, List


class AuditRepository:
    def __init__(self, db: Session):
        self.db = db
    
    async def create(self, log_data: AuditLogCreate) -> AuditLog:
        db_log = AuditLog(
            event_type=log_data.event_type,
            user_id=log_data.user_id,
            resource_type=log_data.resource_type,
            resource_id=log_data.resource_id,
            action=log_data.action,
            status=log_data.status,
            description=log_data.description,
            metadata=log_data.metadata,
            ip_address=log_data.ip_address,
            user_agent=log_data.user_agent
        )
        self.db.add(db_log)
        self.db.commit()
        self.db.refresh(db_log)
        return db_log
    
    async def get_by_id(self, log_id: int) -> Optional[AuditLog]:
        return self.db.query(AuditLog).filter(AuditLog.id == log_id).first()
    
    async def list_all(self, skip: int = 0, limit: int = 100) -> List[AuditLog]:
        return self.db.query(AuditLog).order_by(
            desc(AuditLog.timestamp)
        ).offset(skip).limit(limit).all()
    
    async def list_by_user(self, user_id: int, skip: int = 0, limit: int = 100) -> List[AuditLog]:
        return self.db.query(AuditLog).filter(
            AuditLog.user_id == user_id
        ).order_by(desc(AuditLog.timestamp)).offset(skip).limit(limit).all()
    
    async def list_by_event_type(self, event_type: EventType, skip: int = 0, limit: int = 100) -> List[AuditLog]:
        return self.db.query(AuditLog).filter(
            AuditLog.event_type == event_type
        ).order_by(desc(AuditLog.timestamp)).offset(skip).limit(limit).all()
    
    async def list_by_resource(self, resource_type: str, resource_id: int, skip: int = 0, limit: int = 100) -> List[AuditLog]:
        return self.db.query(AuditLog).filter(
            and_(AuditLog.resource_type == resource_type, AuditLog.resource_id == resource_id)
        ).order_by(desc(AuditLog.timestamp)).offset(skip).limit(limit).all()
