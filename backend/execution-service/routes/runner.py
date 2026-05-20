"""
Rutas REST para el motor de ejecución (MS2).

Endpoints:
  POST   /api/v1/runner/test-cases
  GET    /api/v1/runner/test-cases/assignment/{id_tarea_ref}
  POST   /api/v1/runner/execute
  GET    /api/v1/runner/results/{id_intento_ref}
  GET    /api/v1/runner/results/assignment/{id_tarea_ref}
"""

import json
import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import CasoPrueba, ResultadoEjecucion
from app.schemas import (
    CasoPruebaCreateBatch,
    CasoPruebaResponse,
    EjecucionRequest,
    EjecucionResponse,
    DetalleResultadoCaso,
    ResultadoEjecucionResponse,
)
from app.sandbox.executor import SandboxExecutor, ResultadoCaso
from app.core.config import get_settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/runner", tags=["Runner - Motor de Ejecución"])
settings = get_settings()
executor_sandbox = SandboxExecutor(max_timeout_ms=settings.SANDBOX_MAX_TIMEOUT_MS)


# ══════════════════════════════════════════════════════════════════
# EP1: POST /test-cases — Registrar casos de prueba
# ══════════════════════════════════════════════════════════════════


@router.post(
    "/test-cases",
    response_model=List[CasoPruebaResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Registrar casos de prueba para una tarea",
    description="El profesor registra los casos de prueba de una tarea. Acepta un batch de casos.",
)
def crear_casos_prueba_batch(
    batch: CasoPruebaCreateBatch,
    db: Session = Depends(get_db),
) -> List[CasoPruebaResponse]:
    """
    Registrar múltiples casos de prueba para una tarea.

    Args:
        batch: Batch con lista de casos a crear
        db: Sesión de base de datos

    Returns:
        Lista de CasoPruebaResponse con IDs asignados

    Raises:
        422: Validación fallida en Pydantic
    """
    casos_creados = []

    for caso_data in batch.casos:
        # Crear instancia ORM
        nuevo_caso = CasoPrueba(
            id_tarea_ref=caso_data.id_tarea_ref,
            entrada_datos=caso_data.entrada_datos,
            salida_esperada=caso_data.salida_esperada,
            tiempo_limite_ms=caso_data.tiempo_limite_ms,
            descripcion=caso_data.descripcion,
            es_obligatorio=caso_data.es_obligatorio,
        )
        db.add(nuevo_caso)
        db.flush()  # Para obtener el id_caso generado
        casos_creados.append(nuevo_caso)

    db.commit()
    logger.info(
        f"✓ {len(casos_creados)} caso(s) de prueba registrado(s) para "
        f"id_tarea_ref={batch.casos[0].id_tarea_ref}"
    )
    return casos_creados


# ══════════════════════════════════════════════════════════════════
# EP2: GET /test-cases/assignment/{id_tarea_ref} — Listar casos
# ══════════════════════════════════════════════════════════════════


@router.get(
    "/test-cases/assignment/{id_tarea_ref}",
    response_model=List[CasoPruebaResponse],
    summary="Obtener todos los casos de prueba de una tarea",
    description="Recuperar todos los casos de prueba registrados para una tarea específica.",
)
def obtener_casos_por_tarea(
    id_tarea_ref: int,
    db: Session = Depends(get_db),
) -> List[CasoPruebaResponse]:
    """
    Obtener todos los casos de prueba de una tarea.

    Args:
        id_tarea_ref: ID de la tarea
        db: Sesión de base de datos

    Returns:
        Lista de CasoPruebaResponse

    Raises:
        404: No hay casos para esa tarea
    """
    casos = (
        db.query(CasoPrueba)
        .filter(CasoPrueba.id_tarea_ref == id_tarea_ref)
        .order_by(CasoPrueba.id_caso.asc())
        .all()
    )

    if not casos:
        logger.warning(f"No hay casos de prueba para id_tarea_ref={id_tarea_ref}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No hay casos de prueba registrados para la tarea {id_tarea_ref}",
        )

    return casos


# ══════════════════════════════════════════════════════════════════
# EP3: POST /execute — EJECUTAR CÓDIGO (ENDPOINT PRINCIPAL)
# ══════════════════════════════════════════════════════════════════


@router.post(
    "/execute",
    response_model=EjecucionResponse,
    status_code=status.HTTP_200_OK,
    summary="Ejecutar código de estudiante en sandbox",
    description="Ejecuta el código del estudiante contra los casos de prueba de la tarea.",
)
def ejecutar_codigo(
    request: EjecucionRequest,
    db: Session = Depends(get_db),
) -> EjecucionResponse:
    """
    Ejecutar código de estudiante y evaluar contra casos de prueba.

    Lógica:
    1. Buscar casos de prueba de la tarea
    2. Ejecutar en sandbox por cada caso
    3. Comparar output
    4. Guardar resultado en BD
    5. Retornar EjecucionResponse

    Args:
        request: EjecucionRequest con código y parámetros
        db: Sesión de base de datos

    Returns:
        EjecucionResponse con resultados

    Raises:
        404: Sin casos de prueba para esa tarea
        422: Validación fallida
        500: Error en el sandbox
    """
    # 1. Buscar casos de prueba
    casos_db = (
        db.query(CasoPrueba)
        .filter(CasoPrueba.id_tarea_ref == request.id_tarea_ref)
        .all()
    )

    if not casos_db:
        logger.error(f"No hay casos para id_tarea_ref={request.id_tarea_ref}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No hay casos de prueba para la tarea {request.id_tarea_ref}",
        )

    # 2. Ejecutar en sandbox
    resultado_sandbox = executor_sandbox.ejecutar(
        lenguaje=request.lenguaje,
        codigo_fuente=request.codigo_fuente,
        casos_prueba=casos_db,
    )

    # 3. Convertir resultados del sandbox a schema
    detalle_casos_schema = [
        DetalleResultadoCaso(
            id_caso=rc.id_caso,
            descripcion=rc.descripcion,
            entrada_datos=rc.entrada_datos,
            salida_esperada=rc.salida_esperada,
            salida_obtenida=rc.salida_obtenida,
            paso=rc.paso,
            tiempo_ms=rc.tiempo_ms,
            es_obligatorio=rc.es_obligatorio,
            error=rc.error,
        )
        for rc in resultado_sandbox.detalle_casos
    ]

    # 4. Guardar resultado en BD
    resultado_nuevo = ResultadoEjecucion(
        id_intento_ref=request.id_intento_ref,
        id_tarea_ref=request.id_tarea_ref,
        lenguaje=request.lenguaje,
        estado_compilacion=resultado_sandbox.estado_compilacion,
        tiempo_usado_ms=resultado_sandbox.tiempo_usado_ms,
        memoria_usada_kb=resultado_sandbox.memoria_usada_kb,
        salida_consola=resultado_sandbox.salida_consola,
        aprobado=resultado_sandbox.aprobado,
        casos_totales=resultado_sandbox.casos_totales,
        casos_aprobados=resultado_sandbox.casos_aprobados,
    )

    # Serializar detalle_casos como JSON
    resultado_nuevo.set_detalle_casos_dict([asdict(rc) for rc in resultado_sandbox.detalle_casos])

    db.add(resultado_nuevo)
    db.commit()
    db.refresh(resultado_nuevo)

    logger.info(
        f"✓ Resultado registrado: id_intento_ref={request.id_intento_ref}, "
        f"aprobado={resultado_nuevo.aprobado}"
    )

    # 5. Retornar response
    return EjecucionResponse(
        id_resultado=resultado_nuevo.id_resultado,
        id_intento_ref=resultado_nuevo.id_intento_ref,
        id_tarea_ref=resultado_nuevo.id_tarea_ref,
        lenguaje=resultado_nuevo.lenguaje,
        estado_compilacion=resultado_nuevo.estado_compilacion,
        aprobado=resultado_nuevo.aprobado,
        casos_totales=resultado_nuevo.casos_totales,
        casos_aprobados=resultado_nuevo.casos_aprobados,
        tiempo_usado_ms=resultado_nuevo.tiempo_usado_ms,
        memoria_usada_kb=resultado_nuevo.memoria_usada_kb,
        salida_consola=resultado_nuevo.salida_consola,
        detalle_casos=detalle_casos_schema,
        ejecutado_en=resultado_nuevo.ejecutado_en,
    )


def asdict(obj):
    """Convertir ResultadoCaso a diccionario"""
    return {
        "id_caso": obj.id_caso,
        "descripcion": obj.descripcion,
        "entrada_datos": obj.entrada_datos,
        "salida_esperada": obj.salida_esperada,
        "salida_obtenida": obj.salida_obtenida,
        "paso": obj.paso,
        "tiempo_ms": obj.tiempo_ms,
        "es_obligatorio": obj.es_obligatorio,
        "error": obj.error,
    }


# ══════════════════════════════════════════════════════════════════
# EP4: GET /results/{id_intento_ref} — Consultar resultado
# ══════════════════════════════════════════════════════════════════


@router.get(
    "/results/{id_intento_ref}",
    response_model=ResultadoEjecucionResponse,
    summary="Obtener resultado de un intento",
    description="Consultar el resultado más reciente de un intento específico.",
)
def obtener_resultado_por_intento(
    id_intento_ref: int,
    db: Session = Depends(get_db),
) -> ResultadoEjecucionResponse:
    """
    Obtener el resultado más reciente de un intento.

    Args:
        id_intento_ref: ID del intento
        db: Sesión de base de datos

    Returns:
        ResultadoEjecucionResponse

    Raises:
        404: No hay resultado para ese intento
    """
    resultado = (
        db.query(ResultadoEjecucion)
        .filter(ResultadoEjecucion.id_intento_ref == id_intento_ref)
        .order_by(ResultadoEjecucion.ejecutado_en.desc())
        .first()
    )

    if not resultado:
        logger.warning(f"No hay resultados para id_intento_ref={id_intento_ref}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No hay resultados para el intento {id_intento_ref}",
        )

    # Deserializar detalle_casos
    detalle_casos_parsed = []
    if resultado.detalle_casos:
        detalle_dict = json.loads(resultado.detalle_casos)
        detalle_casos_parsed = [
            DetalleResultadoCaso(**caso) for caso in detalle_dict
        ]

    return ResultadoEjecucionResponse(
        id_resultado=resultado.id_resultado,
        id_intento_ref=resultado.id_intento_ref,
        id_tarea_ref=resultado.id_tarea_ref,
        lenguaje=resultado.lenguaje,
        estado_compilacion=resultado.estado_compilacion,
        aprobado=resultado.aprobado,
        casos_totales=resultado.casos_totales,
        casos_aprobados=resultado.casos_aprobados,
        tiempo_usado_ms=resultado.tiempo_usado_ms,
        memoria_usada_kb=resultado.memoria_usada_kb,
        salida_consola=resultado.salida_consola,
        detalle_casos=detalle_casos_parsed,
        ejecutado_en=resultado.ejecutado_en,
    )


# ══════════════════════════════════════════════════════════════════
# EP5: GET /results/assignment/{id_tarea_ref} — Listar resultados
# ══════════════════════════════════════════════════════════════════


@router.get(
    "/results/assignment/{id_tarea_ref}",
    response_model=List[ResultadoEjecucionResponse],
    summary="Listar resultados de una tarea",
    description="Obtener todos los resultados de ejecución de una tarea (para el profesor).",
)
def obtener_resultados_por_tarea(
    id_tarea_ref: int,
    db: Session = Depends(get_db),
) -> List[ResultadoEjecucionResponse]:
    """
    Listar todos los resultados de una tarea.

    Args:
        id_tarea_ref: ID de la tarea
        db: Sesión de base de datos

    Returns:
        Lista de ResultadoEjecucionResponse

    Raises:
        404: No hay resultados para esa tarea
    """
    resultados = (
        db.query(ResultadoEjecucion)
        .filter(ResultadoEjecucion.id_tarea_ref == id_tarea_ref)
        .order_by(ResultadoEjecucion.ejecutado_en.desc())
        .all()
    )

    if not resultados:
        logger.warning(f"No hay resultados para id_tarea_ref={id_tarea_ref}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No hay resultados para la tarea {id_tarea_ref}",
        )

    # Deserializar detalle_casos para cada resultado
    respuestas = []
    for resultado in resultados:
        detalle_casos_parsed = []
        if resultado.detalle_casos:
            detalle_dict = json.loads(resultado.detalle_casos)
            detalle_casos_parsed = [
                DetalleResultadoCaso(**caso) for caso in detalle_dict
            ]

        respuestas.append(
            ResultadoEjecucionResponse(
                id_resultado=resultado.id_resultado,
                id_intento_ref=resultado.id_intento_ref,
                id_tarea_ref=resultado.id_tarea_ref,
                lenguaje=resultado.lenguaje,
                estado_compilacion=resultado.estado_compilacion,
                aprobado=resultado.aprobado,
                casos_totales=resultado.casos_totales,
                casos_aprobados=resultado.casos_aprobados,
                tiempo_usado_ms=resultado.tiempo_usado_ms,
                memoria_usada_kb=resultado.memoria_usada_kb,
                salida_consola=resultado.salida_consola,
                detalle_casos=detalle_casos_parsed,
                ejecutado_en=resultado.ejecutado_en,
            )
        )

    return respuestas
