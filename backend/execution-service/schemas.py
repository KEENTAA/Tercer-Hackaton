"""
Schemas Pydantic v2 para validación de requests y responses de los endpoints.
Todos los schemas son reutilizables y composables.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, field_validator, Field


# ══════════════════════════════════════════════════════════════════
# SCHEMAS PARA CASOS DE PRUEBA
# ══════════════════════════════════════════════════════════════════


class CasoPruebaBase(BaseModel):
    """Base con campos comunes de un caso de prueba"""

    entrada_datos: Optional[str] = None
    salida_esperada: str
    tiempo_limite_ms: int = Field(default=3000, gt=0, le=10000)
    descripcion: Optional[str] = Field(default=None, max_length=255)
    es_obligatorio: bool = True


class CasoPruebaCreate(CasoPruebaBase):
    """Schema para crear un caso de prueba individual"""

    id_tarea_ref: int = Field(gt=0)

    @field_validator("salida_esperada")
    @classmethod
    def salida_no_vacia(cls, v: str) -> str:
        """Validar que salida_esperada no esté vacía"""
        if not v or not v.strip():
            raise ValueError("salida_esperada no puede estar vacía")
        return v


class CasoPruebaCreateBatch(BaseModel):
    """Schema para crear múltiples casos de prueba en un batch"""

    casos: list[CasoPruebaCreate] = Field(min_length=1)


class CasoPruebaResponse(CasoPruebaBase):
    """Response con el caso de prueba creado (con id_caso)"""

    id_caso: int
    id_tarea_ref: int
    creado_en: datetime

    model_config = {"from_attributes": True}


# ══════════════════════════════════════════════════════════════════
# SCHEMAS PARA EJECUCIÓN
# ══════════════════════════════════════════════════════════════════


class EjecucionRequest(BaseModel):
    """Request para ejecutar código de un estudiante"""

    id_intento_ref: int = Field(gt=0)
    id_tarea_ref: int = Field(gt=0)
    lenguaje: str
    codigo_fuente: str

    @field_validator("lenguaje")
    @classmethod
    def validar_lenguaje(cls, v: str) -> str:
        """Validar que el lenguaje esté en la lista permitida"""
        lenguajes_permitidos = {"python", "javascript", "java", "c", "cpp"}
        v_lower = v.lower().strip()
        if v_lower not in lenguajes_permitidos:
            raise ValueError(
                f"Lenguaje no soportado. Permitidos: {', '.join(lenguajes_permitidos)}"
            )
        return v_lower

    @field_validator("codigo_fuente")
    @classmethod
    def validar_codigo(cls, v: str) -> str:
        """Validar que el código no esté vacío"""
        if not v or not v.strip():
            raise ValueError("codigo_fuente no puede estar vacío")
        return v.strip()


# ══════════════════════════════════════════════════════════════════
# SCHEMAS PARA RESULTADOS
# ══════════════════════════════════════════════════════════════════


class DetalleResultadoCaso(BaseModel):
    """Detalle del resultado de un caso de prueba individual"""

    id_caso: int
    descripcion: Optional[str]
    entrada_datos: Optional[str]
    salida_esperada: str
    salida_obtenida: str
    paso: bool
    tiempo_ms: Optional[int]
    es_obligatorio: bool
    error: Optional[str] = None


class EjecucionResponse(BaseModel):
    """Response completo tras ejecutar código"""

    id_resultado: int
    id_intento_ref: int
    id_tarea_ref: int
    lenguaje: str
    estado_compilacion: str
    aprobado: bool
    casos_totales: int
    casos_aprobados: int
    tiempo_usado_ms: Optional[int]
    memoria_usada_kb: Optional[int]
    salida_consola: Optional[str]
    detalle_casos: list[DetalleResultadoCaso]
    ejecutado_en: datetime

    model_config = {"from_attributes": True}


class ResultadoEjecucionResponse(BaseModel):
    """Response al consultar un resultado existente"""

    id_resultado: int
    id_intento_ref: int
    id_tarea_ref: int
    lenguaje: str
    estado_compilacion: str
    aprobado: bool
    casos_totales: int
    casos_aprobados: int
    tiempo_usado_ms: Optional[int]
    memoria_usada_kb: Optional[int]
    salida_consola: Optional[str]
    detalle_casos: Optional[list[DetalleResultadoCaso]] = None
    ejecutado_en: datetime

    model_config = {"from_attributes": True}


# ══════════════════════════════════════════════════════════════════
# SCHEMAS PARA SALUD DEL SERVICIO
# ══════════════════════════════════════════════════════════════════


class HealthDatabaseStatus(BaseModel):
    """Estado de la conexión a la base de datos"""

    conectado: bool
    motor: str
    version: Optional[str] = None


class HealthResponse(BaseModel):
    """Response del endpoint /health"""

    status: str
    servicio: str
    version: str
    entorno: str
    base_de_datos: HealthDatabaseStatus
