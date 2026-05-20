# Arquitectura de Microservicios - Sistema de Evaluación Automática de Código

## Estructura General

```
backend/
├── gateway/                    # API Gateway (FastAPI)
├── auth-service/              # Gestión de autenticación y JWT
├── user-service/              # Gestión de usuarios y perfiles
├── assignment-service/        # Gestión de tareas/asignaciones
├── submission-service/        # Gestión de envíos de código
├── execution-service/         # Ejecución de código en sandbox
├── grading-service/           # Calificación automática
├── plagiarism-service/        # Detección de plagio
├── audit-service/             # Auditoría de eventos
├── lms-integration-service/   # Integración con LMS
├── shared/                    # Librerías compartidas
└── docker-compose.yml         # Orquestación

frontend/
├── public/
├── src/
│   ├── components/            # Componentes reutilizables
│   ├── pages/                 # Páginas por rol
│   ├── hooks/                 # Custom hooks
│   ├── services/              # API clients
│   ├── layouts/               # Layouts
│   ├── stores/                # Estado global
│   └── config/                # Configuración
└── package.json
```

## Flujo de Eventos

```
1. submissionCreated
   ├─→ execution-service
   ├─→ audit-service

2. executionCompleted
   ├─→ grading-service
   ├─→ audit-service

3. gradingCompleted
   ├─→ plagiarism-service
   ├─→ audit-service

4. plagiarismAnalyzed
   └─→ audit-service

5. auditLog
   └─→ audit-service (central Hub)
```

## Base de Datos por Microservicio

| Servicio | Table | Responsabilidad |
|----------|-------|-----------------|
| auth-service | users, sessions, roles | Autenticación y autorización |
| user-service | user_profiles, user_roles | Perfiles y roles de usuarios |
| assignment-service | assignments, criteria | Tareas y criterios de evaluación |
| submission-service | submissions, submission_files | Envíos de código |
| execution-service | execution_logs, test_cases, execution_results | Logs y resultados de ejecución |
| grading-service | grades, grade_rubrics | Calificaciones y rúbricas |
| plagiarism-service | code_signatures, plagiarism_reports, plagiarism_matches | Detección de plagio |
| audit-service | audit_logs, event_logs | Auditoría central |
| lms-integration-service | lms_connections, sync_logs | Integración externa |

## Comunicación Inter-Servicios

- **REST + JWT**: Llamadas síncronas entre servicios
- **RabbitMQ Events**: Publicación de eventos asíncrona
- **Redis Cache**: Caché distribuido
- **API Gateway**: Punto de entrada único

## Seguridad

- JWT con RS256
- RBAC (Role-Based Access Control)
- Validación de entrada con Pydantic
- Sanitización de datos
- Sandbox para ejecución segura
