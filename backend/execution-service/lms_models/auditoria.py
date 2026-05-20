from sqlalchemy import String, DateTime, ForeignKey, func, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.session import Base
from datetime import datetime
from typing import Any

class HistorialAuditoria(Base):
    __tablename__ = "historial_auditoria"

    id_auditoria: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    id_intento: Mapped[int] = mapped_column(ForeignKey("intentos.id_intento"), nullable=False)
    accion: Mapped[str] = mapped_column(String(50), nullable=False) # 'CREACION_INTENTO', 'MODIFICACION_NOTA'
    valor_anterior: Mapped[Any] = mapped_column(JSON, nullable=True)
    valor_nuevo: Mapped[Any] = mapped_column(JSON, nullable=True)
    fecha_cambio: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    ejecutado_por: Mapped[int] = mapped_column(ForeignKey("usuarios.id_usuario"), nullable=True) # Nullable si automatiza el runner