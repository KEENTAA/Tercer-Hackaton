import queue
import threading
from sqlalchemy.orm import Session
from .database import SessionLocal
from . import models, utils

task_queue = queue.Queue()

def process_plagiarism_task(data: dict):
    db = SessionLocal()
    try:
        id_intento = data['id_intento']
        source_code = data['source_code']
        id_tarea = data['id_tarea_ref']
        id_estudiante = data['id_estudiante_ref']
        
        # 1. Similitud Interna (Fuzzy) contra LA MISMA TAREA
        anteriores = db.query(models.FirmaCodigo).filter(
            models.FirmaCodigo.id_tarea_ref == id_tarea,
            models.FirmaCodigo.id_estudiante_ref != id_estudiante
        ).all()

        max_sim_interna = 0.0
        for ant in anteriores:
            sim = utils.calculate_fuzzy_similarity(source_code, ant.codigo_fuente or "")
            if sim > max_sim_interna: max_sim_interna = sim

        # 2. Persistir firma para el futuro
        nueva_firma = models.FirmaCodigo(
            id_intento_ref=id_intento, id_tarea_ref=id_tarea,
            id_estudiante_ref=id_estudiante, hash_codigo=utils.generate_code_hash(source_code),
            codigo_fuente=source_code
        )
        db.add(nueva_firma); db.commit()

        # 3. CONEXIÓN API DOLOS (Validación Externa Profesional)
        dolos = utils.call_dolos_api(source_code, id_estudiante)

        # 4. REPORTE DE AUDITORÍA ESTATAL (MVP 4)
        porcentaje_final = max(max_sim_interna, dolos['similarity'])
        reporte = models.ReportePlagio(
            id_intento_ref=id_intento,
            porcentaje_similitud_total=porcentaje_final,
            proveedor_externo=dolos['provider'],
            url_evidencia_auditoria=dolos['url'],
            estado_transaccion='COMPLETED'
        )
        db.add(reporte); db.commit()
        print(f"[AUDIT] Intento {id_intento} registrado con {porcentaje_final}% similitud via {dolos['provider']}")
        
    except Exception as e:
        print(f"[!] Error Audit: {e}"); db.rollback()
    finally:
        db.close()

def worker_loop():
    while True:
        data = task_queue.get()
        if data is None: break
        process_plagiarism_task(data); task_queue.task_done()

threading.Thread(target=worker_loop, daemon=True).start()
def add_to_queue(data: dict): task_queue.put(data)
