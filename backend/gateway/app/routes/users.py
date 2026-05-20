from fastapi import APIRouter, Depends, HTTPException, Query
from ..config import settings
from ..middleware.auth import get_current_user
import httpx

router = APIRouter(prefix="/api/v1/users", tags=["users"])


@router.get("/{user_id}")
async def get_user(user_id: int, auth: dict = Depends(get_current_user)):
    """Obtener usuario - proxy a user-service"""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{settings.user_service_url}/api/v1/users/{user_id}",
            headers={"Authorization": f"Bearer {auth['token']}"}
        )
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.json())
        return response.json()


@router.get("")
async def list_users(
    skip: int = Query(0),
    limit: int = Query(100),
    auth: dict = Depends(get_current_user)
):
    """Listar usuarios"""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{settings.user_service_url}/api/v1/users",
            params={"skip": skip, "limit": limit},
            headers={"Authorization": f"Bearer {auth['token']}"}
        )
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.json())
        return response.json()


@router.put("/{user_id}")
async def update_user(user_id: int, data: dict, auth: dict = Depends(get_current_user)):
    """Actualizar usuario"""
    async with httpx.AsyncClient() as client:
        response = await client.put(
            f"{settings.user_service_url}/api/v1/users/{user_id}",
            json=data,
            headers={"Authorization": f"Bearer {auth['token']}"}
        )
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.json())
        return response.json()
