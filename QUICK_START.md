# 🚀 GUÍA DE INICIO RÁPIDO

## Prerequisitos

- Docker 20.10+
- Docker Compose 2.0+
- Git

## Instalación y Ejecución

### 1. Clonar el Repositorio

```bash
cd Tercer-Hackaton
```

### 2. Copiar variables de entorno

```bash
cp .env.example .env
```

### 3. Iniciar todos los servicios con Docker Compose

```bash
cd backend
docker-compose up -d
```

Esto levantará:
- **Bases de Datos**: 9 instancias PostgreSQL independientes
- **Message Broker**: RabbitMQ (puerto 15672 para admin)
- **Cache**: Redis
- **Microservicios**: 9 servicios FastAPI
- **API Gateway**: Puerta de entrada centralizada

### 4. Verificar que los servicios estén corriendo

```bash
# Revisar logs
docker-compose logs -f

# Verificar health check del gateway
curl http://localhost:8000/health
```

### 5. Iniciar Frontend

```bash
cd ../frontend
npm install
npm run dev
```

El frontend estará disponible en `http://localhost:5173`

## 📊 URLs de Acceso

| Componente | URL | Credenciales |
|-----------|-----|-------------|
| **Frontend** | http://localhost:5173 | - |
| **API Gateway** | http://localhost:8000 | - |
| **RabbitMQ Admin** | http://localhost:15672 | guest / guest |
| **Auth Service** | http://localhost:8001 | - |
| **User Service** | http://localhost:8004 | - |
| **Assignment Service** | http://localhost:8005 | - |
| **Submission Service** | http://localhost:8002 | - |
| **Execution Service** | http://localhost:8003 | - |
| **Grading Service** | http://localhost:8006 | - |
| **Plagiarism Service** | http://localhost:8009 | - |
| **Audit Service** | http://localhost:8007 | - |
| **LMS Service** | http://localhost:8008 | - |

## 📝 Flujo Completo de Ejemplo

### 1. Registro de Usuario

```bash
POST http://localhost:8000/api/v1/auth/register
{
  "email": "estudiante@example.com",
  "password": "password123",
  "full_name": "Juan Pérez"
}
```

### 2. Login

```bash
POST http://localhost:8000/api/v1/auth/login
{
  "email": "estudiante@example.com",
  "password": "password123"
}

# Respuesta:
{
  "token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": 1,
    "email": "estudiante@example.com",
    "role": "student"
  }
}
```

### 3. Crear Tarea (Como Profesor)

```bash
POST http://localhost:8000/api/v1/assignments
Headers: Authorization: Bearer {token}
{
  "course_id": 1,
  "title": "Tarea 1: Calculadora",
  "description": "Implementar una calculadora básica en Python",
  "type": "coding",
  "due_date": "2024-06-30",
  "max_score": 100,
  "allow_multiple_submissions": true,
  "instructions": "Implementar las operaciones básicas: suma, resta, multiplicación y división"
}
```

### 4. Enviar Código (Como Estudiante)

```bash
POST http://localhost:8000/api/v1/submissions
Headers: Authorization: Bearer {token}
{
  "assignment_id": 1,
  "code": "def add(a, b): return a + b\n...",
  "language": "python"
}

# Evento generado: submissionCreated
```

### 5. Ejecutar Código (Automático)

- El submission service emite evento `submissionCreated`
- Execution service recibe el evento y ejecuta el código en sandbox
- Emite evento `executionCompleted`

```bash
# Resultado:
{
  "submission_id": 1,
  "execution_status": "success",
  "output": "...",
  "errors": "",
  "execution_time_ms": 125
}
```

### 6. Calificar (Automático)

- Grading service recibe evento `executionCompleted`
- Compara con test cases y genera calificación
- Emite evento `gradingCompleted`

```bash
{
  "submission_id": 1,
  "grade": 95,
  "feedback": "Excelente implementación"
}
```

### 7. Detectar Plagio (Automático)

- Plagiarism service recibe evento `submissionCreated`
- Analiza código contra base de datos de envíos anteriores
- Emite evento `plagiarismAnalyzed`

```bash
{
  "submission_id": 1,
  "plagiarism_percentage": 5,
  "status": "passed"
}
```

### 8. Registrar Auditoría (Automático)

- Audit service registra todos los eventos para trazabilidad

```bash
GET http://localhost:8000/api/v1/audit/logs
```

## 🗄️ Bases de Datos

Cada microservicio tiene su propia base de datos PostgreSQL:

- **auth_db** (5401): Usuarios y tokens
- **user_db** (5402): Perfiles de usuario
- **assignment_db** (5403): Tareas y criterios
- **submission_db** (5404): Envíos de código
- **execution_db** (5405): Resultados de ejecución
- **grading_db** (5406): Calificaciones
- **plagiarism_db** (5407): Análisis de plagio
- **audit_db** (5408): Logs de auditoría
- **lms_integration_db** (5409): Configuraciones LMS

## 🔄 Arquitectura de Eventos

```
Submission → Execution → Grading → Plagiarism → Audit
    ↓            ↓           ↓          ↓           ↓
(Enviado)  (Ejecutado)  (Calificado) (Analizado) (Registrado)
```

Todos los microservicios escuchan eventos via **RabbitMQ** y se comunican de forma desacoplada.

## 📋 Requisitos Técnicos Cumplidos

✅ Arquitectura de microservicios  
✅ Base de datos por servicio  
✅ Event-driven architecture  
✅ FastAPI (Python asíncrono)  
✅ Pydantic para validación  
✅ JWT Authentication  
✅ API Gateway centralizado  
✅ RBAC (Roles)  
✅ Manejo de errores consistente  
✅ Docker Compose completo  
✅ Frontend React + Tailwind  
✅ Componentes modulares  
✅ Principios SOLID  
✅ Bajo acoplamiento  
✅ DDD (Domain Driven Design)  

## ⚠️ Notas Importantes

1. **Cambiar JWT Secret**: Modificar la variable `JWT_SECRET_KEY` en `.env` para producción
2. **Credenciales**: Las credenciales de base de datos en `docker-compose.yml` son de demo
3. **LMS Integration**: Configurar `LMS_API_KEY` y `LMS_BASE_URL` antes de usar
4. **Rate Limiting**: API Gateway incluye rate limiting (100 req/60seg)

## 🧹 Limpiar Contenedores

```bash
cd backend
docker-compose down -v  # -v elimina volúmenes
```

## 📞 Soporte

Para más información, revisar:
- [ARQUITECTURA.md](docs/ARQUITECTURA.md)
- [INSTALACION.md](INSTALLATION_GUIDE.md)
- [ARCHITECTURE.md](ARQUITECTURA_MICROSERVICIOS.md)
