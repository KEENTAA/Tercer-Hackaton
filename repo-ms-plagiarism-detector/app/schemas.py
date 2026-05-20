from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class ReportePlagioBase(BaseModel):
    id_intento_ref: int
    porcentaje_similitud_total: float
    estado_analisis: str

class ReportePlagioCreate(ReportePlagioBase):
    pass

class ReportePlagioResponse(ReportePlagioBase):
    id_reporte: int
    id_externo_turnitin: Optional[str]
    fecha_analisis: datetime

    class Config:
        from_attributes = True

class SubmissionEvent(BaseModel):
    id_intento: int
    id_tarea_ref: int
    id_estudiante_ref: str
    source_code: str
