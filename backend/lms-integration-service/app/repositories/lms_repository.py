from sqlalchemy.orm import Session
from ..domain.models import LMSIntegration, LMSCourseMapping
from ..schemas.lms import LMSIntegrationCreate, LMSCourseMappingCreate
from typing import Optional, List


class LMSRepository:
    def __init__(self, db: Session):
        self.db = db
    
    async def create_integration(self, data: LMSIntegrationCreate) -> LMSIntegration:
        db_obj = LMSIntegration(**data.dict())
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj
    
    async def get_integration(self, integration_id: int) -> Optional[LMSIntegration]:
        return self.db.query(LMSIntegration).filter(
            LMSIntegration.id == integration_id
        ).first()
    
    async def list_integrations(self, skip: int = 0, limit: int = 100) -> List[LMSIntegration]:
        return self.db.query(LMSIntegration).offset(skip).limit(limit).all()
    
    async def create_course_mapping(self, data: LMSCourseMappingCreate) -> LMSCourseMapping:
        db_obj = LMSCourseMapping(**data.dict())
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj
    
    async def get_course_mapping(self, mapping_id: int) -> Optional[LMSCourseMapping]:
        return self.db.query(LMSCourseMapping).filter(
            LMSCourseMapping.id == mapping_id
        ).first()
    
    async def get_course_mapping_by_lms_course(self, lms_course_id: str) -> Optional[LMSCourseMapping]:
        return self.db.query(LMSCourseMapping).filter(
            LMSCourseMapping.lms_course_id == lms_course_id
        ).first()
