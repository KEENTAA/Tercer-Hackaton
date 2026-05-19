# Arquitectura Completa del Sistema
## Plataforma de Evaluación Automática de Código

---

# 1. Resumen Ejecutivo

Se propone el diseño de una plataforma escalable para una universidad que permite:

- Subida de código fuente por estudiantes  
- Ejecución automática y calificación  
- Detección de plagio  
- Auditoría completa de resultados  
- Integración con sistema LMS legado  

El sistema está diseñado para soportar alta concurrencia (30.000+ estudiantes), garantizar trazabilidad completa y permitir escalabilidad horizontal.

---

# 2. Principios Arquitectónicos

- Separación por dominios (DDD)
- Bajo acoplamiento
- Alta cohesión
- Principios SOLID
- Event-Driven Architecture (EDA)
- Procesamiento asíncrono
- Auditoría inmutable
- Seguridad en ejecución (sandbox)

---

# 3. Estilo Arquitectónico

Microservicios + Arquitectura Orientada a Eventos + Workers Asíncronos

---

# 4. Visión General del Sistema

Frontend (React + Tailwind)
        |
    API Gateway
        |
-----------------------------------------------------
| auth | users | assignments | submissions | grading |
| plagiarism | audit | lms-integration             |
-----------------------------------------------------
        |
    Message Broker (Kafka / RabbitMQ)
        |
    Workers:
      - execution
      - plagiarism

---

# 5. Bounded Contexts (DDD)

## 5.1 Identity & Access
- Autenticación
- Autorización
- Roles

## 5.2 Academic Management
- Cursos
- Tareas
- Criterios

## 5.3 Submission Management
- Envíos
- Intentos
- Versionado

## 5.4 Execution Engine
- Ejecución de código
- Sandbox seguro

## 5.5 Grading Engine
- Evaluación
- Cálculo de score

## 5.6 Plagiarism Detection
- Comparación interna
- Integración externa

## 5.7 Audit & Compliance
- Historial
- Auditoría

## 5.8 LMS Integration
- Adaptador a sistema legacy

---

# 6. Microservicios

## 6.1 auth-service
- Login
- JWT
- Roles

## 6.2 user-service
- Gestión de usuarios
- Sincronización LMS

## 6.3 assignment-service
- Creación de tareas
- Fechas límite
- Criterios de evaluación

## 6.4 submission-service
- Recepción de código
- Validaciones
- Intentos

## 6.5 execution-service
- Ejecución en sandbox
- Control de recursos

## 6.6 grading-service
- Evaluación automática
- Nota final

## 6.7 plagiarism-service
- Análisis interno
- Integración Turnitin

## 6.8 audit-service
- Registro de eventos
- Logs históricos

## 6.9 lms-integration-service
- Adaptador al mainframe
- Sincronización

---

# 7. Arquitectura Interna de un Microservicio

module/
├── controllers/
├── services/
├── repositories/
├── domain/
├── schemas/
├── infrastructure/

---

# 8. Flujo Principal

## Flujo: Envío de código

1. Estudiante envía código
2. submission-service valida deadline
3. Guarda en base de datos
4. Emite evento submissionCreated
5. execution-service ejecuta código
6. Emite executionCompleted
7. grading-service calcula nota
8. plagiarism-service analiza
9. audit-service registra eventos
10. Resultado disponible

---

# 9. Eventos del Sistema

- submissionCreated
- executionCompleted
- gradingCompleted
- plagiarismAnalyzed
- gradeFinalized

---

# 10. Modelo de Datos

## users
- id
- email
- role

## assignments
- id
- title
- deadline

## submissions
- id
- userId
- assignmentId
- attemptNumber

## execution_results
- id
- submissionId
- output
- status

## grading_results
- id
- score
- feedback

## plagiarism_results
- id
- similarityScore

## audit_logs
- id
- eventType
- timestamp

---

# 11. Reglas de Negocio

- RN1: No aceptar envíos fuera del deadline
- RN2: Permitir múltiples intentos
- RN3: Persistir todos los envíos
- RN4: Registrar todas las ejecuciones
- RN5: Evaluar según criterios definidos
- RN6: Detectar plagio en cada envío
- RN7: Auditoría obligatoria

---

# 12. Pruebas de Aceptación

- PA1: Envío antes del deadline → aceptado
- PA2: Envío fuera de tiempo → rechazado
- PA3: Múltiples intentos → permitidos
- PA4: Resultado persistido
- PA5: Plagio detectado
- PA6: LMS sincronizado
- PA7: Auditoría disponible

---

# 13. Seguridad

## Ejecución de código
- Contenedores Docker aislados
- Sin acceso a red
- Límites:
  - CPU
  - Memoria
  - Tiempo

## Autenticación
- JWT
- RBAC

---

# 14. Persistencia

- PostgreSQL
- Base de datos por microservicio
- Consistencia eventual

---

# 15. Integración LMS

Patrón:
Anti-Corruption Layer

- Traduce modelos internos
- Evita dependencia del legacy

---

# 16. Escalabilidad

- Escalado horizontal
- Workers distribuidos
- Colas de procesamiento
- Servicios stateless

---

# 17. Auditoría

- Event sourcing (parcial)
- Logs inmutables

Eventos:
- submissionCreated
- executionCompleted
- gradeAssigned

---

# 18. Frontend

## Tecnologías
- React
- Tailwind CSS

## Estructura

src/
├── components/
├── hooks/
├── services/
├── pages/

## Componentes

- StudentDashboard
- SubmissionForm
- ResultsViewer
- TeacherPanel

---

# 19. Tecnologías

## Backend
- FastAPI (async)
- Pydantic
- JWT

## Infraestructura
- Docker
- Kafka / RabbitMQ

## Base de datos
- PostgreSQL

## Frontend
- React + Tailwind

---

# 20. Riesgos y Mitigación

| Riesgo | Mitigación |
|-------|----------|
| Código malicioso | Sandbox |
| Alta carga | Workers + colas |
| LMS legacy | Adaptador |
| Plagio costoso | Async |

---

# 21. Roadmap

## Fase 1
- Monolito modular

## Fase 2
- Separar execution-service

## Fase 3
- Event-driven completo

---

# 22. Conclusión

La arquitectura es:

- Escalable
- Segura
- Auditada
- Desacoplada

Cumple todos los requisitos del sistema académico.

---

# 23. Justificación

Se eligió esta arquitectura porque:

- Soporta alta concurrencia
- Permite ejecución segura
- Facilita auditoría
- Integra sistemas legacy
- Escala horizontalmente
``