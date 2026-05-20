from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
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