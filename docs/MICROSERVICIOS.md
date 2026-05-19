# Descripción Detallada de Microservicios
## Sistema de Evaluación Automática de Código

---

# 1. auth-service

## Propósito
Gestionar la identidad y el acceso al sistema, asegurando autenticación segura y autorización basada en roles.

## Responsabilidades
- Autenticación de usuarios mediante credenciales
- Emisión y validación de JWT (access + refresh)
- Gestión de permisos (RBAC)
- Integración con proveedores externos (LMS o SSO opcional)

## Casos de Uso
- Login de estudiante/profesor
- Validación de token en requests
- Renovación de sesiones

## Contratos principales

### Request
POST /auth/login

### Response
{
  "success": true,
  "data": {
    "accessToken": "...",
    "refreshToken": "...",
    "user": { ... }
  }
}

## Reglas de Negocio
- RN-AUTH-1: El token debe incluir rol y permisos
- RN-AUTH-2: Tokens deben expirar
- RN-AUTH-3: No exponer información sensible

## Decisiones Técnicas
- Stateless authentication (JWT)
- Separación total de lógica de identidad

---

# 2. user-service

## Propósito
Gestionar el ciclo de vida de los usuarios y su representación dentro del sistema.

## Responsabilidades
- CRUD de usuarios
- Gestión de perfiles
- Sincronización con LMS
- Gestión de roles

## Entidades
- User
- Role
- UserProfile

## Interacciones
- Consumido por auth-service
- Integrado con lms-integration-service

## Reglas de Negocio
- RN-USER-1: Todo usuario debe tener rol
- RN-USER-2: Datos deben ser consistentes con LMS

## Decisiones Técnicas
- Base de datos propia
- Sincronización eventual con LMS

---

# 3. assignment-service

## Propósito
Administrar las tareas académicas y definir las reglas de evaluación.

## Responsabilidades
- Crear y editar tareas
- Definir deadlines
- Configurar criterios de evaluación
- Asociar tareas a cursos

## Entidades
- Assignment
- EvaluationCriteria
- TestCase

## Casos de Uso
- Profesor crea tarea
- Profesor define criterios de evaluación
- Consulta de tareas por estudiante

## Reglas de Negocio
- RN-ASSIGN-1: Toda tarea debe tener deadline
- RN-ASSIGN-2: Debe existir al menos un criterio
- RN-ASSIGN-3: No modificar tareas activas sin control

## Decisiones Técnicas
- Versionado de criterios
- Preparado para múltiples lenguajes

---

# 4. submission-service

## Propósito
Gestionar el ingreso, versionado y validación de envíos de código.

## Responsabilidades
- Recepción de código fuente
- Control de múltiples intentos
- Validación de deadlines
- Persistencia de envíos
- Orquestación inicial del flujo

## Entidades
- Submission
- SubmissionFile
- Attempt

## Eventos Emitidos
- submissionCreated

## Flujo Interno
1. Validar usuario
2. Validar deadline
3. Registrar intento
4. Almacenar archivo
5. Emitir evento

## Reglas de Negocio
- RN-SUB-1: Rechazar envíos fuera del deadline
- RN-SUB-2: Permitir múltiples intentos
- RN-SUB-3: Cada intento es inmutable

## Decisiones Técnicas
- Separación entre metadata y archivos
- Uso de storage externo (S3 o similar)

---

# 5. execution-service

## Propósito
Ejecutar código de manera segura, aislada y controlada.

## Responsabilidades
- Compilar código
- Ejecutar código en sandbox
- Gestionar límites de ejecución
- Capturar salida (stdout/stderr)

## Características Críticas
- Entorno aislado (Docker / Firecracker)
- Sin acceso a red
- Timeout de ejecución
- Control de recursos

## Eventos Consumidos
- submissionCreated

## Eventos Emitidos
- executionCompleted

