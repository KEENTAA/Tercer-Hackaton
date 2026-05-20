# PRÓXIMOS PASOS - ROADMAP DE IMPLEMENTACIÓN

## Estado Actual del Sistema

✅ **Completados**:
- Arquitectura general diseñada
- Docker Compose con 9 BD, RabbitMQ, Redis
- Auth Service (completo)
- Submission Service (completo)
- Execution Service (dominio + esqueleto)
- Grading Service (dominio + esqueleto)
- Plagiarism Service (dominio + esqueleto)
- Frontend React (completo con routing básico)
- Dockerfiles para todos los servicios

❌ **Faltando**:
- User Service (completo)
- Assignment Service (completo)
- Audit Service (completo)
- LMS Integration Service (completo)
- API Gateway (puerto 8000)
- Event consumers en cada servicio
- Controllers y repositories en execution, grading, plagiarism
- Frontend: dashboards teacher/admin, detalles de resultados
- Tests unitarios e integración
- Documentación API OpenAPI/Swagger

---

## FASE 1: Completar Servicios Base (2-3 días)

### 1.1 User Service

**Archivos a crear**:

```
backend/user-service/
├── app/
│   ├── __init__.py
│   ├── main.py                    # FastAPI app
│   ├── config.py                  # Config
│   ├── domain/
│   │   └── models.py              # User Profile, UserPreferences
│   ├── repositories/
│   │   └── user_repository.py     # CRUD operaciones
│   ├── services/
│   │   └── user_service.py        # Lógica
│   └── controllers/
│       └── user_controller.py     # Endpoints
├── requirements.txt
└── Dockerfile
```

**Endpoints**:
```
GET    /api/users/{user_id}         # Obtener perfil
PUT    /api/users/{user_id}         # Actualizar perfil
GET    /api/users/search            # Buscar usuarios
POST   /api/users/{user_id}/preferences  # Preferencias
```

### 1.2 Assignment Service

**Archivos a crear**:

```
backend/assignment-service/
├── app/
│   ├── main.py
│   ├── config.py
│   ├── domain/
│   │   └── models.py              # Assignment, TestCase, Rubric
│   ├── repositories/
│   │   └── assignment_repository.py
│   ├── services/
│   │   └── assignment_service.py
│   └── controllers/
│       └── assignment_controller.py
├── requirements.txt
└── Dockerfile
```

**Endpoints**:
```
POST   /api/assignments/            # Crear tarea
GET    /api/assignments/{id}        # Obtener detalles
PUT    /api/assignments/{id}        # Actualizar
DELETE /api/assignments/{id}        # Eliminar
GET    /api/assignments/{id}/test-cases  # Test cases
POST   /api/assignments/{id}/test-cases  # Agregar test
```

### 1.3 Audit Service

**Archivos a crear**:

```
backend/audit-service/
├── app/
│   ├── main.py
│   ├── config.py
│   ├── domain/
│   │   └── models.py              # AuditLog, EventLog
│   ├── repositories/
│   │   └── audit_repository.py
│   ├── services/
│   │   ├── audit_service.py       # Lógica
│   │   └── event_consumer.py      # Escucha eventos
│   └── controllers/
│       └── audit_controller.py
├── requirements.txt
└── Dockerfile
```

**Endpoints**:
```
GET    /api/audits/                 # Logs de auditoría
GET    /api/audits/user/{user_id}   # Auditoría de usuario
GET    /api/audits/{submission_id}  # Auditoría de envío
GET    /api/audits/events           # Stream de eventos
```

### 1.4 LMS Integration Service

**Archivos a crear**:

```
backend/lms-service/
├── app/
│   ├── main.py
│   ├── config.py
│   ├── domain/
│   │   └── models.py              # LMSIntegration, SyncLog
│   ├── repositories/
│   │   └── lms_repository.py
│   ├── services/
│   │   ├── lms_service.py         # Lógica
│   │   ├── canvas_client.py       # Integración Canvas
│   │   └── moodle_client.py       # Integración Moodle
│   └── controllers/
│       └── lms_controller.py
├── requirements.txt
└── Dockerfile
```

**Endpoints**:
```
POST   /api/lms/connect             # Conectar LMS
GET    /api/lms/sync                # Sincronizar cursos
POST   /api/lms/grades/sync         # Sincronizar calificaciones
GET    /api/lms/status              # Estado de sincronización
```

---

## FASE 2: Implementar Event Consumers (1-2 días)

### 2.1 Execution Service Consumer

