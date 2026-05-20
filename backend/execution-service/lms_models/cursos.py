from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.session import Base

from sqlalchemy import Column, Integer, ForeignKey, DateTime
from sqlalchemy.sql import func
from app.db.session import Base
class Curso(Base):
    __tablename__ = "cursos"

    id_curso: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    codigo_curso: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    nombre: Mapped[str] = mapped_column(String(150), nullable=False)
    gestion: Mapped[str] = mapped_column(String(10), nullable=False)
    id_profesor: Mapped[int] = mapped_column(ForeignKey("usuarios.id_usuario"), nullable=False)

    # Relaciones
    profesor = relationship("Usuario", back_populates="cursos_dictados")
    tareas = relationship("Tarea", back_populates="curso", cascade="all, delete-orphan")

class Matricula(Base):
    __tablename__ = "matriculas"

    id_matricula = Column(Integer, primary_key=True, index=True)
    id_estudiante = Column(Integer, ForeignKey("usuarios.id_usuario", ondelete="CASCADE"), nullable=False)
    id_curso = Column(Integer, ForeignKey("cursos.id_curso", ondelete="CASCADE"), nullable=False)
    fecha_inscripcion = Column(DateTime, server_default=func.now(), nullable=False)