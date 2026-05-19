# PROMPT PARA GITHUB COPILOT — MS2: Motor de Ejecución y Evaluación
# repo-ms-code-runner | Frog Software Ltda. | Hackathon 19/05/2026
# ─────────────────────────────────────────────────────────────────
# USO: Pega esto en Copilot Chat (modo Workspace o Agent) con el
#      repositorio vacío abierto, o úsalo como comentario inicial
#      en un archivo main.py en blanco.
# ─────────────────────────────────────────────────────────────────

Actúa como un Arquitecto de Software Senior especializado en Python y FastAPI.
Construye el código fuente completo y funcional del repositorio "repo-ms-code-runner"
(Microservicio 2: Motor de Ejecución y Evaluación) para el sistema de calificación
automática de tareas de programación de Frog Software Ltda.

────────────────────────────────────────────────────────────────────────────────
## STACK TECNOLÓGICO (NO NEGOCIABLE)
────────────────────────────────────────────────────────────────────────────────

- Lenguaje    : Python 3.11
- Framework   : FastAPI (última versión estable)
- ORM         : SQLAlchemy 2.x (estilo declarativo con DeclarativeBase)
- BD          : PostgreSQL (conectar con psycopg2-binary)
- Validación  : Pydantic v2 (BaseModel, field_validator)
- Config      : pydantic-settings (lee desde archivo .env)
- Servidor    : Uvicorn
- Contenedor  : Docker + Docker Compose


────────────────────────────────────────────────────────────────────────────────
## ESTRUCTURA DE ARCHIVOS REQUERIDA (modular, lista para GitHub)
────────────────────────────────────────────────────────────────────────────────

repo-ms-code-runner/
├── app/
│   ├── __init__.py
│   ├── main.py               ← Instancia FastAPI, lifespan, CORS, routers
│   ├── database.py           ← Engine, SessionLocal, Base, get_db(), init_db()
│   ├── models.py             ← Modelos ORM SQLAlchemy
│   ├── schemas.py            ← Schemas Pydantic (request/response)
│   ├── core/
│   │   ├── __init__.py
│   │   └── config.py         ← Settings con pydantic-settings
│   ├── routes/
│   │   ├── __init__.py
│   │   └── runner.py         ← Todos los endpoints REST
│   └── sandbox/
│       ├── __init__.py
│       └── executor.py       ← Motor de ejecución con subprocess
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md


────────────────────────────────────────────────────────────────────────────────
## BASE DE DATOS PostgreSQL: DB_Code_Runner
## ESQUEMA OFICIAL DEL PROYECTO (respetar al pie de la letra)
────────────────────────────────────────────────────────────────────────────────

### TABLA: casos_prueba
Implementar con SQLAlchemy exactamente con estas columnas
(los nombres deben coincidir con el esquema del proyecto para que
la L-FK id_tarea_ref sea consistente con el MS1):

  id_caso          SERIAL       PRIMARY KEY
  id_tarea_ref     INTEGER      NOT NULL, INDEX   -- L-FK lógica al MS1 (sin FK física)
  entrada_datos    TEXT         NULLABLE           -- stdin para el código del alumno
  salida_esperada  TEXT         NOT NULL           -- stdout esperado exacto
  tiempo_limite_ms INTEGER      NOT NULL DEFAULT 3000  -- ms, CHECK > 0

Columnas ADICIONALES permitidas para mejorar funcionalidad (no rompen el esquema):
  descripcion      VARCHAR(255) NULLABLE           -- nombre descriptivo del caso
  es_obligatorio   BOOLEAN      NOT NULL DEFAULT TRUE  -- si falla, reprueba el intento
  creado_en        TIMESTAMPTZ  NOT NULL DEFAULT now()

### TABLA: resultados_ejecucion
Implementar con SQLAlchemy exactamente con estas columnas del esquema oficial:

  id_resultado        SERIAL       PRIMARY KEY
  id_intento_ref      INTEGER      NOT NULL, INDEX  -- L-FK lógica al MS1 (sin FK física)
  estado_compilacion  VARCHAR(20)  NOT NULL
      CHECK estado_compilacion IN ('SUCCESS','COMPILATION_ERROR','RUNTIME_ERROR')
  tiempo_usado_ms     INTEGER      NULLABLE
  memoria_usada_kb    INTEGER      NULLABLE
  salida_consola      TEXT         NULLABLE
  aprobado            BOOLEAN      NOT NULL DEFAULT FALSE