```python
# backend/execution-service/app/services/event_consumer.py

import pika
import json
from typing import Callable

class ExecutionEventConsumer:
    def __init__(self, rabbitmq_url: str):
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(url=rabbitmq_url)
        )
        self.channel = self.connection.channel()
        self.setup_consumer()
    
    def setup_consumer(self):
        # Declarar exchange
        self.channel.exchange_declare(
            exchange='code-grading',
            exchange_type='topic',
            durable=True
        )
        
        # Declarar queue
        self.channel.queue_declare(
            queue='execution.queue',
            durable=True
        )
        
        # Binding
        self.channel.queue_bind(
            exchange='code-grading',
            queue='execution.queue',
            routing_key='submission.*'
        )
    
    def start(self):
        def callback(ch, method, properties, body):
            try:
                event = json.loads(body)
                self.handle_event(event)
                ch.basic_ack(delivery_tag=method.delivery_tag)
            except Exception as e:
                print(f"Error: {e}")
                ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
        
        self.channel.basic_consume(
            queue='execution.queue',
            on_message_callback=callback
        )
        
        print("Execution Service listening for events...")
        self.channel.start_consuming()
    
    def handle_event(self, event: dict):
        if event['event_type'] == 'submission.submissionCreated':
            self.handle_submission_created(event['data'])
    
    def handle_submission_created(self, data: dict):
        submission_id = data['submission_id']
        code_content = data['code_content']
        language = data['language']
        
        # Ejecutar código
        result = execute_code_in_sandbox(code_content, language)
        
        # Publicar evento siguiente
        publish_execution_completed(submission_id, result)
```

### 2.2 Grading Service Consumer

```python
# backend/grading-service/app/services/event_consumer.py

class GradingEventConsumer:
    def handle_event(self, event: dict):
        if event['event_type'] == 'execution.executionCompleted':
            self.handle_execution_completed(event['data'])
    
    def handle_execution_completed(self, data: dict):
        submission_id = data['submission_id']
        test_results = data['test_results']
        
        # Calcular calificación
        score = calculate_score(test_results)
        
        # Guardar en BD
        grade = Grade(
            submission_id=submission_id,
            score=score,
            percentage=(score/100)*100,
            status='completed'
        )
        save_grade(grade)
        
        # Publicar evento
        publish_grading_completed(submission_id, score)
```

### 2.3 Plagiarism Service Consumer

```python
# backend/plagiarism-service/app/services/event_consumer.py

class PlagiarismEventConsumer:
    def handle_event(self, event: dict):
        if event['event_type'] == 'grading.gradingCompleted':
            self.handle_grading_completed(event['data'])
    
    def handle_grading_completed(self, data: dict):
        submission_id = data['submission_id']
        assignment_id = data['assignment_id']
        
        # Obtener código de envío
        code = get_submission_code(submission_id)
        
        # Generar fingerprint
        fingerprint = generate_code_fingerprint(code)
        
        # Comparar con envíos previos
        matches = find_similar_submissions(assignment_id, fingerprint)
        
        # Crear reporte
        report = PlagiarismReport(
            submission_id=submission_id,
            assignment_id=assignment_id,
            plagiarism_percentage=calculate_plagiarism_percentage(matches),
            matches=matches
        )
        save_plagiarism_report(report)
        
        # Publicar evento
        publish_plagiarism_analyzed(submission_id, report)
```

### 2.4 Audit Service Consumer (escucha TODOS los eventos)

```python
# backend/audit-service/app/services/event_consumer.py

class AuditEventConsumer:
    def setup_consumer(self):
        # Escuchar todos los eventos
        self.channel.queue_bind(
            exchange='code-grading',
            queue='audit.queue',
            routing_key='*.*'  # Todos los eventos
        )
    
    def handle_event(self, event: dict):
        # Registrar evento en BD
        audit_log = AuditLog(
            event_type=event['event_type'],
            timestamp=event['timestamp'],
            data=event['data'],
            status='logged'
        )
        save_audit_log(audit_log)
```

---

## FASE 3: API Gateway (1 día)

### 3.1 Crear API Gateway

```
backend/api-gateway/
├── app/
│   ├── main.py
│   ├── config.py
│   ├── middleware/
│   │   ├── auth.py               # Validar JWT
│   │   ├── logging.py            # Logging
│   │   └── rate_limit.py         # Rate limiting
│   ├── routers/
│   │   ├── auth.py
│   │   ├── submissions.py
│   │   ├── grades.py
│   │   └── ...
│   └── clients/
│       ├── auth_client.py        # Cliente a auth-service
│       └── submission_client.py
├── requirements.txt
└── Dockerfile
```

**Rutas**:
```
/api/auth/*          → auth-service (8001)
/api/submissions/*   → submission-service (8004)
/api/executions/*    → execution-service (8005)
/api/grades/*        → grading-service (8006)
/api/plagiarism/*    → plagiarism-service (8007)
/api/users/*         → user-service (8002)
/api/assignments/*   → assignment-service (8003)
/api/audits/*        → audit-service (8008)
/api/lms/*           → lms-service (8009)
```

---

## FASE 4: Frontend Expansions (2-3 días)

### 4.1 Teacher Dashboard

```
frontend/src/pages/
├── TeacherDashboard.tsx
│   ├── Assignment management
│   ├── Student submissions view
│   ├── Grading interface
│   ├── Plagiarism reports
│   └── Statistics
```

### 4.2 Admin Dashboard

```
frontend/src/pages/
├── AdminDashboard.tsx
│   ├── User management
│   ├── System metrics
│   ├── Audit logs viewer
│   ├── LMS integrations
│   └── System health
```

### 4.3 Submission Details Page

```
frontend/src/pages/
├── SubmissionDetails.tsx
│   ├── Code preview
│   ├── Test results
│   ├── Grade details
│   ├── Plagiarism report
│   └── Feedback
```

