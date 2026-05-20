# GUÍA DE INSTALACIÓN Y EJECUCIÓN

## Requisitos Previos

- Docker y Docker Compose
- Python 3.11+
- Node.js 18+
- npm o yarn

## 1. Configuración del Backend

### 1.1 Clonar el Repositorio

```bash
git clone <repo-url>
cd Tercer-Hackaton/backend
```

### 1.2 Crear archivo .env

```bash
cp .env.example .env
```

### 1.3 Iniciar Servicios con Docker Compose

```bash
docker-compose up -d
```

Esto iniciará:
- 9 PostgreSQL databases (una por microservicio)
- RabbitMQ (port 5672, management UI on 15672)
- Redis (port 6379)

### 1.4 Iniciar cada Microservicio

Abrir terminal en cada carpeta de microservicio y ejecutar:

```bash
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 8001  # Auth Service como ejemplo
```

O usar el script de inicio:

```bash
# Terminal 1 - Auth Service
cd auth-service && uvicorn app.main:app --reload --port 8001

# Terminal 2 - Submission Service
cd submission-service && uvicorn app.main:app --reload --port 8004

# Terminal 3 - Execution Service
cd execution-service && uvicorn app.main:app --reload --port 8005

# Terminal 4 - Grading Service
cd grading-service && uvicorn app.main:app --reload --port 8006

# Terminal 5 - Plagiarism Service
cd plagiarism-service && uvicorn app.main:app --reload --port 8007

# Continuar con los otros servicios restantes...
```

## 2. Configuración del Frontend

### 2.1 Instalar dependencias

```bash
cd frontend
npm install
```

### 2.2 Crear archivo .env

```bash
REACT_APP_API_URL=http://localhost:8000
```

### 2.3 Iniciar servidor de desarrollo

```bash
npm run dev
```

Frontend estará disponible en http://localhost:3000

## 3. Flujo de Funcionamiento

### 3.1 Flujo de Envío y Calificación

```
1. Usuario inicia sesión (Auth Service)
   ├─ POST /api/auth/login
   ├─ Retorna: access_token + refresh_token
   └─ Se almacena en localStorage

2. Estudiante envía código (Submission Service)
   ├─ POST /api/submissions
   ├─ Datos: assignment_id, student_id, code_content, language
   ├─ Evento: submissionCreated → RabbitMQ
   └─ Respuesta: submission_id

3. Execution Service recibe evento
   ├─ Consume: submission.submissionCreated
   ├─ Ejecuta el código en sandbox
   ├─ Compara contra test cases
   ├─ Publica: execution.executionCompleted
   └─ Guarda resultados en execution_results

4. Grading Service recibe evento
   ├─ Consume: submission.executionCompleted
   ├─ Calcula score basado en:
   │  ├─ Test cases pasados
   │  ├─ Eficiencia de código
   │  ├─ Rúbrica definida
   │  └─ Criterios de evaluación
   ├─ Publica: grading.gradingCompleted
   └─ Guarda grades en BD

5. Plagiarism Service recibe evento
   ├─ Consume: grading.gradingCompleted
   ├─ Genera fingerprint del código
   ├─ Compara contra envíos previos
   ├─ Detecta similitudes
   ├─ Publica: plagiarism.plagiarismAnalyzed
   └─ Guarda reportes en BD

6. Audit Service registra todo
   ├─ Consume: TODOS los eventos
   ├─ Registra user_id, timestamp, acción
   ├─ Información completa para auditoría
   └─ Permite trazabilidad completa
```

## 4. Endpoints Principales

### Auth Service (8001)

```
POST   /api/auth/register         # Registro
POST   /api/auth/login            # Login
POST   /api/auth/refresh          # Refrescar token
POST   /api/auth/logout           # Logout
GET    /api/auth/me               # Usuario actual
POST   /api/auth/change-password  # Cambiar contraseña
```

### Submission Service (8004)

```
POST   /api/submissions/                    # Enviar código
GET    /api/submissions/history/{assignment_id}  # Historial
GET    /api/submissions/{submission_id}    # Detalles del envío
```

### Grading Service (8006)

```
GET    /api/grades/{submission_id}         # Obtener calificación
POST   /api/grades/                        # Crear calificación
PUT    /api/grades/{submission_id}         # Actualizar calificación
```

