"""
Modelos ORM de SQLAlchemy 2.x para las tablas de la base de datos db_code_runner.

Tablas:
  - casos_prueba: Almacena los casos de prueba de cada tarea
  - resultados_ejecucion: Almacena los resultados de cada ejecución de código
"""

import json
from datetime import datetime, timezone

from sqlalchemy import Boolean, Index, Integer, String, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from database import Base


class CasoPrueba(Base):
    """
    Modelo para la tabla 'casos_prueba'.

    Representa un caso de prueba de una tarea específica.
    Contiene entrada esperada, salida esperada y configuración del caso.
    """

    __tablename__ = "casos_prueba"

    # Columnas obligatorias del esquema oficial
    id_caso: Mapped[int] = mapped_column(primary_key=True, index=True)
    id_tarea_ref: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    entrada_datos: Mapped[str | None] = mapped_column(Text, nullable=True)
    salida_esperada: Mapped[str] = mapped_column(Text, nullable=False)
    tiempo_limite_ms: Mapped[int] = mapped_column(
        Integer, nullable=False, default=3000
    )

    # Columnas adicionales permitidas (extienden el esquema sin romper)
    descripcion: Mapped[str | None] = mapped_column(
        String(255), nullable=True
    )
    es_obligatorio: Mapped[bool] = mapped_column(Boolean, default=True)
    creado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    # Índices adicionales para mejorar queries
    __table_args__ = (
        Index("idx_casos_prueba_id_tarea_ref", "id_tarea_ref"),
        Index("idx_casos_prueba_es_obligatorio", "es_obligatorio"),
    )

    def __repr__(self) -> str:
        return (
            f"<CasoPrueba(id_caso={self.id_caso}, "
            f"id_tarea_ref={self.id_tarea_ref}, "
            f"descripcion={self.descripcion})>"
        )


class ResultadoEjecucion(Base):
    """
    Modelo para la tabla 'resultados_ejecucion'.

    Representa el resultado de la ejecución de un código de estudiante.
    Almacena el estado de compilación, si pasó todas las pruebas y detalles.
    """

    __tablename__ = "resultados_ejecucion"

    # Columnas obligatorias del esquema oficial
    id_resultado: Mapped[int] = mapped_column(primary_key=True, index=True)
    id_intento_ref: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    estado_compilacion: Mapped[str] = mapped_column(String(20), nullable=False)
    tiempo_usado_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    memoria_usada_kb: Mapped[int | None] = mapped_column(Integer, nullable=True)
    salida_consola: Mapped[str | None] = mapped_column(Text, nullable=True)
    aprobado: Mapped[bool] = mapped_column(Boolean, default=False)

    # Columnas adicionales permitidas (extienden el esquema sin romper)
    id_tarea_ref: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    lenguaje: Mapped[str] = mapped_column(String(30), nullable=False)
    detalle_casos: Mapped[str | None] = mapped_column(Text, nullable=True)
    casos_totales: Mapped[int] = mapped_column(Integer, default=0)
    casos_aprobados: Mapped[int] = mapped_column(Integer, default=0)
    ejecutado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        index=True,
    )

    # Índices adicionales
    __table_args__ = (
        Index("idx_resultados_id_intento_ref", "id_intento_ref"),
        Index("idx_resultados_id_tarea_ref", "id_tarea_ref"),
        Index("idx_resultados_ejecutado_en", "ejecutado_en"),
    )

    def __repr__(self) -> str:
        return (
            f"<ResultadoEjecucion(id_resultado={self.id_resultado}, "
            f"id_intento_ref={self.id_intento_ref}, "
            f"aprobado={self.aprobado})>"
        )

    def get_detalle_casos_dict(self) -> list:
        """
        Deserializa detalle_casos desde JSON string a diccionario.

        Returns:
            list: Lista de diccionarios con detalles de cada caso.
        """
        if self.detalle_casos:
            return json.loads(self.detalle_casos)
        return []

    def set_detalle_casos_dict(self, detalle: list) -> None:
        """
        Serializa detalle_casos desde diccionario a JSON string.

        Args:
            detalle: Lista de diccionarios con detalles de los casos.
        """
        self.detalle_casos = json.dumps(detalle, ensure_ascii=False, indent=2)
