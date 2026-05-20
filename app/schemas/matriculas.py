from pydantic import BaseModel
from datetime import datetime

class MatriculaCreate(BaseModel):
    id_curso: int

class MatriculaResponse(BaseModel):
    id_matricula: int
    id_estudiante: int
    id_curso: int
    fecha_inscripcion: datetime

    class Config:
        from_attributes = True