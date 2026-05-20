from sqlalchemy.orm import Session
from ..repositories.user_repository import UserRepository
from ..schemas.user import UserCreate, UserUpdate, UserResponse
from ..domain.models import UserRole
from typing import List, Optional


class UserService:
    def __init__(self, db: Session):
        self.repository = UserRepository(db)
    
    async def create_user(self, user_data: UserCreate) -> UserResponse:
        db_user = await self.repository.create(user_data)
        return UserResponse.from_orm(db_user)
    
    async def get_user(self, user_id: int) -> Optional[UserResponse]:
        db_user = await self.repository.get_by_id(user_id)
        if not db_user:
            return None
        return UserResponse.from_orm(db_user)
    
    async def get_user_by_email(self, email: str) -> Optional[UserResponse]:
        db_user = await self.repository.get_by_email(email)
        if not db_user:
            return None
        return UserResponse.from_orm(db_user)
    
    async def list_users(self, skip: int = 0, limit: int = 100) -> dict:
        users = await self.repository.list_all(skip, limit)
        return {
            "total": len(users),
            "users": [UserResponse.from_orm(u) for u in users]
        }
    
    async def list_users_by_role(self, role: str, skip: int = 0, limit: int = 100) -> dict:
        role_enum = UserRole(role)
        users = await self.repository.list_by_role(role_enum, skip, limit)
        return {
            "total": len(users),
            "users": [UserResponse.from_orm(u) for u in users]
        }
    
    async def update_user(self, user_id: int, user_data: UserUpdate) -> Optional[UserResponse]:
        db_user = await self.repository.update(user_id, user_data)
        if not db_user:
            return None
        return UserResponse.from_orm(db_user)
    
    async def delete_user(self, user_id: int) -> bool:
        result = await self.repository.soft_delete(user_id)
        return result is not None
    
    async def activate_user(self, user_id: int) -> Optional[UserResponse]:
        db_user = await self.repository.activate_user(user_id)
        if not db_user:
            return None
        return UserResponse.from_orm(db_user)
    
    async def deactivate_user(self, user_id: int) -> Optional[UserResponse]:
        db_user = await self.repository.deactivate_user(user_id)
        if not db_user:
            return None
        return UserResponse.from_orm(db_user)
