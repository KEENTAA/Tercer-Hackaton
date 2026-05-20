# Sistema de Evaluación Automática de Código

Un sistema completo basado en **microservicios** para evaluar automáticamente código de estudiantes, calificar basado en test cases, y detectar plagio.

## 🚀 Características Principales

- ✅ **Autenticación centralizada** con JWT
- ✅ **Evaluación automática** de código en sandbox seguro
- ✅ **Calificación automática** basada en test cases
- ✅ **Detección de plagio** con análisis de similitud
- ✅ **Auditoría completa** de todas las acciones
- ✅ **Event-driven architecture** con RabbitMQ
- ✅ **Escalable** con 9 microservicios independientes
- ✅ **Frontend React** con dashboards para estudiantes y profesores
- ✅ **Dockerizado** y listo para producción

## 📋 Stack Tecnológico

### Backend
- **Framework**: FastAPI 0.104.1
- **Lenguaje**: Python 3.11
- **ORM**: SQLAlchemy 2.0.23
- **Validación**: Pydantic 2.5.0
- **Base de datos**: PostgreSQL 15
- **Message Broker**: RabbitMQ 3.12
- **Cache**: Redis 7
- **Autenticación**: JWT (HS256)

### Frontend
- **Framework**: React 18.2.0
- **Lenguaje**: TypeScript
- **Estilos**: Tailwind CSS 3.3.0
- **Enrutador**: React Router v6
- **Estado**: Zustand 4.4.0
- **HTTP Client**: Axios 1.6.0
- **Build**: Vite 5.0.0

### Infraestructura
- **Contenedores**: Docker + Docker Compose
- **Orquestación**: Docker Compose
- **Proxy inverso**: Nginx
- **CI/CD**: GitHub Actions (opcional)

## 📁 Estructura del Proyecto

```
.
├── backend/                          # Microservicios backend
│   ├── auth-service/                 # ✅ Autenticación y JWT
│   ├── submission-service/           # ✅ Gestión de envíos
│   ├── execution-service/            # ✅ Ejecución de código
│   ├── grading-service/              # ✅ Calificación automática
│   ├── plagiarism-service/           # ✅ Detección de plagio
│   ├── user-service/                 # 📋 Perfil de usuario
│   ├── assignment-service/           # 📋 Gestión de tareas
│   ├── audit-service/                # 📋 Auditoría de eventos
│   ├── lms-service/                  # 📋 Integración LMS
│   ├── api-gateway/                  # 📋 Gateway centralizado
│   └── shared/                       # Módulos compartidos
│
├── frontend/                         # ✅ Aplicación React
│   ├── src/
│   │   ├── pages/                   # Vistas principales
│   │   ├── components/              # Componentes reutilizables
│   │   ├── stores/                  # Estado con Zustand
│   │   ├── services/                # Clientes API
│   │   ├── config/                  # Configuración
│   │   └── styles/                  # Estilos Tailwind
│   └── public/                      # Assets estáticos
│
├── docker-compose.yml               # 👈 Iniciar desarrollo
├── docker-compose.prod.yml          # 👈 Producción
├── docs/                            # Documentación
│   ├── ARQUITECTURA.md
│   ├── MICROSERVICIOS.md
│   ├── EVENT_DRIVEN_ARCHITECTURE.md
│   ├── INSTALLATION_GUIDE.md
│   ├── DEPLOYMENT_GUIDE.md
│   └── NEXT_STEPS.md
└── .env.example                     # 👈 Copiar a .env

✅ = Completado
📋 = En desarrollo
```

## 🏗️ Arquitectura

### Componentes Principales

```
┌─────────────────────────────────────────────────────┐
│                    Frontend React                   │
│         (Dashboard Estudiante/Profesor)             │
└─────────────────────┬───────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────┐
│              API Gateway (Port 8000)                │
│        (Enrutamiento, Auth, Rate Limiting)          │
└──┬──┬──┬──┬──┬──┬──┬──┬──┬─────────────────────────┘
   │  │  │  │  │  │  │  │  │
   ▼  ▼  ▼  ▼  ▼  ▼  ▼  ▼  ▼
┌─────────────────────────────────────────────────────┐
│           Microservicios (8001-8009)                │
│ ┌──────────┐ ┌──────────┐ ┌──────────┐             │
│ │   Auth   │ │ Submission│ │Execution│             │
│ │(8001)    │ │ (8004)   │ │ (8005)  │             │
│ └──────────┘ └──────────┘ └──────────┘             │
│ ┌──────────┐ ┌──────────┐ ┌──────────┐             │
│ │ Grading  │ │Plagiarism│ │  Audit   │             │
│ │ (8006)   │ │ (8007)   │ │ (8008)  │             │
│ └──────────┘ └──────────┘ └──────────┘             │
└─────────────────────────────────────────────────────┘
                      │
        ┌─────────────┼─────────────┐
        ▼             ▼             ▼
    ┌────────┐   ┌────────┐   ┌────────┐
    │9 x DB │   │RabbitMQ│   │ Redis  │
    │(SQL)  │   │(Events)│   │(Cache) │
    └────────┘   └────────┘   └────────┘
```

### Flujo de Eventos

```
1. Estudiante envía código
   ↓
2. Submission Service publica: submission.submissionCreated
   ↓
3. Execution Service consume → ejecuta tests
   ├→ Publica: execution.executionCompleted
   │
4. Grading Service consume → califica
   ├→ Publica: grading.gradingCompleted
   │
5. Plagiarism Service consume → detecta similitudes
   ├→ Publica: plagiarism.plagiarismAnalyzed
   │
6. Audit Service consume TODOS → registra auditoría
   │
7. ✅ Envío COMPLETAMENTE PROCESADO
```