Columnas ADICIONALES permitidas (extienden sin romper el contrato):
  id_tarea_ref     INTEGER      NOT NULL, INDEX   -- para consultas por tarea
  lenguaje         VARCHAR(30)  NOT NULL           -- 'python','java','javascript','c','cpp'
  detalle_casos    TEXT         NULLABLE           -- JSON serializado, resultado por caso
  casos_totales    INTEGER      NULLABLE DEFAULT 0
  casos_aprobados  INTEGER      NULLABLE DEFAULT 0
  ejecutado_en     TIMESTAMPTZ  NOT NULL DEFAULT now()  -- inmutable, para auditoría

### IMPORTANTE — CLAVES LÓGICAS (L-FK):
NO crear Foreign Keys físicas hacia ninguna tabla de otro microservicio.
id_tarea_ref e id_intento_ref son INTEGER simples con INDEX, no FK.
Esto garantiza el desacoplamiento total entre microservicios.


────────────────────────────────────────────────────────────────────────────────
## ENDPOINTS REST (FastAPI) — DOCUMENTAR EN SWAGGER AUTOMÁTICAMENTE
────────────────────────────────────────────────────────────────────────────────

Prefijo base: /api/v1/runner
Tags Swagger: ["Runner - Motor de Ejecución"]

### EP1 — POST /api/v1/runner/test-cases
- Propósito : El Profesor (vía API Gateway) registra los casos de prueba de una tarea.
- Request   : Body JSON con lista de casos bajo la clave "casos" (batch).
              Cada caso: { id_tarea_ref, entrada_datos, salida_esperada,
                           tiempo_limite_ms, descripcion?, es_obligatorio? }
- Response  : 201 Created — Lista de CasoPruebaResponse con id_caso generado.
- Validar   : tiempo_limite_ms > 0 y <= 10000. salida_esperada no vacío.

### EP2 — GET /api/v1/runner/test-cases/assignment/{id_tarea_ref}
- Propósito : Recuperar todos los casos de prueba de una tarea específica.
- Path param: id_tarea_ref: int (gt=0)
- Response  : 200 OK — Lista de CasoPruebaResponse ordenada por id_caso ASC.
- Error     : 404 si no existen casos para esa tarea.

### EP3 — POST /api/v1/runner/execute  ← ENDPOINT PRINCIPAL
- Propósito : Ejecutar el código de un estudiante en el sandbox y guardar el resultado.
- Request   : Body JSON:
              {
                "id_intento_ref": int,   // L-FK al Intento del MS1
                "id_tarea_ref"  : int,   // para buscar los casos de prueba
                "lenguaje"      : str,   // 'python' | 'javascript' | 'java' | 'c' | 'cpp'
                "codigo_fuente" : str    // código completo del estudiante como string
              }
- Lógica interna (IMPLEMENTAR en este orden):
    1. Buscar casos de prueba de id_tarea_ref en la BD local. Si no hay → 404.
    2. Ejecutar el código en un subproceso aislado (subprocess) por cada caso:
         - Pasar entrada_datos como stdin al proceso.
         - Capturar stdout y stderr.
         - Respetar tiempo_limite_ms como timeout (subprocess.run timeout).
         - Si timeout → marcar ese caso como fallido con estado TIMEOUT.
    3. Comparar stdout.strip() real vs salida_esperada.strip().
    4. Determinar aprobado=True solo si todos los casos con es_obligatorio=True pasaron.
    5. Guardar ResultadoEjecucion en la BD con todos los campos.
    6. Retornar EjecucionResponse completo sincrónicamente.
- Response  : 200 OK — EjecucionResponse (ver schema abajo).
- Errores   : 404 (sin casos), 422 (validación), 500 (error del sandbox).

### EP4 — GET /api/v1/runner/results/{id_intento_ref}
- Propósito : Consultar el resultado más reciente de un intento específico.
- Path param: id_intento_ref: int (gt=0)
- Response  : 200 OK — ResultadoEjecucionResponse con detalle_casos deserializado.
- Error     : 404 si no hay resultado para ese intento.

