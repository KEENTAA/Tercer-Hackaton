from sqlalchemy.orm import Session
from sqlalchemy import and_
from ..domain.models import Assignment, AssignmentStatus, GradingCriteria
from ..schemas.assignment import AssignmentCreate, AssignmentUpdate
from datetime import datetime
from typing import Optional, List


class AssignmentRepository:
    def __init__(self, db: Session):
        self.db = db
    
    async def create(self, assignment_data: AssignmentCreate) -> Assignment:
        db_assignment = Assignment(
            course_id=assignment_data.course_id,
            title=assignment_data.title,
            description=assignment_data.description,
            type=assignment_data.type,
            due_date=assignment_data.due_date,
            max_score=assignment_data.max_score,
            allow_multiple_submissions=assignment_data.allow_multiple_submissions,
            allow_late_submission=assignment_data.allow_late_submission,
            instructions=assignment_data.instructions
        )
        self.db.add(db_assignment)
        self.db.commit()
        self.db.refresh(db_assignment)
        return db_assignment
    
    async def get_by_id(self, assignment_id: int) -> Optional[Assignment]:
        return self.db.query(Assignment).filter(Assignment.id == assignment_id).first()
    
    async def get_by_course(self, course_id: int, skip: int = 0, limit: int = 100) -> List[Assignment]:
        return self.db.query(Assignment).filter(
            Assignment.course_id == course_id
        ).offset(skip).limit(limit).all()
    
    async def list_all(self, skip: int = 0, limit: int = 100) -> List[Assignment]:
        return self.db.query(Assignment).offset(skip).limit(limit).all()
    
    async def update(self, assignment_id: int, assignment_data: AssignmentUpdate) -> Optional[Assignment]:
        db_assignment = await self.get_by_id(assignment_id)
        if not db_assignment:
            return None
        
        update_data = assignment_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_assignment, field, value)
        
        db_assignment.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(db_assignment)
        return db_assignment
    
    async def publish(self, assignment_id: int) -> Optional[Assignment]:
        db_assignment = await self.get_by_id(assignment_id)
        if not db_assignment:
            return None
        
        db_assignment.status = AssignmentStatus.PUBLISHED
        db_assignment.published_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(db_assignment)
        return db_assignment
    
    async def close(self, assignment_id: int) -> Optional[Assignment]:
        db_assignment = await self.get_by_id(assignment_id)
        if not db_assignment:
            return None
        
        db_assignment.status = AssignmentStatus.CLOSED
        db_assignment.closed_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(db_assignment)
        return db_assignment
