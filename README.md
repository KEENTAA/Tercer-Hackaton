# MS2 - Motor de Ejecución y Evaluación

**Microservicio 2 del Sistema de Calificación Automática de Tareas de Programación**

Frog Software Ltda. | Hackathon 19/05/2026

---

## Descripción General

El **MS2** es el motor de ejecución que permite compilar y ejecutar código de estudiantes en un entorno aislado (sandbox) y evaluar su correctitud contra casos de prueba predefinidos.

### Rol en la Arquitectura

```
┌─────────────────┐
│    Frontend     │ Angular
│    Angular      │
└────────┬────────┘
         │
    ┌────▼─────────────────────┐
    │  API Gateway +           │
    │  Orquestador             │
    └────┬──────────┬──────┬───┘
         │          │      │
    ┌────▼──┐  ┌────▼──┐  ┌▼─────────┐
    │  MS1  │  │ MS2   │  │   MS3    │
    │Tasks  │  │Runner │  │Plagiarism│
    │Grading│  │Execute│  │Detector  │
    └───────┘  └───────┘  └──────────┘
               ↑ Este es MS2
```

**Responsabilidades del MS2:**
- Recibir código fuente de estudiantes desde el API Gateway
- Ejecutar el código en un sandbox seguro
- Evaluar la salida contra casos de prueba definidos
- Registrar resultados en su propia BD (sin acceso a otras)
- Retornar veredicto: aprobado/reprobado con detalles

**¿Qué NO hace el MS2?**
- No gestiona estudiantes ni tareas (eso es MS1)
- No accede a BD de otros microservicios
- No decide calificaciones finales
- No retorna código fuente en respuestas

---

## Equipo de Desarrollo

| Rol                  | Responsable        |
|----------------------|--------------------|
| Arquitecto Senior    | Frog Software      |
| Desarrollo Backend   | GitHub Copilot     |
| Sandbox Engine       | Python subprocess  |
| DevOps               | Docker + Compose   |

---

## Base de Datos: `db_code_runner`

### Motor: PostgreSQL 16+

### Tabla: `casos_prueba`

Casos de prueba para evaluar el código de estudiantes.

| Columna              | Tipo       | Restricciones        | Descripción                        |
|----------------------|------------|----------------------|------------------------------------|
| `id_caso`            | SERIAL     | PK, AUTO_INCREMENT   | Identificador único                |
| `id_tarea_ref`       | INTEGER    | NOT NULL, INDEX      | L-FK lógica a tarea (MS1)          |
| `entrada_datos`      | TEXT       | NULLABLE             | stdin para el código (ej: "5 3")   |
| `salida_esperada`    | TEXT       | NOT NULL             | stdout esperado exacto             |
| `tiempo_limite_ms`   | INTEGER    | NOT NULL, CHECK>0    | Timeout en ms (default: 3000)      |
| `descripcion`        | VARCHAR    | NULLABLE, max_len255 | Nombre descriptivo (ej: "Test 1")  |
| `es_obligatorio`     | BOOLEAN    | NOT NULL, DEFAULT=1  | Si falla, reprueba el intento      |
| `creado_en`          | TIMESTAMPTZ| NOT NULL, DEFAULT NOW| Timestamp UTC de creación          |

**Índices:**
- PRIMARY KEY: `id_caso`
- INDEX: `id_tarea_ref` (búsquedas por tarea)
- INDEX: `es_obligatorio` (para filtrar pruebas obligatorias)

**Notas de Diseño:**
- `id_tarea_ref` es **L-FK lógica** (no FK física). Apunta a `Tareas.id_tarea` en MS1.
- Desacoplamiento total: MS2 no valida si `id_tarea_ref` existe en MS1.
- Múltiples casos por tarea: 1 tarea = N casos de prueba.

---

### Tabla: `resultados_ejecucion`

Resultados de cada ejecución de código de un estudiante.

