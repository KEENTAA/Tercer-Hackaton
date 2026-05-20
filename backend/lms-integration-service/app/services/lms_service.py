from sqlalchemy.orm import Session
from ..repositories.lms_repository import LMSRepository
from ..schemas.lms import LMSIntegrationCreate, LMSCourseMappingCreate, LMSIntegrationResponse, LMSCourseMappingResponse
from typing import Optional
import httpx


class LMSService:
    def __init__(self, db: Session):
        self.repository = LMSRepository(db)
    
    async def create_integration(self, data: LMSIntegrationCreate) -> LMSIntegrationResponse:
        db_obj = await self.repository.create_integration(data)
        return LMSIntegrationResponse.from_orm(db_obj)
    
    async def get_integration(self, integration_id: int) -> Optional[LMSIntegrationResponse]:
        db_obj = await self.repository.get_integration(integration_id)
        if not db_obj:
            return None
        return LMSIntegrationResponse.from_orm(db_obj)
    
    async def list_integrations(self, skip: int = 0, limit: int = 100) -> dict:
        integrations = await self.repository.list_integrations(skip, limit)
        return {
            "total": len(integrations),
            "integrations": [LMSIntegrationResponse.from_orm(i) for i in integrations]
        }
    
    async def create_course_mapping(self, data: LMSCourseMappingCreate) -> LMSCourseMappingResponse:
        db_obj = await self.repository.create_course_mapping(data)
        return LMSCourseMappingResponse.from_orm(db_obj)
    
    async def sync_grade_to_lms(self, lms_course_id: str, student_id: int, grade: float, feedback: Optional[str] = None) -> bool:
        """
        Sincroniza calificaciones con el LMS externo
        """
        try:
            mapping = await self.repository.get_course_mapping_by_lms_course(lms_course_id)
            if not mapping:
                return False
            
            integration = await self.repository.get_integration(mapping.lms_integration_id)
            if not integration or not integration.is_active:
                return False
            
            # Simular llamada a LMS external API
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{integration.base_url}/api/grades/sync",
                    headers={"Authorization": f"Bearer {integration.api_key}"},
                    json={
                        "course_id": lms_course_id,
                        "student_id": student_id,
                        "grade": grade,
                        "feedback": feedback
                    }
                )
                return response.status_code == 200
        except Exception as e:
            return False
