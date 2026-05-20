from sqlalchemy.orm import Session
from sqlalchemy import and_
from ..domain.models import User, UserRole
from ..schemas.user import UserCreate, UserUpdate
from datetime import datetime
from typing import Optional, List


class UserRepository:
    def __init__(self, db: Session):
        self.db = db
    
    async def create(self, user_data: UserCreate) -> User:
        db_user = User(
            email=user_data.email,
            full_name=user_data.full_name,
            role=user_data.role or UserRole.STUDENT,
            is_active=True
        )
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return db_user
    
    async def get_by_id(self, user_id: int) -> Optional[User]:
        return self.db.query(User).filter(
            and_(User.id == user_id, User.deleted_at.is_(None))
        ).first()
    
    async def get_by_email(self, email: str) -> Optional[User]:
        return self.db.query(User).filter(
            and_(User.email == email, User.deleted_at.is_(None))
        ).first()
    
    async def list_all(self, skip: int = 0, limit: int = 100) -> List[User]:
        return self.db.query(User).filter(
            User.deleted_at.is_(None)
        ).offset(skip).limit(limit).all()
    
    async def list_by_role(self, role: UserRole, skip: int = 0, limit: int = 100) -> List[User]:
        return self.db.query(User).filter(
            and_(User.role == role, User.deleted_at.is_(None))
        ).offset(skip).limit(limit).all()
    
    async def update(self, user_id: int, user_data: UserUpdate) -> Optional[User]:
        db_user = await self.get_by_id(user_id)
        if not db_user:
            return None
        
        update_data = user_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_user, field, value)
        
        db_user.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(db_user)
        return db_user
    
    async def soft_delete(self, user_id: int) -> Optional[User]:
        db_user = await self.get_by_id(user_id)
        if not db_user:
            return None
        
        db_user.deleted_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(db_user)
        return db_user
    
    async def activate_user(self, user_id: int) -> Optional[User]:
        db_user = await self.get_by_id(user_id)
        if not db_user:
            return None
        
        db_user.is_active = True
        db_user.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(db_user)
        return db_user
    
    async def deactivate_user(self, user_id: int) -> Optional[User]:
        db_user = await self.get_by_id(user_id)
        if not db_user:
            return None
        
        db_user.is_active = False
        db_user.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(db_user)
        return db_user
