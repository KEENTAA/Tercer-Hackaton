# ARCHITECTURE.md - Arquitectura Detallada de MS2

## Descripción General de la Arquitectura

MS2 es un microservicio modular, desacoplado y escalable diseñado para ejecutar código de estudiantes en entorno sandbox.

```
┌─────────────────────────────────────────────────────────┐
│         FastAPI Application (app/main.py)               │
│  - Lifespan Management (startup/shutdown)               │
│  - CORS Middleware                                       │
│  - Global Exception Handler                             │
│  - Health Check & Info Endpoints                        │
└────┬────────────────────────────────────────────────────┘
     │
     ├─────────────────────────────────────────────────────────────┐
     │                                                             │
     ▼                          ▼                                  ▼
┌──────────────┐        ┌────────────────┐           ┌─────────────────────┐
│ Database     │        │ Routes (REST)  │           │ Sandbox Executor    │
│ (database.py)│        │ (routes/...)   │           │ (sandbox/executor.py│
│              │        │                │           │                     │
│ - SQLAlchemy │        │ EP1: POST      │           │ - Python AST        │
│ - PostgreSQL │        │     /test-cases│           │ - Subprocess        │
│ - Migrations │        │ EP2: GET       │           │ - Compilation       │
│              │        │     /test-case/│           │ - Timeout           │
│              │        │ EP3: POST      │           │ - Output Capture    │
│              │        │     /execute   │           │                     │
│              │        │ EP4: GET       │           │ Supported Languages:│
│              │        │     /results   │           │  - Python           │
│              │        │ EP5: GET       │           │  - JavaScript       │
│              │        │     /results/  │           │  - Java             │
│              │        │                │           │  - C                │
│              │        │ (+ health/info)│           │  - C++              │
└──────────────┘        └────────────────┘           └─────────────────────┘
     ▲                        ▲                               ▲
     │ Models                 │ Schemas                       │ Dataclasses
     │ (models.py)            │ (schemas.py)                  │ (executor.py)
     │                        │                               │
     └────────────────────────┴───────────────────────────────┘
                              │
                   ┌──────────▼──────────┐
                   │ Configuration       │
                   │ (core/config.py)    │
                   │                     │
                   │ Settings from .env  │
                   └─────────────────────┘
```

---

## Flujo de una Solicitud de Ejecución (EP3)

```
┌─────────────────────────────────────┐
│ Cliente (API Gateway / Frontend)    │
│ POST /api/v1/runner/execute         │
│ {                                   │
│   "id_intento_ref": 123,            │
│   "id_tarea_ref": 42,               │
│   "lenguaje": "python",             │
│   "codigo_fuente": "..."            │
│ }                                   │
└────────────┬────────────────────────┘
             │
             ▼
    ┌────────────────────────────────┐
    │ FastAPI Request Validation     │
    │ (Pydantic EjecucionRequest)    │
    │ - Lenguaje en lista permitida  │
    │ - Código no vacío              │
    │ - id_intento_ref > 0           │
    └────────┬───────────────────────┘
             │
             ▼
    ┌────────────────────────────────┐
    │ Obtener sesión de BD (get_db) │
    └────────┬───────────────────────┘
             │
             ▼
    ┌────────────────────────────────┐
    │ Query CasoPrueba               │
    │ WHERE id_tarea_ref = 42        │
    │ ORDER BY id_caso ASC           │
    │                                │
    │ ¿Existen?                      │
    │ NO → HTTP 404                  │
    │ SÍ → Continuar                 │
    └────────┬───────────────────────┘
             │
             ▼
    ┌────────────────────────────────────┐
    │ SandboxExecutor.ejecutar()         │
    │                                    │
    │ Para Python:                       │
    │   AST Validation                   │
    │   ├─ Detectar imports bloqueados   │
    │   ├─ Detectar símbolos bloqueados  │
    │   └─ Si error → COMPILATION_ERROR │
    │                                    │
    │ Para C/C++/Java:                   │
    │   Compilación                      │
    │   ├─ Escribir en temp dir          │
    │   ├─ Ejecutar compilador           │
    │   ├─ Si error → COMPILATION_ERROR │
    │   └─ Si ok → Obtener ejecutable   │
    │                                    │
    │ Para cada CasoPrueba:              │
    │   subprocess.run()                 │
    │   ├─ Pasar entrada_datos como stdin│
    │   ├─ Capturar stdout/stderr        │
    │   ├─ Respetar timeout              │
    │   ├─ Comparar outputs              │
    │   └─ Registrar resultado           │
    │                                    │
    │ Calcular:                          │
    │   - casos_totales                  │
    │   - casos_aprobados                │
    │   - aprobado = todos obligatorios  │
    │                                    │
    │ Return ResultadoEjecucionSandbox   │
    └────────┬───────────────────────────┘
             │
             ▼
    ┌────────────────────────────────────┐
    │ Crear ResultadoEjecucion ORM       │
    │ - Guardar en PostgreSQL            │
    │ - Serializar detalle_casos → JSON  │
    │ - Calcular aprobado                │
    └────────┬───────────────────────────┘
             │
             ▼
    ┌────────────────────────────────────┐
    │ Construir EjecucionResponse        │
    │ (con todos los detalles)           │
    └────────┬───────────────────────────┘
             │
             ▼
    ┌────────────────────────────────────┐
    │ HTTP 200 + JSON Response           │
    │ Retornar al cliente                │
    └────────────────────────────────────┘
```