## 🚀 Quick Start

### Requisitos Previos

- Docker y Docker Compose
- (Opcional) Python 3.11+ para desarrollo local
- (Opcional) Node.js 18+ para frontend local

### Opción 1: Con Docker (Recomendado)

```bash
# 1. Clonar repositorio
git clone <repo-url>
cd Tercer-Hackaton

# 2. Copiar variables de entorno
cp .env.example .env

# 3. Iniciar servicios
docker-compose up -d

# 4. Verificar que está corriendo
docker-compose ps

# 5. Acceder a la aplicación
# Frontend: http://localhost:3000
# Swagger API: http://localhost:8001/docs
# RabbitMQ UI: http://localhost:15672 (guest/guest)
```

### Opción 2: Desarrollo Local

```bash
# Backend
cd backend/auth-service
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8001

# Frontend (en otra terminal)
cd frontend
npm install
npm run dev
```

## 📖 Documentación

| Documento | Descripción |
|-----------|-------------|
| [ARQUITECTURA.md](docs/ARQUITECTURA.md) | Diseño general del sistema |
| [EVENT_DRIVEN_ARCHITECTURE.md](EVENT_DRIVEN_ARCHITECTURE.md) | Explicación eventos y RabbitMQ |
| [INSTALLATION_GUIDE.md](INSTALLATION_GUIDE.md) | Instalación y ejecución |
| [NEXT_STEPS.md](NEXT_STEPS.md) | Roadmap y próximas implementaciones |
| [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) | Despliegue en producción |

## 🔌 API Endpoints Principales

### Auth Service (8001)
```bash
POST   /api/auth/register          # Registrar usuario
POST   /api/auth/login             # Iniciar sesión
POST   /api/auth/refresh           # Refrescar token
POST   /api/auth/logout            # Cerrar sesión
GET    /api/auth/me                # Usuario actual
```

### Submission Service (8004)
```bash
POST   /api/submissions/           # Enviar código
GET    /api/submissions/{id}       # Obtener envío
GET    /api/submissions/history/{assignment_id}  # Historial
```

### Grading Service (8006)
```bash
GET    /api/grades/{submission_id}  # Obtener calificación
POST   /api/grades/                 # Crear calificación
```

### Plagiarism Service (8007)
```bash
GET    /api/plagiarism/{submission_id}  # Reporte de plagio
GET    /api/plagiarism/{assignment_id}/analysis  # Análisis general
```

## 🔐 Seguridad

- ✅ Contraseñas hasheadas con bcrypt
- ✅ JWT tokens con expiración configurable
- ✅ CORS configurado
- ✅ Rate limiting
- ✅ Validación con Pydantic
- ✅ Sandbox para ejecución de código
- ✅ Auditoría completa de acciones

## 📊 Monitoreo

### RabbitMQ Management UI
```
URL: http://localhost:15672
Usuario: guest
Contraseña: guest
```

### Logs
```bash
# Ver logs de un servicio
docker-compose logs -f auth-service

# Ver logs de todos
docker-compose logs -f
```

### Health Checks
```bash
curl http://localhost:8001/health
curl http://localhost:8004/health
curl http://localhost:8006/health
```

## 🧪 Testing

```bash
# Backend - Tests unitarios
pytest backend/

# Frontend - Tests
npm test

# Frontend - E2E
npm run test:e2e
```

## 📈 Escalado

El sistema está diseñado para escalar horizontalmente:

```yaml
# Múltiples instancias de servicios
services:
  auth-service-1:
    image: auth-service:latest
    ports:
      - "8001:8001"
  
  auth-service-2:
    image: auth-service:latest
    ports:
      - "8011:8001"
  
  # Load balancer distribuye tráfico
  load-balancer:
    image: nginx:latest
    ports:
      - "8000:80"
```

## 🐛 Troubleshooting

### Error: "Port already in use"
```bash
lsof -i :8001  # Encontrar proceso
kill -9 <PID>  # Matar proceso
```

### Error: "Connection refused"
```bash
docker-compose ps              # Verificar servicios corriendo
docker-compose logs servicename # Ver logs
docker-compose restart servicename  # Reiniciar
```

### Error: "Database connection failed"
```bash
docker-compose exec auth-db psql -U postgres -d auth_db
```

Ver más en [TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)

## 🚀 Próximos Pasos

1. **User Service** - Gestión de perfiles
2. **Assignment Service** - Gestión de tareas
3. **Audit Service** - Registro de eventos
4. **API Gateway** - Central de enrutamiento
5. **Frontend Expansions** - Dashboards completos
6. **CI/CD** - GitHub Actions
7. **Monitoring** - Prometheus + Grafana

Ver [NEXT_STEPS.md](NEXT_STEPS.md) para detalles completos.

## 📄 Licencia

Este proyecto está bajo la licencia MIT.

## 👥 Contribuidores

- [@Andres](https://github.com/andres) - Arquitectura y Backend

## 📞 Soporte

Para preguntas o problemas:
1. Revisar documentación en `/docs`
2. Buscar en [Issues](issues/)
3. Abrir nuevo Issue con detalles

---

**Última actualización**: Mayo 2024
**Versión**: 1.0.0-beta
**Estado**: En desarrollo 🚧
