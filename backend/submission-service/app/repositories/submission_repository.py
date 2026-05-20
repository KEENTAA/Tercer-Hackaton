# Submission Service - Repositorio

from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import Optional, List
from ..domain.models import Submission, SubmissionFile, SubmissionStatus
import uuid


class SubmissionRepository:
    """Repositorio para gestionar envíos"""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def create_submission(
        self,
        assignment_id: str,
        student_id: str,
        code_content: str,
        language: str,
        attempt_number: int = 1
    ) -> Submission:
        """Crear nuevo envío"""
        submission = Submission(
            id=str(uuid.uuid4()),
            assignment_id=assignment_id,
            student_id=student_id,
            code_content=code_content,
            language=language,
            attempt_number=attempt_number,
            status=SubmissionStatus.SUBMITTED,
            is_immutable=1  # Es inmutable desde el momento de creación
        )
        
        self.db.add(submission)
        self.db.commit()
        self.db.refresh(submission)
        return submission
    
    async def get_submission_by_id(self, submission_id: str) -> Optional[Submission]:
        """Obtener envío por ID"""
        return self.db.query(Submission).filter(Submission.id == submission_id).first()
    
    async def get_submission_history(
        self,
        assignment_id: str,
        student_id: str,
        limit: int = 100
    ) -> List[Submission]:
        """Obtener historial de envíos"""
        return self.db.query(Submission).filter(
            Submission.assignment_id == assignment_id,
            Submission.student_id == student_id
        ).order_by(desc(Submission.submitted_at)).limit(limit).all()
    
    async def update_submission_status(
        self,
        submission_id: str,
        status: SubmissionStatus
    ) -> Submission:
        """Actualizar estado del envío"""
        submission = await self.get_submission_by_id(submission_id)
        if submission:
            submission.status = status
            self.db.commit()
            self.db.refresh(submission)
        return submission
    
    async def add_submission_file(
        self,
        submission_id: str,
        filename: str,
        file_content: str,
        mime_type: str = "text/plain"
    ) -> SubmissionFile:
        """Agregar archivo a un envío"""
        file = SubmissionFile(
            id=str(uuid.uuid4()),
            submission_id=submission_id,
            filename=filename,
            file_content=file_content,
            file_size=len(file_content),
            mime_type=mime_type
        )
        
        self.db.add(file)
        self.db.commit()
        self.db.refresh(file)
        return file
    
    async def get_latest_submission(
        self,
        assignment_id: str,
        student_id: str
    ) -> Optional[Submission]:
        """Obtener último envío del estudiante para una tarea"""
        return self.db.query(Submission).filter(
            Submission.assignment_id == assignment_id,
            Submission.student_id == student_id
        ).order_by(desc(Submission.submitted_at)).first()