| Columna                | Tipo       | Restricciones | Descripción                              |
|------------------------|------------|----------------|------------------------------------------|
| `id_resultado`         | SERIAL     | PK             | Identificador único                      |
| `id_intento_ref`       | INTEGER    | NOT NULL, INDEX| L-FK lógica a intento (MS1)              |
| `id_tarea_ref`         | INTEGER    | NOT NULL, INDEX| L-FK lógica a tarea (MS1)                |
| `lenguaje`             | VARCHAR(30)| NOT NULL       | 'python' \| 'javascript' \| 'java' \| 'c' \| 'cpp' |
| `estado_compilacion`   | VARCHAR(20)| NOT NULL, CHECK| 'SUCCESS' \| 'COMPILATION_ERROR' \| 'RUNTIME_ERROR' |
| `aprobado`             | BOOLEAN    | NOT NULL       | Si pasó todos los casos obligatorios     |
| `casos_totales`        | INTEGER    | DEFAULT=0      | Total de casos de prueba ejecutados      |
| `casos_aprobados`      | INTEGER    | DEFAULT=0      | Casos que pasaron                        |
| `tiempo_usado_ms`      | INTEGER    | NULLABLE       | Tiempo total de ejecución en ms          |
| `memoria_usada_kb`     | INTEGER    | NULLABLE       | Memoria consumida en KB (futuro)         |
| `salida_consola`       | TEXT       | NULLABLE       | Mensajes de error (compilación/runtime)  |
| `detalle_casos`        | TEXT       | NULLABLE       | JSON serializado con resultado de c/caso |
| `ejecutado_en`         | TIMESTAMPTZ| NOT NULL, INDEX| Timestamp UTC de ejecución               |

**Índices:**
- PRIMARY KEY: `id_resultado`
- INDEX: `id_intento_ref` (búsquedas por intento)
- INDEX: `id_tarea_ref` (búsquedas por tarea)
- INDEX: `ejecutado_en` (ordenamientos por fecha)

**Notas de Diseño:**
- `detalle_casos` almacena JSON con el resultado de cada caso prueba:
  ```json
  [
    {
      "id_caso": 1,
      "descripcion": "Entrada simple",
      "entrada_datos": "5",
      "salida_esperada": "5",
      "salida_obtenida": "5",
      "paso": true,
      "tiempo_ms": 45,
      "es_obligatorio": true,
      "error": null
    }
  ]
  ```
- Las L-FKs (`id_intento_ref`, `id_tarea_ref`) son **lógicas**: MS2 no valida que existan en MS1.
- Inmutabilidad: Una vez creado, un resultado no se modifica.

---

## Endpoints REST

**Base:** `/api/v1/runner`

### EP1: POST `/test-cases` — Registrar casos de prueba

Permite al profesor (vía API Gateway) registrar los casos de prueba de una tarea.

**Request:**
```http
POST /api/v1/runner/test-cases HTTP/1.1
Content-Type: application/json

{
  "casos": [
    {
      "id_tarea_ref": 42,
      "entrada_datos": "5 3",
      "salida_esperada": "8",
      "tiempo_limite_ms": 2000,
      "descripcion": "Suma de dos números",
      "es_obligatorio": true
    },
    {
      "id_tarea_ref": 42,
      "entrada_datos": "10 20",
      "salida_esperada": "30",
      "tiempo_limite_ms": 2000,
      "descripcion": "Suma mayor",
      "es_obligatorio": true
    }
  ]
}
```

**Response:** `201 Created`
```json
[
  {
    "id_caso": 1,
    "id_tarea_ref": 42,
    "entrada_datos": "5 3",
    "salida_esperada": "8",
    "tiempo_limite_ms": 2000,
    "descripcion": "Suma de dos números",
    "es_obligatorio": true,
    "creado_en": "2026-05-19T14:30:00+00:00"
  },
  {
    "id_caso": 2,
    "id_tarea_ref": 42,
    "entrada_datos": "10 20",
    "salida_esperada": "30",
    "tiempo_limite_ms": 2000,
    "descripcion": "Suma mayor",
    "es_obligatorio": true,
    "creado_en": "2026-05-19T14:30:00+00:00"
  }
]
```

**Errores:**
- `400`: Validación fallida (ej: `tiempo_limite_ms` > 10000)
- `422`: Datos inválidos (ej: `salida_esperada` vacío)