### EP5 — GET /api/v1/runner/results/assignment/{id_tarea_ref}
- Propósito : Listar todos los resultados de ejecución de una tarea (para el profesor).
- Path param: id_tarea_ref: int (gt=0)
- Response  : 200 OK — Lista de ResultadoEjecucionResponse ordenada por ejecutado_en DESC.
- Error     : 404 si no hay resultados.

### EP6 — GET /health  (tag: "Sistema")
- Response  : { status, servicio, version, entorno, base_de_datos }
              Verificar conexión real a PostgreSQL con SELECT 1.


────────────────────────────────────────────────────────────────────────────────
## MOTOR SANDBOX (app/sandbox/executor.py) — IMPLEMENTAR COMPLETO
────────────────────────────────────────────────────────────────────────────────

Clase: SandboxExecutor
  Método público: ejecutar(lenguaje, codigo_fuente, casos_prueba) → ResultadoEjecucionSandbox

Lenguajes soportados y sus comandos:
  python     → python3 {archivo.py}                    (interpretado)
  javascript → node {archivo.js}                       (interpretado)
  java       → javac {Main.java} && java -cp {dir} Main (compilado, clase debe ser Main)
  c          → gcc {archivo.c} -o {bin} -lm && {bin}   (compilado)
  cpp        → g++ {archivo.cpp} -o {bin} -std=c++17 && {bin} (compilado)

Flujo de ejecución:
  1. Para Python: analizar el AST con ast.parse() antes de ejecutar.
     Bloquear imports de: os, sys, subprocess, shutil, socket, ctypes,
     multiprocessing, threading, signal, importlib.
     Si detecta un módulo bloqueado → retornar COMPILATION_ERROR con mensaje explicativo.
  2. Escribir codigo_fuente en un archivo temporal (tempfile.TemporaryDirectory).
  3. Si el lenguaje requiere compilación, ejecutar compilador con subprocess.run(timeout=30).
     Si returncode != 0 → retornar COMPILATION_ERROR con el stderr del compilador.
  4. Para cada caso de prueba, ejecutar el binario/script con:
       subprocess.run(cmd, input=stdin, capture_output=True, text=True,
                      timeout=caso.tiempo_limite_ms/1000)
     Capturar TimeoutExpired → ese caso falla con error TIMEOUT.
  5. Comparar stdout.strip() == caso.salida_esperada.strip() → paso: bool
  6. Agregar ResultadoCaso por cada caso ejecutado.
  7. aprobado = all(c.paso for c in detalle_casos if c.es_obligatorio)

Dataclasses de retorno del sandbox:
  @dataclass ResultadoCaso:
    id_caso, descripcion, entrada_datos, salida_esperada,
    salida_obtenida, paso: bool, tiempo_ms, es_obligatorio, error

  @dataclass ResultadoEjecucionSandbox:
    estado_compilacion: str  # solo: SUCCESS | COMPILATION_ERROR | RUNTIME_ERROR
    aprobado: bool
    tiempo_usado_ms, memoria_usada_kb, salida_consola
    detalle_casos: list[ResultadoCaso]
    casos_totales: int, casos_aprobados: int


────────────────────────────────────────────────────────────────────────────────
## SCHEMAS PYDANTIC v2 (app/schemas.py)
────────────────────────────────────────────────────────────────────────────────

CasoPruebaCreate:
  id_tarea_ref: int (gt=0)
  entrada_datos: Optional[str]
  salida_esperada: str (min_length=1)
  tiempo_limite_ms: int = 3000 (gt=0, le=10000)
  descripcion: Optional[str] (max_length=255)
  es_obligatorio: bool = True

CasoPruebaCreateBatch:
  casos: list[CasoPruebaCreate] (min_length=1)

CasoPruebaResponse(CasoPruebaBase):
  id_caso: int
  creado_en: datetime
  model_config = {"from_attributes": True}

EjecucionRequest:
  id_intento_ref: int (gt=0)
  id_tarea_ref: int (gt=0)
  lenguaje: str  → @field_validator: lower() y validar contra set {'python','javascript','java','c','cpp'}
  codigo_fuente: str (min_length=1)  → @field_validator: strip() no vacío

