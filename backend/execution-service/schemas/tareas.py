from pydantic import BaseModel, ConfigDict
from datetime import datetime
from decimal import Decimal
from typing import List

# --- CRITERIOS DE CALIFICACIÓN ---
class CriterioBase(BaseModel):
    descripcion: str
    ponderacion: Decimal

class CriterioCreate(CriterioBase):
    pass

class CriterioUpdate(BaseModel):
    descripcion: str | None = None
    ponderacion: Decimal | None = None

class CriterioResponse(CriterioBase):
    id_criterio: int
    id_tarea: int

    model_config = ConfigDict(from_attributes=True)

# --- TAREAS ---
class TareaBase(BaseModel):
    titulo: str
    descripcion: str
    fecha_limite: datetime

class TareaCreate(TareaBase):
    id_curso: int
    criterios: List[CriterioCreate]

class TareaUpdate(BaseModel):
    titulo: str | None = None
    descripcion: str | None = None
    fecha_limite: datetime | None = None

class TareaResponse(TareaBase):
    id_tarea: int
    id_curso: int
    criterios: List[CriterioResponse] = []

    model_config = ConfigDict(from_attributes=True)