# Main para Auth Service

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from ..config import settings
from ..controllers.auth_controller import router as auth_router
from ..domain.models import Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import logging

# Configurar logging
logging.basicConfig(level=settings.LOG_LEVEL)
logger = logging.getLogger(__name__)

# Crear aplicación FastAPI
app = FastAPI(
    title="Auth Service",
    description="Servicio de autenticación centralizado",
    version="1.0.0"
)

# Configurar CORS
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

# Incluir routers
app.include_router(auth_router)


@app.get("/health", tags=["health"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": settings.service_name
    }


@app.get("/", tags=["info"])
async def root():
    """Root endpoint"""
    return {
        "service": settings.service_name,
        "version": "1.0.0",
        "status": "running"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=settings.service_host,
        port=settings.service_port
    )
