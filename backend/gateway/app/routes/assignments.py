from fastapi import APIRouter, Depends, HTTPException, Query
from ..config import settings
from ..middleware.auth import get_current_user
import httpx

router = APIRouter(prefix="/api/v1/assignments", tags=["assignments"])


@router.get("")
async def list_assignments(
    skip: int = Query(0),
    limit: int = Query(100),
    auth: dict = Depends(get_current_user)
):
    """Listar tareas"""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{settings.assignment_service_url}/api/v1/assignments",
            params={"skip": skip, "limit": limit},
            headers={"Authorization": f"Bearer {auth['token']}"}
        )
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.json())
        return response.json()


@router.get("/{assignment_id}")
async def get_assignment(assignment_id: int, auth: dict = Depends(get_current_user)):
    """Obtener tarea"""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{settings.assignment_service_url}/api/v1/assignments/{assignment_id}",
            headers={"Authorization": f"Bearer {auth['token']}"}
        )
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.json())
        return response.json()


@router.post("")
async def create_assignment(data: dict, auth: dict = Depends(get_current_user)):
    """Crear tarea (profesor)"""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{settings.assignment_service_url}/api/v1/assignments",
            json=data,
            headers={"Authorization": f"Bearer {auth['token']}"}
        )
        if response.status_code != 201:
            raise HTTPException(status_code=response.status_code, detail=response.json())
        return response.json()


@router.get("/course/{course_id}")
async def get_course_assignments(
    course_id: int,
    skip: int = Query(0),
    limit: int = Query(100),
    auth: dict = Depends(get_current_user)
):
    """Obtener tareas de un curso"""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{settings.assignment_service_url}/api/v1/assignments/course/{course_id}",
            params={"skip": skip, "limit": limit},
            headers={"Authorization": f"Bearer {auth['token']}"}
        )
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.json())
        return response.json()
