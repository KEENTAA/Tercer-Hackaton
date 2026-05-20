from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from app.core.config import settings

# Crear el motor de conexión
engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)

# Crear la fábrica de sesiones independientes
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para que hereden nuestros futuros modelos del ORM
Base = declarative_base()

# Dependencia para los endpoints de FastAPI (Inyección de dependencias)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()