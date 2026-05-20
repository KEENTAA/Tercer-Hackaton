from fastapi import APIRouter, Depends, HTTPException
from ..config import settings
from ..middleware.auth import get_current_user
import httpx

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@router.post("/login")
async def login(email: str, password: str):
    """Proxy para login - pasa al auth service"""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{settings.auth_service_url}/api/v1/auth/login",
            json={"email": email, "password": password}
        )
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.json())
        return response.json()


@router.post("/register")
async def register(email: str, password: str, full_name: str):
    """Proxy para registro - pasa al auth service"""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{settings.auth_service_url}/api/v1/auth/register",
            json={"email": email, "password": password, "full_name": full_name}
        )
        if response.status_code != 201:
            raise HTTPException(status_code=response.status_code, detail=response.json())
        return response.json()


@router.post("/refresh")
async def refresh_token(token: str):
    """Refresh JWT token"""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{settings.auth_service_url}/api/v1/auth/refresh",
            json={"token": token}
        )
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.json())
        return response.json()


@router.post("/logout")
async def logout(auth: dict = Depends(get_current_user)):
    """Logout (invalida token en cache si es necesario)"""
    return {"message": "Logged out successfully"}
