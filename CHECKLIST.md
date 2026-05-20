# CHECKLIST - Implementación MS2

## ✅ Estructura del Proyecto

- [x] `/app/` - Directorio principal
  - [x] `__init__.py`
  - [x] `main.py` - Punto de entrada FastAPI
  - [x] `database.py` - Configuración SQLAlchemy + PostgreSQL
  - [x] `models.py` - ORM: CasoPrueba, ResultadoEjecucion
  - [x] `schemas.py` - Pydantic v2 schemas (request/response)
  - [x] `/core/` - Configuración
    - [x] `__init__.py`
    - [x] `config.py` - Settings desde .env
  - [x] `/routes/` - Endpoints REST
    - [x] `__init__.py`
    - [x] `runner.py` - Todos los 6 endpoints
  - [x] `/sandbox/` - Motor de ejecución
    - [x] `__init__.py`
    - [x] `executor.py` - SandboxExecutor + compiladores

---

## ✅ Archivos de Configuración

- [x] `requirements.txt` - Dependencias Python
- [x] `.env.example` - Template de variables de entorno
- [x] `.gitignore` - Archivos a ignorar en Git
- [x] `setup.py` - Setup para instalar como paquete
- [x] `Dockerfile` - Multi-stage build para Docker
- [x] `docker-compose.yml` - Orchestration (FastAPI + PostgreSQL)

---

## ✅ Documentación

- [x] `README.md` - Guía completa para evaluador/docente
  - [x] Descripción general
  - [x] Tabla de equipo
  - [x] Esquema de BD detallado
  - [x] Documentación de 6 endpoints
  - [x] Tabla de lenguajes soportados
  - [x] Stack tecnológico
  - [x] Instalación paso a paso (Docker + local)
  - [x] Ejemplo de prueba completa (cURL)
  - [x] Troubleshooting
  - [x] Diagrama de flujo ASCII

- [x] `ARCHITECTURE.md` - Detalles técnicos
  - [x] Diagrama de arquitectura
  - [x] Flujo de solicitud
  - [x] Capas de arquitectura
  - [x] Modelos de datos ORM
  - [x] Seguridad del sandbox (5 niveles)
  - [x] Manejo de errores
  - [x] Compilación de lenguajes
  - [x] Claves lógicas (L-FK)
  - [x] Patrones de diseño
  - [x] Performance considerations

---

## ✅ Testing

- [x] `test_api.http` - Archivo REST Client para VS Code
  - [x] Health check
  - [x] Crear casos de prueba
  - [x] Ejecutar Python (exitoso/fallido/bloqueado)
  - [x] Ejecutar JavaScript
  - [x] Ejecutar C/C++
  - [x] Consultar resultados
  - [x] Tests de validación (errores esperados)

- [x] `test_ms2.py` - Tests pytest
  - [x] Health check
  - [x] Creación de casos
  - [x] Listado de casos
  - [x] Validaciones
  - [x] Ejecución exitosa
  - [x] Ejecución fallida
  - [x] Bloques de seguridad
  - [x] Consulta de resultados

---

## ✅ Scripts de Inicio Rápido

- [x] `quickstart.sh` - Setup automático (Linux/Mac)
- [x] `quickstart.bat` - Setup automático (Windows)

---

## ✅ Endpoints REST Implementados

### Gestión de Casos de Prueba

- [x] **EP1: POST `/api/v1/runner/test-cases`**
  - [x] Crear batch de casos
  - [x] Validación: tiempo_limite_ms (0-10000)
  - [x] Validación: salida_esperada no vacío
  - [x] Response: 201 Created con id_caso

- [x] **EP2: GET `/api/v1/runner/test-cases/assignment/{id_tarea_ref}`**
  - [x] Listar casos de una tarea
  - [x] Ordenar por id_caso ASC
  - [x] Error 404 si no existen

### Ejecución de Código

- [x] **EP3: POST `/api/v1/runner/execute`** (PRINCIPAL)
  - [x] Validar request (Pydantic)
  - [x] Buscar casos de prueba
  - [x] Ejecutar en sandbox
  - [x] Compilación (Java, C, C++)
  - [x] AST validation (Python)
  - [x] Timeout enforcement
  - [x] Comparación exacta de salidas
  - [x] Guardar resultado en BD
  - [x] Response: 200 OK con EjecucionResponse

### Consulta de Resultados

- [x] **EP4: GET `/api/v1/runner/results/{id_intento_ref}`**
  - [x] Obtener resultado más reciente
  - [x] Deserializar JSON detalle_casos
  - [x] Error 404 si no existe