---

## Capas de la Arquitectura

### 1. **Presentation Layer** (app/main.py, app/routes/runner.py)

Endpoints REST que reciben solicitudes del API Gateway.

- **Responsabilidades:**
  - Validación de entrada (Pydantic schemas)
  - Manejo de errores HTTP
  - Conversión ORM ↔ Response schemas
  - Logging de eventos

- **Comunicación:**
  - ✅ Recibe: EjecucionRequest (JSON)
  - ✅ Retorna: EjecucionResponse (JSON)
  - ❌ Acceso directo a BD: No (usa get_db)

### 2. **Database Layer** (app/database.py, app/models.py)

Gestión de persistencia con SQLAlchemy + PostgreSQL.

- **Responsabilidades:**
  - Pool de conexiones
  - Transacciones
  - Inicialización de tablas (DDL)
  - Sesiones con context managers

- **Componentes:**
  - **engine**: Conexión a PostgreSQL
  - **SessionLocal**: Factory de sesiones
  - **Base**: Clase base para ORM
  - **get_db()**: Dependencia FastAPI

### 3. **Business Logic Layer** (app/sandbox/executor.py)

Lógica de ejecución y evaluación de código.

- **Responsabilidades:**
  - Validación de seguridad (AST parsing)
  - Compilación (Java, C, C++)
  - Ejecución en subprocess
  - Captura de output
  - Comparación de resultados

- **Separación de concerns:**
  - **SandboxExecutor**: Orquestación
  - **_validar_ast_python()**: Seguridad
  - **_compilar_*()**: Compiladores
  - **_ejecutar_caso()**: Ejecución

### 4. **Configuration Layer** (app/core/config.py)

Gestión centralizada de configuración.

- **Responsabilidades:**
  - Cargar .env
  - Validar con Pydantic
  - Proporcionar a toda la app (singleton con @lru_cache)

---

## Modelos de Datos (ORM)

### CasoPrueba

```python
class CasoPrueba(Base):
    id_caso: int           # PK
    id_tarea_ref: int      # L-FK (no FK física)
    entrada_datos: str     # stdin
    salida_esperada: str   # stdout esperado
    tiempo_limite_ms: int  # timeout
    descripcion: str       # opcional
    es_obligatorio: bool   # si falla, reprueba
    creado_en: datetime    # immutable
```

**Índices:**
- PK: `id_caso`
- INDEX: `id_tarea_ref` (búsquedas por tarea)
- INDEX: `es_obligatorio` (filtros)

### ResultadoEjecucion

```python
class ResultadoEjecucion(Base):
    id_resultado: int          # PK
    id_intento_ref: int        # L-FK
    id_tarea_ref: int          # L-FK
    lenguaje: str              # python|javascript|java|c|cpp
    estado_compilacion: str    # SUCCESS|COMPILATION_ERROR|RUNTIME_ERROR
    aprobado: bool             # si pasó todos los obligatorios
    casos_totales: int         # total de casos ejecutados
    casos_aprobados: int       # casos que pasaron
    tiempo_usado_ms: int       # tiempo total
    memoria_usada_kb: int      # (opcional, para futuro)
    salida_consola: str        # errores de compilación
    detalle_casos: str         # JSON serializado
    ejecutado_en: datetime     # immutable, UTC
```

**Índices:**
- PK: `id_resultado`
- INDEX: `id_intento_ref` (consultas por intento)
- INDEX: `id_tarea_ref` (consultas por tarea)
- INDEX: `ejecutado_en` (ordenamientos)

---

## Seguridad del Sandbox

### Nivel 1: AST Parsing (Python)

Se escanea el código **antes de ejecutar** usando `ast.parse()`:

```python
# Bloquear imports
if isinstance(node, ast.Import):
    for alias in node.names:
        if alias.name in MODULOS_BLOQUEADOS:
            raise ValueError(f"Módulo '{alias.name}' bloqueado")

# Bloquear símbolos
elif isinstance(node, ast.Call):
    if node.func.id in SIMBOLOS_BLOQUEADOS:
        raise ValueError(f"Función '{node.func.id}' bloqueada")
```

**Módulos bloqueados:** os, sys, subprocess, socket, threading, importlib, etc.
**Símbolos bloqueados:** exec, eval, compile, open, __import__

### Nivel 2: Timeout Enforcement

Cada caso tiene un `tiempo_limite_ms`:

```python
result = subprocess.run(
    cmd,
    input=stdin_bytes,
    timeout=tiempo_limite_ms / 1000.0  # Convertir a segundos
)
```

Si `TimeoutExpired` → Caso falla sin bloquear otros.

### Nivel 3: I/O Isolation

- **stdin:** Solo desde caso de prueba
- **stdout:** Capturado
- **stderr:** Capturado
- **Archivos:** Se usan directorios temporales (`tempfile.TemporaryDirectory`)
- **Red:** Sin acceso (subprocess no abre conexiones)

### Nivel 4: User Isolation (Docker)

El contenedor corre como usuario `runner` (non-root):

```dockerfile
RUN groupadd -r runner && useradd -r -g runner runner
USER runner
```

### Nivel 5: Resource Limits

- **Tiempo:** Timeout por caso
- **Memoria:** Sin límite actual (posible mejora: `resource.setrlimit()`)
- **CPU:** Sin límite actual (posible mejora: cgroups)

---

## Manejo de Errores

### Niveles de Error

| Nivel | Tipo | Statuscode | Respuesta |
|-------|------|------------|-----------|
| Validación | 400/422 | FastAPI auto | `{"detail": "..."}` |
| Recurso no encontrado | 404 | Manual | `{"detail": "..."}` |
| Error de negocio | 200 | En resultado | `{"estado_compilacion": "ERROR"}` |
| Error interno | 500 | Handler global | `{"detail": "Error interno"}` |

### Ejemplos

**Validación Pydantic (422):**
```
POST /execute
{"lenguaje": "rust"}  ← no soportado
→ 422 Unprocessable Entity
```

**Recurso no encontrado (404):**
```
POST /execute (id_tarea_ref=999 sin casos)
→ 404 Not Found
```

**Error de negocio (200 + estado):**
```
POST /execute (código con import os)
→ 200 OK
{"estado_compilacion": "COMPILATION_ERROR", "aprobado": false}
```

---

## Flujo de Compilación (Lenguajes compilados)

### Java

```bash
# 1. Guardar en temp: Main.java
# 2. Compilar:
javac Main.java

# 3. Si error → COMPILATION_ERROR
# 4. Si ok → Ejecutar:
java -cp {temp_path} Main

# Nota: Clase DEBE llamarse Main
```

### C

```bash
# 1. Guardar en temp: main.c
# 2. Compilar:
gcc main.c -o main -lm

# 3. Si error → COMPILATION_ERROR
# 4. Si ok → Ejecutar:
./main
```

### C++

```bash
# 1. Guardar en temp: main.cpp
# 2. Compilar:
g++ main.cpp -o main -std=c++17

# 3. Si error → COMPILATION_ERROR
# 4. Si ok → Ejecutar:
./main
```

---

## Serialización de Resultados

### JSON en `detalle_casos`

El campo `detalle_casos` en `ResultadoEjecucion` almacena JSON:

```json
[
  {
    "id_caso": 1,
    "descripcion": "Suma básica",
    "entrada_datos": "5 3",
    "salida_esperada": "8",
    "salida_obtenida": "8",
    "paso": true,
    "tiempo_ms": 45,
    "es_obligatorio": true,
    "error": null
  },
  {
    "id_caso": 2,
    "descripcion": "Suma grande",
    "entrada_datos": "100 200",
    "salida_esperada": "300",
    "salida_obtenida": "300",
    "paso": true,
    "tiempo_ms": 40,
    "es_obligatorio": true,
    "error": null
  }
]
```

**Ventajas:**
- ✅ Flexibilidad: Agregar campos sin migración
- ✅ Performance: Lectura directa (sin JOIN)
- ✅ Historial: Snapshot exacto del resultado

**Desventajas:**
- ❌ Queries complejas (no es relacional)
- ❌ Indexación limitada

---

## Claves Lógicas (L-FK) vs Foreign Keys

### ¿Por qué NO usar FK físicas?

```sql
-- ❌ NO hacer:
ALTER TABLE resultados_ejecucion
ADD CONSTRAINT fk_intento
FOREIGN KEY (id_intento_ref)
REFERENCES intentos(id_intento);  -- Tabla del MS1 ❌ ACOPLAMIENTO
```

