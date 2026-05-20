from pydantic import BaseModel, EmailStr, ConfigDict

class UsuarioBase(BaseModel):
    codigo_universitario: str
    nombre: str
    correo: EmailStr
    rol: str  # 'ESTUDIANTE', 'PROFESOR', 'ADMIN'

class UsuarioCreate(UsuarioBase):
    password: str

class UsuarioUpdate(BaseModel):
    nombre: str | None = None
    correo: EmailStr | None = None
    password: str | None = None

class UsuarioResponse(UsuarioBase):
    id_usuario: int

    model_config = ConfigDict(from_attributes=True)