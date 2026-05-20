from sqlalchemy import Column, Integer, String, DECIMAL, ForeignKey, TIMESTAMP, Text, func
from .database import Base

class FirmaCodigo(Base):
    __tablename__ = "firmas_codigo"
    id_firma = Column(Integer, primary_key=True, index=True)
    id_intento_ref = Column(Integer, nullable=False)
    id_tarea_ref = Column(Integer, nullable=False, index=True)
    id_estudiante_ref = Column(String(50), nullable=False)
    hash_codigo = Column(String(64), nullable=False, index=True)
    codigo_fuente = Column(Text, nullable=True)

class ReportePlagio(Base):
    __tablename__ = "reportes_plagio"
    id_reporte = Column(Integer, primary_key=True, index=True)
    id_intento_ref = Column(Integer, nullable=False)
    porcentaje_similitud_total = Column(DECIMAL(5, 2), default=0.00)
    
    # Campos para Auditoría Estatal (MVP 4)
    proveedor_externo = Column(String(100), default="Dolos Academic API")
    url_evidencia_auditoria = Column(String(255)) 
    estado_transaccion = Column(String(20), default="COMPLETED")
    
    fecha_analisis = Column(TIMESTAMP, server_default=func.now())

class CoincidenciaPlagio(Base):
    __tablename__ = "coincidencias_plagio"
    id_reporte = Column(Integer, ForeignKey("reportes_plagio.id_reporte"), primary_key=True)
    id_firma_coincidente = Column(Integer, ForeignKey("firmas_codigo.id_firma"), primary_key=True)
    porcentaje_coincidencia = Column(DECIMAL(5, 2))