---

### EP2: GET `/test-cases/assignment/{id_tarea_ref}` — Listar casos

Recuperar todos los casos de prueba de una tarea.

**Request:**
```http
GET /api/v1/runner/test-cases/assignment/42 HTTP/1.1
```

**Response:** `200 OK`
```json
[
  {
    "id_caso": 1,
    "id_tarea_ref": 42,
    "entrada_datos": "5 3",
    "salida_esperada": "8",
    "tiempo_limite_ms": 2000,
    "descripcion": "Suma de dos números",
    "es_obligatorio": true,
    "creado_en": "2026-05-19T14:30:00+00:00"
  },
  {
    "id_caso": 2,
    "id_tarea_ref": 42,
    "entrada_datos": "10 20",
    "salida_esperada": "30",
    "tiempo_limite_ms": 2000,
    "descripcion": "Suma mayor",
    "es_obligatorio": true,
    "creado_en": "2026-05-19T14:30:00+00:00"
  }
]
```

**Errores:**
- `404`: No hay casos registrados para esa tarea

---

### EP3: POST `/execute` — EJECUTAR CÓDIGO (PRINCIPAL)

Ejecuta el código de un estudiante en el sandbox y lo evalúa contra los casos de prueba.

**Request:**
```http
POST /api/v1/runner/execute HTTP/1.1
Content-Type: application/json

{
  "id_intento_ref": 123,
  "id_tarea_ref": 42,
  "lenguaje": "python",
  "codigo_fuente": "a, b = map(int, input().split())\nprint(a + b)"
}
```

**Response:** `200 OK`
```json
{
  "id_resultado": 501,
  "id_intento_ref": 123,
  "id_tarea_ref": 42,
  "lenguaje": "python",
  "estado_compilacion": "SUCCESS",
  "aprobado": true,
  "casos_totales": 2,
  "casos_aprobados": 2,
  "tiempo_usado_ms": 89,
  "memoria_usada_kb": null,
  "salida_consola": null,
  "detalle_casos": [
    {
      "id_caso": 1,
      "descripcion": "Suma de dos números",
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
      "descripcion": "Suma mayor",
      "entrada_datos": "10 20",
      "salida_esperada": "30",
      "salida_obtenida": "30",
      "paso": true,
      "tiempo_ms": 44,
      "es_obligatorio": true,
      "error": null
    }
  ],
  "ejecutado_en": "2026-05-19T14:35:00+00:00"
}
```

**Con error de compilación:**
```json
{
  "id_resultado": 502,
  "id_intento_ref": 124,
  "id_tarea_ref": 42,
  "lenguaje": "python",
  "estado_compilacion": "COMPILATION_ERROR",
  "aprobado": false,
  "casos_totales": 2,
  "casos_aprobados": 0,
  "tiempo_usado_ms": null,
  "memoria_usada_kb": null,
  "salida_consola": "El módulo 'os' está bloqueado por razones de seguridad",
  "detalle_casos": [],
  "ejecutado_en": "2026-05-19T14:36:00+00:00"
}
```

**Errores:**
- `404`: No hay casos para esa tarea
- `422`: Validación fallida (lenguaje inválido, código vacío)
- `500`: Error crítico en sandbox

---

### EP4: GET `/results/{id_intento_ref}` — Consultar resultado

Obtener el resultado más reciente de un intento.

**Request:**
```http
GET /api/v1/runner/results/123 HTTP/1.1
```

**Response:** `200 OK`
(Mismo que EP3)

**Errores:**
- `404`: No hay resultados para ese intento

---

### EP5: GET `/results/assignment/{id_tarea_ref}` — Listar resultados

Obtener todos los resultados de una tarea (para el profesor).

**Request:**
```http
GET /api/v1/runner/results/assignment/42 HTTP/1.1
```

**Response:** `200 OK`
```json
[
  { /* ResultadoEjecucion 501 */ },
  { /* ResultadoEjecucion 502 */ },
  /* más resultados, ordenados por ejecutado_en DESC */
]
```

---

### EP6: GET `/health` — Health Check