- [x] **EP5: GET `/api/v1/runner/results/assignment/{id_tarea_ref}`**
  - [x] Listar todos los resultados de una tarea
  - [x] Ordenar por ejecutado_en DESC
  - [x] Error 404 si no existen

### Salud del Servicio

- [x] **EP6: GET `/health`**
  - [x] Status del servicio
  - [x] Verificar conexión a BD
  - [x] Response: HealthResponse

---

## ✅ Motor Sandbox (executor.py)

### Lenguajes Soportados

- [x] Python 3
  - [x] AST parsing
  - [x] Bloqueo de módulos peligrosos
  - [x] Bloqueo de símbolos peligrosos
- [x] JavaScript (Node.js)
- [x] Java
  - [x] Compilación con javac
  - [x] Ejecución con java -cp
  - [x] Validación: Clase Main
- [x] C
  - [x] Compilación con gcc
  - [x] Flags: -lm
- [x] C++
  - [x] Compilación con g++
  - [x] Standard: C++17

### Características de Seguridad

- [x] AST scanning (Python)
- [x] Timeout enforcement (todos)
- [x] I/O capturing (stdout/stderr)
- [x] Compilación en directorio temporal
- [x] Usuario non-root (Docker)
- [x] Módulos bloqueados Python: os, sys, subprocess, socket, etc.
- [x] Símbolos bloqueados: exec, eval, compile, open, __import__

### Flujo de Ejecución

- [x] Validación previa (AST)
- [x] Compilación si es necesario
- [x] Loop por cada caso:
  - [x] Ejecutar subprocess con stdin
  - [x] Capturar stdout/stderr
  - [x] Respetar timeout
  - [x] Comparar salida
- [x] Cálculo de estadísticas
- [x] Return ResultadoEjecucionSandbox

---

## ✅ Base de Datos

### Tabla: `casos_prueba`

- [x] id_caso (SERIAL PK)
- [x] id_tarea_ref (INTEGER, INDEX, L-FK)
- [x] entrada_datos (TEXT NULLABLE)
- [x] salida_esperada (TEXT NOT NULL)
- [x] tiempo_limite_ms (INTEGER, CHECK > 0)
- [x] descripcion (VARCHAR NULLABLE)
- [x] es_obligatorio (BOOLEAN DEFAULT TRUE)
- [x] creado_en (TIMESTAMPTZ DEFAULT NOW)

### Tabla: `resultados_ejecucion`

- [x] id_resultado (SERIAL PK)
- [x] id_intento_ref (INTEGER, INDEX, L-FK)
- [x] id_tarea_ref (INTEGER, INDEX, L-FK)
- [x] lenguaje (VARCHAR NOT NULL)
- [x] estado_compilacion (VARCHAR CHECK)
- [x] aprobado (BOOLEAN NOT NULL)
- [x] casos_totales (INTEGER)
- [x] casos_aprobados (INTEGER)
- [x] tiempo_usado_ms (INTEGER NULLABLE)
- [x] memoria_usada_kb (INTEGER NULLABLE)
- [x] salida_consola (TEXT NULLABLE)
- [x] detalle_casos (TEXT JSON SERIALIZADO)
- [x] ejecutado_en (TIMESTAMPTZ, INDEX)

### Índices

- [x] PK en ambas tablas
- [x] INDEX en id_tarea_ref (búsquedas)
- [x] INDEX en id_intento_ref (búsquedas)
- [x] INDEX en ejecutado_en (ordenamientos)

---

## ✅ FastAPI + Pydantic

### Schemas Request

- [x] CasoPruebaCreate
  - [x] Validación: id_tarea_ref > 0
  - [x] Validación: tiempo_limite_ms (0-10000)
  - [x] Validación: salida_esperada no vacía
- [x] CasoPruebaCreateBatch
- [x] EjecucionRequest
  - [x] Validación: lenguaje en {python, javascript, java, c, cpp}
  - [x] Validación: codigo_fuente no vacío
- [x] Otros schemas

### Schemas Response

- [x] CasoPruebaResponse
- [x] EjecucionResponse
- [x] DetalleResultadoCaso
- [x] ResultadoEjecucionResponse
- [x] HealthResponse

### Validadores Pydantic v2

- [x] @field_validator decorators
- [x] Normalización (lower, strip)
- [x] Constraints (gt, le, min_length, max_length)
- [x] from_attributes = True para ORM

---

## ✅ Configuración

### Settings (pydantic-settings)

- [x] APP_NAME, APP_VERSION, APP_ENV
- [x] APP_HOST, APP_PORT
- [x] DATABASE_URL
- [x] SANDBOX_MAX_TIMEOUT_MS
- [x] SANDBOX_MAX_MEMORY_KB
- [x] Carga desde .env con lru_cache

