from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from . import models, schemas, database, worker

app = FastAPI(title="MS Plagio - Frog Software")

# Auto-creación de tablas al arrancar (Ideal para Hackathon)
models.Base.metadata.create_all(bind=database.engine)

@app.get("/")
def home():
    return {"status": "Microservicio de Plagio Activo", "asincronia": "Hilos internos"}

@app.post("/analizar")
def post_analizar(submission: schemas.SubmissionEvent):
    """
    Recibe la tarea y la manda a la cola asíncrona.
    """
    worker.add_to_queue(submission.dict())
    return {"message": "Análisis de plagio iniciado en segundo plano", "id_intento": submission.id_intento}

@app.get("/resultado/{id_intento_ref}", response_model=schemas.ReportePlagioResponse)
def get_resultado(id_intento_ref: int, db: Session = Depends(database.get_db)):
    res = db.query(models.ReportePlagio).filter(models.ReportePlagio.id_intento_ref == id_intento_ref).first()
    if not res:
        raise HTTPException(status_code=404, detail="Resultado no listo o ID inválido")
    return res
