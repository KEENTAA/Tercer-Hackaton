from fastapi import APIRouter, Depends, HTTPException, Query
from ..config import settings
from ..middleware.auth import get_current_user
import httpx

router = APIRouter(prefix="/api/v1/submissions", tags=["submissions"])


@router.post("")
async def create_submission(data: dict, auth: dict = Depends(get_current_user)):
    """Crear envío"""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{settings.submission_service_url}/api/v1/submissions",
            json={**data, "student_id": auth["user_id"]},
            headers={"Authorization": f"Bearer {auth['token']}"}
        )
        if response.status_code != 201:
            raise HTTPException(status_code=response.status_code, detail=response.json())
        return response.json()


@router.get("/{submission_id}")
async def get_submission(submission_id: int, auth: dict = Depends(get_current_user)):
    """Obtener envío"""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{settings.submission_service_url}/api/v1/submissions/{submission_id}",
            headers={"Authorization": f"Bearer {auth['token']}"}
        )
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.json())
        return response.json()


@router.get("/assignment/{assignment_id}")
async def get_assignment_submissions(
    assignment_id: int,
    skip: int = Query(0),
    limit: int = Query(100),
    auth: dict = Depends(get_current_user)
):
    """Obtener envíos de una tarea"""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{settings.submission_service_url}/api/v1/submissions/assignment/{assignment_id}",
            params={"skip": skip, "limit": limit},
            headers={"Authorization": f"Bearer {auth['token']}"}
        )
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.json())
        return response.json()


@router.get("")
async def list_submissions(
    skip: int = Query(0),
    limit: int = Query(100),
    auth: dict = Depends(get_current_user)
):
    """Listar todos los envíos"""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{settings.submission_service_url}/api/v1/submissions",
            params={"skip": skip, "limit": limit},
            headers={"Authorization": f"Bearer {auth['token']}"}
        )
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.json())
        return response.json()
