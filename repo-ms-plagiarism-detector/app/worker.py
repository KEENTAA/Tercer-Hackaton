import queue
import threading
from sqlalchemy.orm import Session
from .database import SessionLocal
from . import models, utils

# Cola interna para procesamiento asíncrono inmediato
task_queue = queue.Queue()

def process_plagiarism_task(data: dict):
    """
    Procesa el plagio calculando similitud real contra envíos previos.
    """
    db = SessionLocal()
    try:
        id_intento = data['id_intento']
        source_code = data['source_code']
        id_tarea = data['id_tarea_ref']
        id_estudiante = data['id_estudiante_ref']
        
        print(f"[*] Analizando similitud para intento: {id_intento}")
        
        # 1. Obtener envíos previos de LA MISMA TAREA (excluyendo al autor actual)
        anteriores = db.query(models.FirmaCodigo).filter(
            models.FirmaCodigo.id_tarea_ref == id_tarea,
            models.FirmaCodigo.id_estudiante_ref != id_estudiante
        ).all()

        max_similitud_interna = 0.0
        coincidencias_detectadas = []

        # 2. Comparar contra cada envío anterior (Fuzzy Matching)
        for ant in anteriores:
            sim = utils.calculate_fuzzy_similarity(source_code, ant.codigo_fuente or "")
            if sim > 10.0: # Umbral mínimo para registrar
                coincidencias_detectadas.append((ant.id_firma, sim))
                if sim > max_similitud_interna:
                    max_similitud_interna = sim

        # 3. Guardar firma del envío actual para futuras comparaciones
        hash_code = utils.generate_code_hash(source_code)
        nueva_firma = models.FirmaCodigo(
            id_intento_ref=id_intento,
            id_tarea_ref=id_tarea,
            id_estudiante_ref=id_estudiante,
            hash_codigo=hash_code,
            codigo_fuente=source_code
        )
        db.add(nueva_firma)
        db.commit()
        db.refresh(nueva_firma)

        # 4. TurnItIn (Plagio Externo Mock)
        tii = utils.mock_turnitin_check(source_code)

        # 5. Consolidar Reporte (El mayor entre interno y externo)
        porcentaje_final = max(max_similitud_interna, tii['similarity'])
        
        reporte = models.ReportePlagio(
            id_intento_ref=id_intento,
            porcentaje_similitud_total=porcentaje_final,
            id_externo_turnitin=tii['external_id'],
            estado_analisis='COMPLETADO'
        )
        db.add(reporte)
        db.commit()
        db.refresh(reporte)

        # 6. Registrar todas las coincidencias encontradas
        for firma_id, porcentaje in coincidencias_detectadas:
            match = models.CoincidenciaPlagio(
                id_reporte=reporte.id_reporte,
                id_firma_coincidente=firma_id,
                porcentaje_coincidencia=porcentaje
            )
            db.add(match)
        
        db.commit()
        print(f"[v] Plagio completado para {id_intento}. Similitud máxima: {porcentaje_final}%")
        
    except Exception as e:
        print(f"[!] Error en worker: {e}")
        db.rollback()
    finally:
        db.close()

def worker_loop():
    while True:
        data = task_queue.get()
        if data is None: break
        process_plagiarism_task(data)
        task_queue.task_done()

# Arrancar el hilo al importar el módulo
threading.Thread(target=worker_loop, daemon=True).start()

def add_to_queue(data: dict):
    task_queue.put(data)
