# Submission Service - Main

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from ..config import settings
from ..controllers.submission_controller import router as submission_router
from ..domain.models import Base, Submission, SubmissionFile
from sqlalchemy import create_engine
import logging

logging.basicConfig(level=settings.log_level)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Submission Service",
    description="Servicio de gestión de envíos de código",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inicializar base de datos
engine = create_engine(settings.database_url)
Base.metadata.create_all(bind=engine)

app.include_router(submission_router)


@app.get("/health", tags=["health"])
async def health_check():
    """Health check"""
    return {"status": "healthy", "service": settings.service_name}


@app.get("/", tags=["info"])
async def root():
    """Root endpoint"""
    return {"service": settings.service_name, "version": "1.0.0", "status": "running"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.service_host, port=settings.service_port)