DetalleResultadoCaso:
  id_caso, descripcion, entrada_datos, salida_esperada,
  salida_obtenida, paso: bool, tiempo_ms, es_obligatorio

EjecucionResponse:
  id_resultado, id_intento_ref, id_tarea_ref, lenguaje,
  estado_compilacion, aprobado, casos_totales, casos_aprobados,
  tiempo_usado_ms, memoria_usada_kb, salida_consola,
  detalle_casos: list[DetalleResultadoCaso], ejecutado_en
  model_config = {"from_attributes": True}

ResultadoEjecucionResponse: (igual a EjecucionResponse, detalle_casos opcional)

HealthResponse:
  status, servicio, version, entorno, base_de_datos


────────────────────────────────────────────────────────────────────────────────
## CONFIGURACIÓN (app/core/config.py)
────────────────────────────────────────────────────────────────────────────────

class Settings(BaseSettings):
  APP_NAME: str = "MS2 - Motor de Ejecución y Evaluación"
  APP_VERSION: str = "1.0.0"
  APP_ENV: str = "development"
  APP_HOST: str = "0.0.0.0"
  APP_PORT: int = 8000
  DATABASE_URL: str = "postgresql://runner_user:runner_pass@localhost:5432/db_code_runner"
  SANDBOX_MAX_TIMEOUT_MS: int = 10000
  SANDBOX_MAX_MEMORY_KB: int = 65536

  class Config:
    env_file = ".env"

Decorar get_settings() con @lru_cache()


────────────────────────────────────────────────────────────────────────────────
## DATABASE (app/database.py)
────────────────────────────────────────────────────────────────────────────────

- create_engine con pool_pre_ping=True, pool_size=10, max_overflow=20
- echo=True solo si APP_ENV == "development"
- Dependencia FastAPI: def get_db() → yield db → finally db.close()
- init_db(): importar models y llamar Base.metadata.create_all(bind=engine)


────────────────────────────────────────────────────────────────────────────────
## MAIN (app/main.py)
────────────────────────────────────────────────────────────────────────────────

- Usar @asynccontextmanager lifespan: llamar init_db() al startup, loggear info del servicio.
- Agregar CORSMiddleware con allow_origins=["*"] (para demo del hackathon).
- Registrar manejador global de excepciones con @app.exception_handler(Exception).
- Incluir router con app.include_router(router).
- Endpoints del sistema: GET / (info del servicio) y GET /health.
- FastAPI con: title, description, version, docs_url="/docs", redoc_url="/redoc".


────────────────────────────────────────────────────────────────────────────────
## DOCKERFILE (multi-stage, optimizado para producción)
────────────────────────────────────────────────────────────────────────────────

# Stage 1 — builder: instalar dependencias Python
FROM python:3.11-slim AS builder
  - apt-get install gcc libpq-dev
  - pip install --prefix=/install -r requirements.txt

# Stage 2 — runtime: imagen final lean
FROM python:3.11-slim AS runtime
  - apt-get install: gcc g++ default-jdk nodejs libpq-dev
    (NECESARIOS para que el sandbox pueda compilar Java, C, C++ y ejecutar JS)
  - COPY --from=builder /install /usr/local
  - Crear usuario no-root: groupadd runner / useradd runner
  - WORKDIR /app, COPY --chown=runner:runner . .
  - USER runner
  - ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1
  - EXPOSE 8000
  - HEALTHCHECK: python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"
  - CMD: uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 2


────────────────────────────────────────────────────────────────────────────────
## DOCKER-COMPOSE (entorno local de desarrollo)
────────────────────────────────────────────────────────────────────────────────

version: "3.9"
services:
  postgres:
    image: postgres:16-alpine
    environment: POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB para db_code_runner
    ports: "5432:5432"
    healthcheck: pg_isready

  ms-code-runner:
    build: .
    ports: "8000:8000"
    environment:
      DATABASE_URL: postgresql://runner_user:runner_pass@postgres:5432/db_code_runner
    depends_on: postgres (condition: service_healthy)
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload


────────────────────────────────────────────────────────────────────────────────
## requirements.txt
────────────────────────────────────────────────────────────────────────────────

fastapi==0.111.0
uvicorn[standard]==0.29.0
sqlalchemy==2.0.30
alembic==1.13.1
psycopg2-binary==2.9.9
python-dotenv==1.0.1
pydantic==2.7.1
pydantic-settings==2.2.1
httpx==0.27.0
pytest==8.2.0
pytest-asyncio==0.23.6


