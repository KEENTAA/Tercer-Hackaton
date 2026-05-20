from pydantic import BaseModel, ConfigDict

class CursoBase(BaseModel):
    codigo_curso: str
    nombre: str
    gestion: str

class CursoCreate(CursoBase):
    pass

class CursoUpdate(BaseModel):
    nombre: str | None = None
    gestion: str | None = None

class CursoResponse(CursoBase):
    id_curso: int
    id_profesor: int

    model_config = ConfigDict(from_attributes=True)