## Flujo Interno
1. Recibir evento
2. Preparar entorno (contenedor)
3. Ejecutar código
4. Capturar resultados
5. Destruir entorno
6. Emitir evento

## Reglas de Negocio
- RN-EXEC-1: Ejecución completamente aislada
- RN-EXEC-2: Limitar tiempo y recursos
- RN-EXEC-3: No persistir entorno

## Decisiones Técnicas
- Servicio completamente desacoplado
- Altamente escalable (workers)

---

# 6. grading-service

## Propósito
Evaluar automáticamente los resultados de ejecución y asignar una calificación.

## Responsabilidades
- Ejecutar test cases
- Validar outputs esperados
- Calcular score final
- Generar feedback

## Entidades
- GradingResult
- TestCaseResult

## Eventos Consumidos
- executionCompleted

## Eventos Emitidos
- gradingCompleted

## Reglas de Negocio
- RN-GRADE-1: Evaluación basada en criterios definidos
- RN-GRADE-2: Score debe ser reproducible
- RN-GRADE-3: Feedback obligatorio

## Decisiones Técnicas
- Determinismo en evaluación
- Separación de lógica de ejecución

---

# 7. plagiarism-service

## Propósito
Detectar similitud entre envíos para prevenir fraude académico.

## Responsabilidades
- Análisis de similitud interna
- Integración con servicios externos
- Generación de score de plagio

## Técnicas
- Tokenización
- Comparación estructural (AST)
- Hashing semántico

## Eventos Consumidos
- submissionCreated

## Eventos Emitidos
- plagiarismAnalyzed

## Reglas de Negocio
- RN-PLAG-1: Todo envío debe ser evaluado
- RN-PLAG-2: Resultados deben persistirse
- RN-PLAG-3: Soporte a integración externa

## Decisiones Técnicas
- Procesamiento asíncrono
- Escalado independiente

---

# 8. audit-service

## Propósito
Proveer trazabilidad completa del sistema para cumplimiento regulatorio.

## Responsabilidades
- Registro de eventos del sistema
- Almacenamiento inmutable
- Consulta histórica

## Entidades
- EventStore
- AuditLog

## Eventos Consumidos
- submissionCreated
- executionCompleted
- gradingCompleted
- plagiarismAnalyzed

## Reglas de Negocio
- RN-AUDIT-1: No modificar eventos
- RN-AUDIT-2: Registrar todos los eventos críticos

## Decisiones Técnicas
- Event sourcing parcial
- Append-only storage

---

# 9. lms-integration-service

## Propósito
Actuar como capa de adaptación entre el sistema interno y el LMS legacy.

## Responsabilidades
- Sincronización de usuarios
- Sincronización de cursos
- Envío de calificaciones
- Transformación de datos

## Patrón Aplicado
Anti-Corruption Layer

## Reglas de Negocio
- RN-LMS-1: No acoplar modelo interno
- RN-LMS-2: Manejo de fallos en integración

## Decisiones Técnicas
- Adaptadores específicos
- Retries y resiliencia

---

# 10. communication-service (Opcional)

## Propósito
Gestionar notificaciones hacia los usuarios.

## Responsabilidades
- Envío de emails
- Notificaciones de resultados
- Alertas académicas

---

# 11. Flujo Global del Sistema

1. submission-service recibe envío  
2. Emite submissionCreated  
3. execution-service ejecuta código  
4. grading-service evalúa resultados  
5. plagiarism-service analiza similitud  
6. audit-service registra todo  

---

# 12. Principios de Diseño Aplicados

- Single Responsibility por servicio
- Bajo acoplamiento entre servicios
- Alta cohesión interna
- Comunicación basada en eventos
- Escalabilidad horizontal
- Tolerancia a fallos

---

# 13. Conclusión

La arquitectura de microservicios está diseñada para:

- Escalar con alta carga académica
- Proveer seguridad en ejecución de código
- Garantizar auditoría completa
- Integrarse con sistemas legacy
- Permitir evolución modular del sistema