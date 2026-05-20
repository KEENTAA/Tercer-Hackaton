from sqlalchemy import event
from sqlalchemy.orm import attributes
from app.models.tareas import Intento
from app.models.auditoria import HistorialAuditoria

@event.listens_for(Intento, "after_insert")
def auditar_creacion_intento(mapper, connection, target):
    """Registra automáticamente cuando un estudiante sube un nuevo intento."""
    nuevo_valor = {
        "id_intento": target.id_intento,
        "id_tarea": target.id_tarea,
        "id_estudiante": target.id_estudiante,
        "estado": target.estado,
        "url_codigo_fuente": target.url_codigo_fuente
    }
    
    connection.execute(
        HistorialAuditoria.__table__.insert().values(
            id_intento=target.id_intento,
            accion="CREACION_INTENTO",
            valor_anterior=None,
            valor_nuevo=nuevo_valor,
            ejecutado_por=target.id_estudiante
        )
    )

@event.listens_for(Intento, "after_update")
def auditar_cambio_nota(mapper, connection, target):
    """Detecta si la nota o el estado mutaron y guarda el estado previo y nuevo."""
    state = attributes.instance_state(target)
    historial_nota = attributes.get_history(target, 'nota_total')
    historial_estado = attributes.get_history(target, 'estado')

    # Solo disparamos la auditoría si cambiaron estos datos clave
    if historial_nota.has_changes() or historial_estado.has_changes():
        nota_anterior = historial_nota.deleted[0] if historial_nota.deleted else None
        estado_anterior = historial_estado.deleted[0] if historial_estado.deleted else None
        
        valor_previo = {
            "nota_total": float(nota_anterior) if nota_anterior is not None else None,
            "estado": estado_anterior
        }
        
        valor_actual = {
            "nota_total": float(target.nota_total) if target.nota_total is not None else None,
            "estado": target.estado
        }

        connection.execute(
            HistorialAuditoria.__table__.insert().values(
                id_intento=target.id_intento,
                accion="MODIFICACION_NOTA",
                valor_anterior=valor_previo,
                valor_nuevo=valor_actual,
                ejecutado_por=None # Puede ser nulo si el callback del Code Runner lo actualiza
            )
        )