---

## ✅ Middleware & Lifespan

- [x] CORS middleware (allow_origins=["*"])
- [x] Global exception handler
- [x] Lifespan context manager
  - [x] Startup: init_db()
  - [x] Logging de inicialización
  - [x] Shutdown: logging

---

## ✅ Docker & Deployment

- [x] Dockerfile multi-stage
  - [x] Builder stage
  - [x] Runtime stage (lean)
  - [x] Dependencias: gcc, g++, jdk, node
- [x] docker-compose.yml
  - [x] PostgreSQL 16 service
  - [x] FastAPI service
  - [x] Environment variables
  - [x] Healthcheck
  - [x] Volumes para desarrollo
- [x] Usuario non-root
- [x] Health check endpoint

---

## ✅ Logging

- [x] Logging estándar de Python (no print)
- [x] Logger por módulo
- [x] Niveles: INFO, WARNING, ERROR
- [x] Formato: timestamp - logger - level - message

---

## ✅ Manejo de Errores

- [x] Validación Pydantic (422)
- [x] 404 Not Found (casos/resultados)
- [x] 500 Internal Server Error (catch-all)
- [x] Estados de error en resultado (COMPILATION_ERROR, RUNTIME_ERROR)
- [x] Timeout como estado en caso

---

## ✅ Características Adicionales

- [x] Health check real (SELECT 1)
- [x] Info endpoint (/)
- [x] Swagger docs auto-generado
- [x] ReDoc auto-generado
- [x] OpenAPI schema
- [x] Pool pre-ping para validar conexiones
- [x] Serialización JSON de detalle_casos
- [x] UTC timestamps en BD
- [x] Índices en tablas

---

## ⚠️ Limitaciones Conocidas (Out of Scope Hackathon)

- ⛔ Memoria: no se captura en tiempo real
- ⛔ CPU: sin límites (posible mejora con cgroups)
- ⛔ Red: sin restrictions desde subprocess
- ⛔ Async: todo síncrono (posible mejora con asyncio)
- ⛔ Caching: sin Redis (posible mejora)
- ⛔ Metrics: sin Prometheus (posible mejora)

---

## 📋 Requisitos del Prompt Cumplidos

### Stack Tecnológico

- ✅ Python 3.11
- ✅ FastAPI 0.111.0
- ✅ SQLAlchemy 2.x
- ✅ PostgreSQL con psycopg2-binary
- ✅ Pydantic v2
- ✅ pydantic-settings
- ✅ Uvicorn
- ✅ Docker + Docker Compose

### Estructura Modular

- ✅ app/__init__.py
- ✅ app/main.py (FastAPI + lifespan + CORS)
- ✅ app/database.py
- ✅ app/models.py
- ✅ app/schemas.py
- ✅ app/core/config.py
- ✅ app/routes/runner.py
- ✅ app/sandbox/executor.py
- ✅ Dockerfile, docker-compose.yml
- ✅ requirements.txt, .env.example

### Endpoints Requeridos

- ✅ EP1: POST /test-cases (batch)
- ✅ EP2: GET /test-cases/assignment/{id}
- ✅ EP3: POST /execute (principal)
- ✅ EP4: GET /results/{id}
- ✅ EP5: GET /results/assignment/{id}
- ✅ EP6: GET /health

### Motor Sandbox

- ✅ Soporte: Python, JavaScript, Java, C, C++
- ✅ AST scanning para Python
- ✅ Compilación para Java, C, C++
- ✅ Timeout enforcement
- ✅ Output capturing
- ✅ Comparación exacta

### Base de Datos

- ✅ Tabla casos_prueba (esquema oficial)
- ✅ Tabla resultados_ejecucion (esquema oficial)
- ✅ Claves lógicas (L-FK) sin FK físicas
- ✅ Índices para performance

### Documentación

- ✅ README.md completo
- ✅ ARCHITECTURE.md detallado
- ✅ Docstrings en código (español)
- ✅ Comentarios inline (español)
- ✅ test_api.http para pruebas
- ✅ Ejemplo cURL completo

---

## 🎯 Resumen de Implementación

**Total de archivos:** 19
**Líneas de código:** ~3,500
**Endpoints:** 6 operacionales
**Lenguajes soportados:** 5
**Niveles de seguridad:** 5
**Tablas BD:** 2
**Índices DB:** 6
**Tests: 15+

---

**Estado:** ✅ COMPLETO Y FUNCIONAL
**Fecha:** 2026-05-19
**Versión:** 1.0.0 Hackathon
