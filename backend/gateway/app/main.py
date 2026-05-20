from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter
from slowapi.util import get_remote_address
from .config import settings
from .routes import auth, users, assignments, submissions
import logging

logging.basicConfig(level=settings.log_level)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="API Gateway",
    description="Gateway centralizado para todos los microservicios",
    version="1.0.0"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate Limiting
if settings.rate_limit_enabled:
    limiter = Limiter(key_func=get_remote_address)


# Health check
@app.get("/health", tags=["health"])
async def health_check():
    return {
        "status": "healthy",
        "service": settings.service_name
    }


# Info
@app.get("/", tags=["info"])
async def root():
    return {
        "service": settings.service_name,
        "version": "1.0.0",
        "status": "running"
    }


# Include routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(assignments.router)
app.include_router(submissions.router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.service_host, port=settings.service_port)