Verifica el estado del servicio y la conexión a BD.

**Request:**
```http
GET /health HTTP/1.1
```

**Response:** `200 OK`
```json
{
  "status": "ok",
  "servicio": "MS2 - Motor de Ejecución y Evaluación",
  "version": "1.0.0",
  "entorno": "development",
  "base_de_datos": {
    "conectado": true,
    "motor": "PostgreSQL",
    "version": "16+"
  }
}
```

---

## Lenguajes Soportados

| Lenguaje   | Extensión | Runtime/Compilador          | Status  |
|------------|-----------|-----------------------------|---------| 
| Python     | `.py`     | `python3 3.11+`             | ✅ Full |
| JavaScript | `.js`     | `node 18+`                  | ✅ Full |
| Java       | `.java`   | `javac + java`              | ✅ Full |
| C          | `.c`      | `gcc`                       | ✅ Full |
| C++        | `.cpp`    | `g++ (C++17)`               | ✅ Full |

---

## Motor Sandbox (`app/sandbox/executor.py`)

### Características de Seguridad

#### 1. **Bloqueo de módulos peligrosos en Python**

Módulos bloqueados:
- `os`, `sys`, `subprocess`, `shutil`
- `socket`, `ctypes`, `multiprocessing`, `threading`
- `signal`, `importlib`, `pickle`

Si se detecta un import bloqueado → `COMPILATION_ERROR` inmediatamente.

#### 2. **Análisis de AST**

Se escanea el Abstract Syntax Tree del código Python antes de ejecutar:
- Detecta `import` y `from X import Y`
- Detecta llamadas a funciones peligrosas: `eval`, `exec`, `compile`, `open`
- Bloquea sin ejecutar el código

#### 3. **Timeout enforcement**

Cada caso de prueba tiene un `tiempo_limite_ms`:
- El sandbox ejecuta con `subprocess.run(timeout=...)` en segundos
- Si expira → Estado `TIMEOUT` para ese caso
- No afecta a otros casos

#### 4. **Captura de output**

- Se captura `stdout` y `stderr` de cada ejecución
- Se compara `stdout.strip()` vs `salida_esperada.strip()`
- Igualdad exacta tras normalizar espacios en blanco

#### 5. **Usuario no-root en Docker**

El contenedor corre el proceso como usuario `runner` (non-root).

#### 6. **Compilación segura**

- Java: Clase debe llamarse `Main`
- C/C++: Se compilan en directorio temporal
- Binarios se ejecutan, no se persisten

---

## Stack Tecnológico

| Componente         | Versión  | Propósito                          |
|--------------------|----------|-------------------------------------|
| **Lenguaje**       | Python   | 3.11                               |
| **Framework Web**  | FastAPI  | 0.111.0                            |
| **ORM**            | SQLAlchemy | 2.0.30 (declarativo)            |
| **BD**             | PostgreSQL | 16-alpine (Docker)             |
| **Servidor ASGI**  | Uvicorn  | 0.29.0                             |
| **Validación**     | Pydantic | v2.7.1 (BaseModel, validators)    |
| **Config**         | pydantic-settings | 2.2.1 (.env) |
| **Testing**        | pytest   | 8.2.0 + pytest-asyncio             |
| **Contenedores**   | Docker + Compose | Multi-stage, alpine |

---

## Instalación y Ejecución

### Requisitos Previos

- **Python 3.11+**
- **Docker 24+** (si usas Docker Compose)
- **PostgreSQL 16+** (si NO usas Docker)
- **GCC, G++, JDK, Node.js** (si ejecutas sin Docker)

### Opción 1: Con Docker Compose (RECOMENDADO)

#### 1. Clonar el repositorio
```bash
git clone https://github.com/FrogSoftware/repo-ms-code-runner.git
cd repo-ms-code-runner
```

#### 2. Levanta los servicios
```bash
docker compose up --build
```

El servicio estará disponible en: `http://localhost:8000`

**En segundos:**
- PostgreSQL se levanta e inicializa
- Tablas se crean automáticamente
- Swagger accesible en: `http://localhost:8000/docs`

---

