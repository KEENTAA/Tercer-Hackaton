from sqlalchemy.orm import Session
from ..repositories.assignment_repository import AssignmentRepository
from ..schemas.assignment import AssignmentCreate, AssignmentUpdate, AssignmentResponse
from typing import List, Optional


class AssignmentService:
    def __init__(self, db: Session):
        self.repository = AssignmentRepository(db)
    
    async def create_assignment(self, assignment_data: AssignmentCreate) -> AssignmentResponse:
        db_assignment = await self.repository.create(assignment_data)
        return AssignmentResponse.from_orm(db_assignment)
    
    async def get_assignment(self, assignment_id: int) -> Optional[AssignmentResponse]:
        db_assignment = await self.repository.get_by_id(assignment_id)
        if not db_assignment:
            return None
        return AssignmentResponse.from_orm(db_assignment)
    
    async def get_course_assignments(self, course_id: int, skip: int = 0, limit: int = 100) -> dict:
        assignments = await self.repository.get_by_course(course_id, skip, limit)
        return {
            "total": len(assignments),
            "assignments": [AssignmentResponse.from_orm(a) for a in assignments]
        }
    
    async def list_assignments(self, skip: int = 0, limit: int = 100) -> dict:
        assignments = await self.repository.list_all(skip, limit)
        return {
            "total": len(assignments),
            "assignments": [AssignmentResponse.from_orm(a) for a in assignments]
        }
    
    async def update_assignment(self, assignment_id: int, assignment_data: AssignmentUpdate) -> Optional[AssignmentResponse]:
        db_assignment = await self.repository.update(assignment_id, assignment_data)
        if not db_assignment:
            return None
        return AssignmentResponse.from_orm(db_assignment)
    
    async def publish_assignment(self, assignment_id: int) -> Optional[AssignmentResponse]:
        db_assignment = await self.repository.publish(assignment_id)
        if not db_assignment:
            return None
        return AssignmentResponse.from_orm(db_assignment)
    
    async def close_assignment(self, assignment_id: int) -> Optional[AssignmentResponse]:
        db_assignment = await self.repository.close(assignment_id)
        if not db_assignment:
            return None
        return AssignmentResponse.from_orm(db_assignment)
