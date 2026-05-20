from sqlalchemy.orm import Session
from ..repositories.audit_repository import AuditRepository
from ..schemas.audit import AuditLogCreate, AuditLogResponse
from ..domain.models import EventType
from typing import List, Optional


class AuditService:
    def __init__(self, db: Session):
        self.repository = AuditRepository(db)
    
    async def create_log(self, log_data: AuditLogCreate) -> AuditLogResponse:
        db_log = await self.repository.create(log_data)
        return AuditLogResponse.from_orm(db_log)
    
    async def get_log(self, log_id: int) -> Optional[AuditLogResponse]:
        db_log = await self.repository.get_by_id(log_id)
        if not db_log:
            return None
        return AuditLogResponse.from_orm(db_log)
    
    async def list_logs(self, skip: int = 0, limit: int = 100) -> dict:
        logs = await self.repository.list_all(skip, limit)
        return {
            "total": len(logs),
            "logs": [AuditLogResponse.from_orm(log) for log in logs]
        }
    
    async def list_logs_by_user(self, user_id: int, skip: int = 0, limit: int = 100) -> dict:
        logs = await self.repository.list_by_user(user_id, skip, limit)
        return {
            "total": len(logs),
            "logs": [AuditLogResponse.from_orm(log) for log in logs]
        }
    
    async def list_logs_by_event(self, event_type: str, skip: int = 0, limit: int = 100) -> dict:
        event_enum = EventType(event_type)
        logs = await self.repository.list_by_event_type(event_enum, skip, limit)
        return {
            "total": len(logs),
            "logs": [AuditLogResponse.from_orm(log) for log in logs]
        }
    
    async def list_logs_by_resource(self, resource_type: str, resource_id: int, skip: int = 0, limit: int = 100) -> dict:
        logs = await self.repository.list_by_resource(resource_type, resource_id, skip, limit)
        return {
            "total": len(logs),
            "logs": [AuditLogResponse.from_orm(log) for log in logs]
        }
