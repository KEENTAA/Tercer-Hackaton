from pydantic import BaseModel, EmailStr

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    id_usuario: int | None = None
    rol: str | None = None

class LoginRequest(BaseModel):
    correo: EmailStr
    password: str