**Problemas:**
- MS2 depende de MS1 (acoplamiento)
- Cambios en MS1 → cambios en MS2
- Consistencia distribuida imposible

### Solución: Claves Lógicas (L-FK)

```python
# En MS2:
class ResultadoEjecucion:
    id_intento_ref: int  # INTEGER simple, sin FK
    # Índice para performance
    # __table_args__ = (Index("idx_id_intento_ref", "id_intento_ref"),)

# El MS1 es responsable de validar que id_intento_ref existe
# MS2 confía en el API Gateway que le pasa datos válidos
```

**Ventajas:**
- ✅ Independencia total entre microservicios
- ✅ Escalabilidad (sin consultas cross-db)
- ✅ Resiliencia (MS1 caído no afecta MS2 vio resultados anteriores)

---

## Patrones de Diseño

### 1. **Dependency Injection**

```python
@app.post("/execute")
def ejecutar_codigo(
    request: EjecucionRequest,
    db: Session = Depends(get_db),  # ← Inyección
) -> EjecucionResponse:
    pass
```

### 2. **Repository Pattern** (Implícito)

```python
# En lugar de:
db.query(CasoPrueba).filter(...).all()

# Se podría hacer:
casos = caso_repository.obtener_por_tarea(id_tarea)
```

### 3. **Factory Pattern**

```python
# SandboxExecutor actúa como factory de resultados
executor = SandboxExecutor(max_timeout_ms=10000)
resultado = executor.ejecutar(lenguaje, codigo, casos)
```

### 4. **Singleton Pattern**

```python
@lru_cache()
def get_settings() -> Settings:
    return Settings()
```

---

## Performance Considerations

### Query Optimization

**Índices en `casos_prueba`:**
```sql
CREATE INDEX idx_casos_prueba_id_tarea_ref ON casos_prueba(id_tarea_ref);
```

**Índices en `resultados_ejecucion`:**
```sql
CREATE INDEX idx_resultados_id_intento_ref ON resultados_ejecucion(id_intento_ref);
CREATE INDEX idx_resultados_id_tarea_ref ON resultados_ejecucion(id_tarea_ref);
CREATE INDEX idx_resultados_ejecutado_en ON resultados_ejecucion(ejecutado_en);
```

### Connection Pooling

```python
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,     # Valida conexión antes de usar
    pool_size=10,            # Conexiones por thread
    max_overflow=20,         # Conexiones extra permitidas
)
```

### Async Considerations

Actualmente **síncrono** por:
1. SQLAlchemy ORM (mejor con sync)
2. subprocess (síncrono)
3. Sandbox execution (esperamos resultado antes de retornar)

**Posible mejora:** FastAPI en modo `async` con `asyncio` + AsyncSession

---

## Testing Strategy

### Unit Tests

```python
def test_ejecutar_python_exitoso(client, db):
    # Arrange
    caso = CasoPrueba(...)
    db.add(caso)
    db.commit()

    # Act
    response = client.post("/execute", json={...})

    # Assert
    assert response.status_code == 200
    assert response.json()["aprobado"] is True
```

### Integration Tests

```python
def test_flujo_completo():
    # 1. Crear casos
    # 2. Ejecutar código
    # 3. Consultar resultado
    # 4. Verificar BD
```

### Performance Tests

```bash
# Ejecutar 100 códigos simultáneamente
ab -n 100 -c 10 http://localhost:8000/execute
```

---

## Documentación API (OpenAPI)

FastAPI genera automáticamente:

- **Swagger UI:** `/docs`
- **ReDoc:** `/redoc`
- **OpenAPI JSON:** `/openapi.json`

Todas las docstrings Python se convierten en descripciones OpenAPI.

---

## Deployment Considerations

### Docker

**Multi-stage build:**
1. **Builder:** Python + dependencias compiladas
2. **Runtime:** Only runtime + código (smaller image)

**Usuario non-root:**
```dockerfile
RUN useradd -r -g runner runner
USER runner
```

### Scaling

- **Horizontal:** Replicas con load balancer
- **Vertical:** Pool size, max_overflow
- **Caching:** Redis para resultados frecuentes (futuro)

---

## Future Improvements

1. **Async/await** con AsyncSession
2. **Caching** de resultados con Redis
3. **Metrics** con Prometheus
4. **Resource limits** con cgroups
5. **Distributed tracing** con OpenTelemetry
6. **More languages** (Go, Rust, PHP, etc.)

---

**Última actualización:** 2026-05-19  
**Versión:** 1.0.0-hackathon
