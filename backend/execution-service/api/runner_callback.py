from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.crud import crud_attempt
from app.schemas.intentos import IntentoUpdateEstado, IntentoResponse
from app.core.security import RoleChecker
from app.models.usuarios import Usuario

router = APIRouter(prefix="/runner", tags=["Webhooks Code Runner"])

# Asumimos que el Runner o el Sistema automatizado usa una cuenta con rol 'ADMIN' o 'PROFESOR'
require_sistema = RoleChecker(["ADMIN", "PROFESOR"])

@router.put("/calificar/{id_intento}", response_model=IntentoResponse)
def recibir_calificacion_runner(
    id_intento: int,
    calificacion_data: IntentoUpdateEstado,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_sistema)
):
    """
    Endpoint tipo Webhook. Recibe el desglose de notas desde el evaluador externo 
    y actualiza el estado final. El trigger de SQLAlchemy generará automáticamente el log de auditoría.
    """
    # 1. Verificar existencia del intento
    intento_db = crud_attempt.get_intento_by_id(db, id_intento)
    if not intento_db:
        raise HTTPException(status_code=404, detail="El intento especificado no existe.")

    # 2. Registrar la calificación mediante la capa transaccional segura
    intento_actualizado = crud_attempt.registrar_calificacion_intento(
        db=db, 
        id_intento=id_intento, 
        calificacion_in=calificacion_data
    )
    
    if not intento_actualizado:
        raise HTTPException(status_code=500, detail="Fallo interno al registrar las calificaciones.")

    return intento_actualizado