---

## FASE 5: Testing (2-3 días)

### 5.1 Unit Tests

```
backend/*/tests/
├── unit/
│   ├── test_models.py
│   ├── test_repositories.py
│   ├── test_services.py
│   └── test_controllers.py
```

### 5.2 Integration Tests

```
backend/*/tests/
├── integration/
│   ├── test_api_endpoints.py
│   ├── test_event_flow.py
│   └── test_database.py
```

### 5.3 End-to-End Tests

```
frontend/tests/
├── e2e/
│   ├── login_flow.spec.ts
│   ├── submit_code.spec.ts
│   ├── view_results.spec.ts
│   └── plagiarism_check.spec.ts
```

---

## FASE 6: Documentación (1-2 días)

### 6.1 OpenAPI/Swagger

Agregar a cada servicio:
```python
from fastapi.openapi.utils import get_openapi

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title="Auth Service API",
        version="1.0.0",
        description="Servicio de autenticación",
        routes=app.routes,
    )
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi
```

Accesible en: `/docs` (Swagger UI)

### 6.2 Documentación de API

```
docs/
├── API_REFERENCE.md
├── EVENT_DRIVEN_ARCHITECTURE.md (✅ Hecho)
├── ARCHITECTURE.md (✅ Hecho)
├── DEPLOYMENT_GUIDE.md (✅ Hecho)
├── INSTALLATION_GUIDE.md (✅ Hecho)
├── DEVELOPMENT.md
├── TROUBLESHOOTING.md
└── EXAMPLES.md
```

---

## Estimación de Tiempo

| Fase | Duración | Prioridad |
|------|----------|-----------|
| 1. Servicios base | 2-3 días | Crítica |
| 2. Event consumers | 1-2 días | Crítica |
| 3. API Gateway | 1 día | Alta |
| 4. Frontend | 2-3 días | Alta |
| 5. Testing | 2-3 días | Media |
| 6. Documentación | 1-2 días | Media |
| **TOTAL** | **9-14 días** | |

---

## Comandos Rápidos de Desarrollo

### Iniciar un nuevo servicio

```bash
cd backend
mkdir nuevo-service
cd nuevo-service

# Crear estructura
mkdir -p app/{domain,repositories,services,controllers}
touch app/__init__.py
touch app/main.py
touch app/config.py
touch requirements.txt
touch Dockerfile

# Puerto asignado
# Auth: 8001
# User: 8002
# Assignment: 8003
# Submission: 8004
# Execution: 8005
# Grading: 8006
# Plagiarism: 8007
# Audit: 8008
# LMS: 8009
```

### Ejecutar tests

```bash
# Backend
pytest backend/

# Frontend
npm test
```

### Ver logs en tiempo real

```bash
docker-compose logs -f servicename
```

### Acceder a base de datos

```bash
docker-compose exec auth-db psql -U postgres -d auth_db
```

---

## Checklist de Finalización

- [ ] User Service implementado
- [ ] Assignment Service implementado
- [ ] Audit Service implementado
- [ ] LMS Integration Service implementado
- [ ] Event consumers en execution, grading, plagiarism services
- [ ] API Gateway en port 8000
- [ ] Frontend con dashboards teacher/admin
- [ ] Frontend con detalles de resultados
- [ ] Tests unitarios para todos los servicios
- [ ] Tests de integración para flujos completos
- [ ] Tests E2E para frontend
- [ ] Documentación OpenAPI/Swagger
- [ ] Documentación completa en Markdown
- [ ] CI/CD pipeline configurado (GitHub Actions)
- [ ] Despliegue en staging validado
- [ ] Despliegue en producción
- [ ] Monitoreo y alertas configuradas

---

## Stack de Tecnología Confirmado

- **Backend**: Python 3.11, FastAPI, SQLAlchemy, Pydantic
- **Frontend**: React 18.2, TypeScript, Tailwind CSS, Zustand
- **Bases de datos**: PostgreSQL 15 (9 instancias)
- **Message Broker**: RabbitMQ 3.12
- **Cache**: Redis 7
- **Contenedores**: Docker, Docker Compose
- **Testing backend**: pytest, pytest-asyncio
- **Testing frontend**: Vitest, React Testing Library
- **Testing E2E**: Playwright
- **API docs**: FastAPI Swagger/OpenAPI
- **Deployment**: Docker Compose, Nginx, SSL/TLS
- **Monitoring**: Prometheus, Grafana (opcional)
- **Logging**: ELK Stack (opcional)

---

## Notas Importantes

⚠️ **Seguridad**:
- Cambiar JWT_SECRET_KEY en producción
- Usar HTTPS siempre
- Implementar CORS restrictivo
- Validar todas las entradas
- Usar variables de entorno para secretos

⚠️ **Performance**:
- Agregar índices en BD
- Cachear con Redis
- Implementar rate limiting
- Lazy load en frontend
- Comprimir assets

⚠️ **Escalabilidad**:
- Preparar para múltiples replicas de servicios
- Load balancing con Nginx o HAProxy
- Database connection pooling
- Queue workers escalables