### Plagiarism Service (8007)

```
GET    /api/plagiarism/{submission_id}     # Reporte de plagio
GET    /api/plagiarism/{assignment_id}/analysis  # Análisis general
```

## 5. Ejemplo de Flujo Completo

### 5.1 Registro e Inicio de Sesión

```bash
# 1. Registro
curl -X POST http://localhost:8001/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "estudiante@ejemplo.com",
    "username": "estudiante",
    "password": "SecurePass123!",
    "first_name": "Juan",
    "last_name": "Pérez",
    "role": "student"
  }'

# Respuesta:
{
  "success": true,
  "data": {
    "user": {...},
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "expires_in": 3600
  }
}

# 2. Login
curl -X POST http://localhost:8001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "estudiante",
    "password": "SecurePass123!"
  }'
```

### 5.2 Enviar Código

```bash
# 1. Enviar código
curl -X POST http://localhost:8004/api/submissions/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "assignment_id": "task-123",
    "code_content": "print(\"Hello World\")",
    "language": "python"
  }'

# Respuesta:
{
  "success": true,
  "data": {
    "id": "sub-456",
    "status": "submitted",
    "attempt_number": 1,
    "submitted_at": "2024-05-19T10:30:00Z"
  }
}

# 2. Consultar historial
curl -X GET http://localhost:8004/api/submissions/history/task-123 \
  -H "Authorization: Bearer <access_token>"

# 3. Obtener detalles del envío
curl -X GET http://localhost:8004/api/submissions/sub-456 \
  -H "Authorization: Bearer <access_token>"
```

### 5.3 Consultar Calificación

```bash
curl -X GET http://localhost:8006/api/grades/sub-456 \
  -H "Authorization: Bearer <access_token>"

# Respuesta:
{
  "success": true,
  "data": {
    "id": "grade-789",
    "submission_id": "sub-456",
    "score": 85,
    "percentage": 85.0,
    "status": "completed",
    "feedback": "Código correcto, pero puede ser optimizado...",
    "rubric_scores": {...}
  }
}
```

### 5.4 Revisar Plagio

```bash
curl -X GET http://localhost:8007/api/plagiarism/sub-456 \
  -H "Authorization: Bearer <access_token>"

# Respuesta:
{
  "success": true,
  "data": {
    "id": "plagiarism-123",
    "submission_id": "sub-456",
    "plagiarism_percentage": 5.2,
    "status": "completed",
    "matches": [...]
  }
}
```

## 6. RabbitMQ Management UI

Acceder a: http://localhost:15672
Usuario: guest
Contraseña: guest

Aquí puedes ver:
- Exchanges: code-grading
- Queues: submission.*, execution.*, grading.*, plagiarism.*
- Mensajes publicados y consumidos

## 7. Troubleshooting

### Error de conexión a DB

```bash
# Verificar que los contenedores estén corriendo
docker-compose ps

# Ver logs de un servicio
docker-compose logs auth-db
```

### Error de portque ya está en uso

```bash
# Cambiar puerto en .env o comando de uvicorn
uvicorn app.main:app --reload --port 8010
```

### RabbitMQ connection error

```bash
# Verificar RabbitMQ está corriendo
docker-compose ps | grep rabbitmq

# Reiniciar RabbitMQ
docker-compose restart rabbitmq
```

## 8. Estructura de Base de Datos

Cada microservicio tiene su propia BD con tablas específicas:

### auth_db
- users
- sessions
- roles

### submission_db
- submissions
- submission_files

### execution_db
- execution_logs
- test_cases
- execution_results

### grading_db
- grades
- grade_rubrics

### plagiarism_db
- code_signatures
- plagiarism_reports
- plagiarism_matches

### audit_db
- audit_logs
- event_logs

## 9. Seguridad

- Todos los requests requieren JWT en header Authorization
- Contraseñas hasheadas con bcrypt
- CORS habilitado para desarrollo
- Sanitización de entrada con Pydantic
- Sandbox para ejecución de código

## 10. Próximos Pasos

1. Implementar API Gateway (puerto 8000)
2. Agregar más lenguajes de programación soportados
3. Mejorar algoritmo de detección de plagio
4. Agregar caching con Redis
5. Implementar logging centralizado
6. Agregar métricas con Prometheus
7. Implementar circuity breaker para resilencia