### Opción 2: Desarrollo Local (Sin Docker)

#### 1. Clonar y entrar al directorio
```bash
git clone https://github.com/FrogSoftware/repo-ms-code-runner.git
cd repo-ms-code-runner
```

#### 2. Crear virtual environment
```bash
python -m venv .venv
source .venv/bin/activate  # En Windows: .venv\Scripts\activate
```

#### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

#### 4. Configurar .env
```bash
cp .env.example .env
```

Edita `.env` y asegúrate de que `DATABASE_URL` apunta a tu PostgreSQL local:
```
DATABASE_URL=postgresql://runner_user:runner_pass@localhost:5432/db_code_runner
```

#### 5. Asegúrate de que PostgreSQL está corriendo
```bash
# En Linux/Mac:
psql -U postgres

# Crear usuario y BD si no existen:
CREATE USER runner_user WITH PASSWORD 'runner_pass';
CREATE DATABASE db_code_runner OWNER runner_user;
GRANT ALL PRIVILEGES ON DATABASE db_code_runner TO runner_user;
```

#### 6. Ejecutar el servidor
```bash
uvicorn app.main:app --reload --port 8000
```

Swagger: `http://localhost:8000/docs`

---

## Ejemplo de Prueba Completa (cURL)

### 1. Registrar casos de prueba

```bash
curl -X POST http://localhost:8000/api/v1/runner/test-cases \
  -H "Content-Type: application/json" \
  -d '{
    "casos": [
      {
        "id_tarea_ref": 42,
        "entrada_datos": "5 3",
        "salida_esperada": "8",
        "tiempo_limite_ms": 3000,
        "descripcion": "Suma básica",
        "es_obligatorio": true
      }
    ]
  }'
```

**Respuesta:**
```json
[
  {
    "id_caso": 1,
    "id_tarea_ref": 42,
    "entrada_datos": "5 3",
    "salida_esperada": "8",
    "tiempo_limite_ms": 3000,
    "descripcion": "Suma básica",
    "es_obligatorio": true,
    "creado_en": "2026-05-19T14:40:00+00:00"
  }
]
```

---

### 2. Ejecutar código

```bash
curl -X POST http://localhost:8000/api/v1/runner/execute \
  -H "Content-Type: application/json" \
  -d '{
    "id_intento_ref": 100,
    "id_tarea_ref": 42,
    "lenguaje": "python",
    "codigo_fuente": "a, b = map(int, input().split())\nprint(a + b)"
  }'
```

**Respuesta:**
```json
{
  "id_resultado": 1,
  "id_intento_ref": 100,
  "id_tarea_ref": 42,
  "lenguaje": "python",
  "estado_compilacion": "SUCCESS",
  "aprobado": true,
  "casos_totales": 1,
  "casos_aprobados": 1,
  "tiempo_usado_ms": 67,
  "memoria_usada_kb": null,
  "salida_consola": null,
  "detalle_casos": [
    {
      "id_caso": 1,
      "descripcion": "Suma básica",
      "entrada_datos": "5 3",
      "salida_esperada": "8",
      "salida_obtenida": "8",
      "paso": true,
      "tiempo_ms": 67,
      "es_obligatorio": true,
      "error": null
    }
  ],
  "ejecutado_en": "2026-05-19T14:45:00+00:00"
}
```

---

### 3. Consultar resultado

```bash
curl -X GET http://localhost:8000/api/v1/runner/results/100
```

(Misma respuesta que paso 2)

---

### 4. Listar resultados de una tarea

```bash
curl -X GET http://localhost:8000/api/v1/runner/results/assignment/42
```

---

### 5. Health check

```bash
curl -X GET http://localhost:8000/health
```

**Respuesta:**
```json
{
  "status": "ok",
  "servicio": "MS2 - Motor de Ejecución y Evaluación",
  "version": "1.0.0",
  "entorno": "development",
  "base_de_datos": {
    "conectado": true,
    "motor": "PostgreSQL",
    "version": "16+"
  }
}
```

---

## Documentación Interactiva

Una vez levantada la aplicación, accede a:

- **Swagger UI:** `http://localhost:8000/docs`
- **ReDoc:** `http://localhost:8000/redoc`
- **OpenAPI JSON:** `http://localhost:8000/openapi.json`

---

## Notas de Seguridad

✅ **Implementado:**
- AST scanning de Python
- Timeout enforcement
- Usuario non-root en Docker
- Captura segura de output
- Módulos bloqueados en Python
- Compilación en directorio temporal

⚠️ **Limitaciones actuales:**
- Memoria: no se captura en tiempo real (campo nullable)
- CPU: sin límites (requeriría cgroups en producción)
- Red: subprocess por defecto permite acceso a red

**Para producción:**
- Usar contenedores con cgroups limitados
- Implementar límites de CPU/memoria con `resource.setrlimit()`
- Agregar firewall dentro del sandbox

---

## Troubleshooting

### Error: "permission denied" al ejecutar docker compose

```bash
sudo usermod -aG docker $USER
# Logout y login de nuevo
```

### Error: "Port 5432 already in use"

```bash
# Cambiar puerto en docker-compose.yml:
ports:
  - "5433:5432"  # Local: 5433
```

### Error: "Connection refused" a PostgreSQL

```bash
# Verificar que postgres_db está corriendo:
docker ps | grep postgres

# Revisar logs:
docker logs postgres-ms2
```

### Endpoint retorna 404

1. Verifica que los casos de prueba existan:
   ```bash
   curl http://localhost:8000/api/v1/runner/test-cases/assignment/{id_tarea}
   ```

2. Asegúrate que el `id_tarea_ref` en la request coincide

---

## Diagrama de Flujo: EP3 (Ejecutar Código)

```
┌─────────────────────────────────┐
│ POST /execute (EjecucionRequest)│
└────────┬────────────────────────┘
         │
         ▼
    ┌────────────────────────────┐
    │ Validar request (Pydantic) │
    └────────┬───────────────────┘
             │
             ▼
    ┌──────────────────────────────┐
    │ Buscar casos_prueba en BD    │
    │ (id_tarea_ref)               │
    └────────┬─────────────────────┘
             │
        ¿Existen?
        /         \
      SÍ           NO
      │             └──► HTTP 404
      │
      ▼
    ┌────────────────────────────────┐
    │ Executor.ejecutar()            │
    │ (lenguaje, código, casos)      │
    │                                │
    │ Para Python: AST scan          │
    │ Si bloqueado → COMPILATION_ERR │
    │                                │
    │ Para lenguajes compilados:     │
    │ compilar() → si error → error  │
    │                                │
    │ Para cada caso_prueba:         │
    │  - subprocess.run(timeout)     │
    │  - capturar stdout/stderr      │
    │  - comparar salidas            │
    │  - registrar paso/error        │
    │                                │
    │ Retornar ResultadoEjecucionSB │
    └────────┬─────────────────────┘
             │
             ▼
    ┌──────────────────────────────────┐
    │ Guardar en ResultadoEjecucion BD │
    │ - Serializar detalle_casos JSON  │
    │ - Calcular aprobado              │
    └────────┬───────────────────────┘
             │
             ▼
    ┌──────────────────────────────────┐
    │ HTTP 200 + EjecucionResponse      │
    │ (con id_resultado, detalles, etc)│
    └──────────────────────────────────┘
```

---

## Despliegue en Producción

(Fuera del scope del hackathon, pero aquí van notas)

### Mejoras necesarias:
1. **Secrets management:** Usar AWS Secrets Manager o Vault
2. **Logging centralizado:** ELK Stack o CloudWatch
3. **Monitoreo:** Prometheus + Grafana
4. **Rate limiting:** Nginx o API Gateway
5. **Escalado horizontal:** Load balancer + múltiples replicas
6. **CD/CI:** GitHub Actions → ECR → ECS/K8s

---

## Licencia y Atribuciones

**MS2 - Motor de Ejecución y Evaluación**

Desarrollado por **Frog Software Ltda.** para el hackathon 19/05/2026.

---

**¿Preguntas? Consulta `/docs` en la API o abre un issue en GitHub.**

Happy coding! 🚀
