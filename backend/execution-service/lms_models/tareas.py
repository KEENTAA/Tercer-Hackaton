from sqlalchemy import String, Text, DateTime, ForeignKey, Numeric, CheckConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.session import Base
from datetime import datetime
from decimal import Decimal

class Tarea(Base):
    __tablename__ = "tareas"

    id_tarea: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    id_curso: Mapped[int] = mapped_column(ForeignKey("cursos.id_curso"), nullable=False)
    titulo: Mapped[str] = mapped_column(String(150), nullable=False)
    descripcion: Mapped[str] = mapped_column(Text, nullable=False)
    fecha_limite: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    # Relaciones
    curso = relationship("Curso", back_populates="tareas")
    criterios = relationship("CriterioCalificacion", back_populates="tarea", cascade="all, delete-orphan")
    intentos = relationship("Intento", back_populates="tarea", cascade="all, delete-orphan")

class CriterioCalificacion(Base):
    __tablename__ = "criterios_calificacion"

    id_criterio: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    id_tarea: Mapped[int] = mapped_column(ForeignKey("tareas.id_tarea", ondelete="CASCADE"), nullable=False)
    descripcion: Mapped[str] = mapped_column(String(255), nullable=False)
    ponderacion: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)

    # Relaciones
    tarea = relationship("Tarea", back_populates="criterios")
    calificaciones_criterio = relationship("CalificacionPorCriterio", back_populates="criterio", cascade="all, delete-orphan")

class Intento(Base):
    __tablename__ = "intentos"

    id_intento: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    id_tarea: Mapped[int] = mapped_column(ForeignKey("tareas.id_tarea"), nullable=False)
    id_estudiante: Mapped[int] = mapped_column(ForeignKey("usuarios.id_usuario"), nullable=False)
    numero_intento: Mapped[int] = mapped_column(nullable=False)
    fecha_envio: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    url_codigo_fuente: Mapped[str] = mapped_column(String(255), nullable=False)
    nota_total: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=True)
    estado: Mapped[str] = mapped_column(String(20), default="ENVIADO")

    __table_args__ = (
        CheckConstraint(
            "estado IN ('ENVIADO', 'PROCESANDO', 'CALIFICADO', 'RECHAZADO')", 
            name="check_estado_valido"
        ),
    )

    # Relaciones
    tarea = relationship("Tarea", back_populates="intentos")
    estudiante = relationship("Usuario", back_populates="intentos")
    calificaciones_detalladas = relationship("CalificacionPorCriterio", back_populates="intento", cascade="all, delete-orphan")

class CalificacionPorCriterio(Base):
    __tablename__ = "calificaciones_por_criterio"

    id_intento: Mapped[int] = mapped_column(ForeignKey("intentos.id_intento", ondelete="CASCADE"), primary_key=True)
    id_criterio: Mapped[int] = mapped_column(ForeignKey("criterios_calificacion.id_criterio", ondelete="CASCADE"), primary_key=True)
    nota_obtenida: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    comentarios: Mapped[str] = mapped_column(Text, nullable=True)

    # Relaciones
    intento = relationship("Intento", back_populates="calificaciones_detalladas")
    criterio = relationship("CriterioCalificacion", back_populates="calificaciones_criterio")