from pydantic import BaseModel, ConfigDict
from datetime import datetime
from decimal import Decimal
from typing import List, Optional

# --- DETALLE DE CALIFICACIÓN POR CRITERIO ---
class CalificacionCriterioBase(BaseModel):
    id_criterio: int
    nota_obtenida: Decimal
    comentarios: Optional[str] = None

class CalificacionCriterioCreate(CalificacionCriterioBase):
    pass

class CalificacionCriterioResponse(CalificacionCriterioBase):
    model_config = ConfigDict(from_attributes=True)

# --- INTENTOS DE ENTREGA ---
class IntentoCreate(BaseModel):
    id_tarea: int
    url_codigo_fuente: str
    contenido_codigo: Optional[str] = None

class IntentoUpdateEstado(BaseModel):
    estado: str  # 'ENVIADO', 'PROCESANDO', 'CALIFICADO', 'RECHAZADO'
    nota_total: Optional[Decimal] = None
    calificaciones: Optional[List[CalificacionCriterioCreate]] = None
    contenido_codigo: Optional[str] = None

class IntentoResponse(BaseModel):
    id_intento: int
    id_tarea: int
    id_estudiante: int
    numero_intento: int
    fecha_envio: datetime
    url_codigo_fuente: str
    nota_total: Optional[Decimal] = None
    contenido_codigo: Optional[str]
    estado: str
    calificaciones_detalladas: List[CalificacionCriterioResponse] = []

    model_config = ConfigDict(from_attributes=True)