-- Script de creación para DB_Plagiarism_Detector

CREATE TABLE IF NOT EXISTS firmas_codigo (
    id_firma SERIAL PRIMARY KEY,
    id_intento_ref INT NOT NULL,
    id_tarea_ref INT NOT NULL,
    id_estudiante_ref VARCHAR(50) NOT NULL,
    hash_codigo VARCHAR(64) NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_hash_codigo ON firmas_codigo(hash_codigo);
CREATE INDEX IF NOT EXISTS idx_tarea_ref ON firmas_codigo(id_tarea_ref);

CREATE TABLE IF NOT EXISTS reportes_plagio (
    id_reporte SERIAL PRIMARY KEY,
    id_intento_ref INT NOT NULL,
    porcentaje_similitud_total DECIMAL(5,2) DEFAULT 0.00,
    id_externo_turnitin VARCHAR(100),
    estado_analisis VARCHAR(20) DEFAULT 'PENDIENTE',
    fecha_analisis TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS coincidencias_plagio (
    id_reporte INT REFERENCES reportes_plagio(id_reporte),
    id_firma_coincidente INT REFERENCES firmas_codigo(id_firma),
    porcentaje_coincidencia DECIMAL(5,2),
    PRIMARY KEY (id_reporte, id_firma_coincidente)
);