────────────────────────────────────────────────────────────────────────────────
## README.md — Guía de ejecución para el evaluador/docente
────────────────────────────────────────────────────────────────────────────────

Incluir secciones en español:
1. Descripción del microservicio y su rol en la arquitectura
2. Tabla del equipo de desarrollo
3. Esquema de la BD (tablas, columnas, L-FKs explicadas)
4. Tabla de endpoints REST con método, ruta y descripción
5. Requisitos previos (Python 3.11+, Docker 24+)
6. Paso a paso:
   a) git clone + cd
   b) cp .env.example .env y editar DATABASE_URL
   c) python -m venv .venv && source .venv/bin/activate
   d) pip install -r requirements.txt
   e) uvicorn app.main:app --reload --port 8000
   f) docker compose up --build
   g) Acceso a Swagger: http://localhost:8000/docs
7. Ejemplo de prueba curl completo (registrar casos + ejecutar código + consultar resultado)
8. Tabla de lenguajes soportados con su runtime
9. Sección de seguridad del sandbox (AST scan, timeout, usuario no-root)
10. Diagrama de arquitectura en ASCII mostrando el lugar del MS2


────────────────────────────────────────────────────────────────────────────────
## RESTRICCIONES Y REGLAS DE CALIDAD (Copilot DEBE respetar)
────────────────────────────────────────────────────────────────────────────────

✅ HACER:
  - Todo el código comentado en español (docstrings y comentarios inline).
  - Usar logging estándar de Python (no print()) para los logs del servidor.
  - Manejar excepciones específicas (subprocess.TimeoutExpired, FileNotFoundError, etc.).
  - Serializar detalle_casos como JSON string en la BD (json.dumps / json.loads).
  - Retornar siempre el schema de respuesta correcto, nunca el objeto ORM directamente.
  - Los timestamps deben ser UTC (datetime.now(timezone.utc)).
  - El endpoint /execute debe persistir el resultado ANTES de retornar la respuesta.

❌ NO HACER:
  - No crear FK físicas entre tablas de distintos microservicios.
  - No usar os.system() ni eval() para ejecutar el código de los estudiantes.
  - No bloquear el event loop de FastAPI con operaciones síncronas pesadas sin executor.
  - No hardcodear credenciales de BD en el código fuente (usar .env).
  - No usar print() para logging en producción.
  - No retornar el código fuente del estudiante en ninguna respuesta de la API.
  - No crear tablas adicionales fuera del esquema oficial del proyecto.


────────────────────────────────────────────────────────────────────────────────
## CONTEXTO DEL SISTEMA (para que Copilot entienda el ecosistema)
────────────────────────────────────────────────────────────────────────────────

Este microservicio es el MS2 de un sistema de 5 componentes:
  1. Frontend Angular (repo-frontend)
  2. API Gateway / Orquestador — único punto de entrada (repo-api-gateway-orquestador)
  3. MS1: Gestión de Tareas y Calificaciones (repo-ms-tasks-grading) — Core del negocio
  4. MS2: Motor de Ejecución y Evaluación (repo-ms-code-runner) ← ESTE REPOSITORIO
  5. MS3: Detección de Plagio y Antifraude (repo-ms-plagiarism-detector)

El MS2 es PURAMENTE OPERATIVO:
  - No sabe qué es un LMS ni un estudiante.
  - No accede a la BD del MS1 ni del MS3.
  - Recibe {codigo_fuente + id_intento_ref + id_tarea_ref + lenguaje} desde el Gateway.
  - Ejecuta el código en sandbox, evalúa, persiste y retorna el veredicto.
  - Usa id_tarea_ref e id_intento_ref SOLO como enteros de correlación (L-FK).

Compatibilidad de L-FKs con el MS1 (DB_Tasks_Grading):
  - id_tarea_ref en casos_prueba     → correlaciona con Tareas.id_tarea del MS1
  - id_intento_ref en resultados     → correlaciona con Intentos.id_intento del MS1
  - El MS1 consultará GET /results/{id_intento_ref} para obtener el veredicto
    y actualizar la nota en su propia BD.
