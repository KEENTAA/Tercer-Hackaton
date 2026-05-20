from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .controllers.audit_controller import router as audit_router
from .domain.models import Base
from sqlalchemy import create_engine
import logging

logging.basicConfig(level=settings.log_level)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Audit Service",
    description="Servicio de auditoría de eventos",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

engine = create_engine(settings.database_url)
Base.metadata.create_all(bind=engine)

app.include_router(audit_router)


@app.get("/health", tags=["health"])
async def health_check():
    return {"status": "healthy", "service": settings.service_name}


@app.get("/", tags=["info"])
async def root():
    return {"service": settings.service_name, "version": "1.0.0", "status": "running"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.service_host, port=settings.service_port)
