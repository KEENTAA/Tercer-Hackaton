from sqlalchemy import String, CheckConstraint, ForeignKey, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.session import Base
from datetime import datetime

class CursoEstudiante(Base):
    __tablename__ = "curso_estudiante"
    
    id_curso: Mapped[int] = mapped_column(
        ForeignKey("cursos.id_curso", ondelete="CASCADE"), 
        primary_key=True
    )
    id_estudiante: Mapped[int] = mapped_column(
        ForeignKey("usuarios.id_usuario", ondelete="CASCADE"), 
        primary_key=True
    )
    fecha_inscripcion: Mapped[datetime] = mapped_column(
        DateTime, 
        server_default=func.now()
    )

class Usuario(Base):
    __tablename__ = "usuarios"

    id_usuario: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    codigo_universitario: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    correo: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    rol: Mapped[str] = mapped_column(String(20), nullable=False)

    __table_args__ = (
        CheckConstraint(
            "rol IN ('ESTUDIANTE', 'PROFESOR', 'ADMIN')", 
            name="check_rol_valido"
        ),
    )

    # Relaciones del ciclo de vida
    cursos_dictados = relationship("Curso", back_populates="profesor")
    intentos = relationship("Intento", back_populates="estudiante")