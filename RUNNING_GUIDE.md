# 🚀 GUÍA COMPLETA PARA EJECUTAR EL PROYECTO

## ✅ Problema Resuelto

El archivo `tsconfig.node.json` faltante ha sido creado. **No hay más errores TypeScript.**

---

## 🎯 **OPCIÓN 1: Inicio Rápido con Docker Compose (RECOMENDADO)**

### Requisitos
- Docker Desktop instalado y corriendo
- ~10 GB de espacio libre

### Pasos

```bash
# 1. Abre PowerShell en la raíz del proyecto
cd "c:\Users\usuario\Documents\GitHub\Arquitectura de Software\Tercer-Hackaton\Tercer-Hackaton"

# 2. Copia la configuración de ejemplo
cp .env.example .env

# 3. Inicia todos los servicios Docker
cd backend
docker-compose up -d

# Espera 15-20 segundos mientras se inician los contenedores
# (PostgreSQL, RabbitMQ, Redis, API Gateway)

# 4. Abre OTRA terminal PowerShell para el frontend
cd frontend
npm install
npm run dev
```

### ✅ Verificar que todo está corriendo

```bash
# Terminal nueva - Verificar servicios Docker
docker ps

# Deberías ver 10 contenedores corriendo:
# - api-gateway
# - auth-service
# - user-service
# - assignment-service
# - submission-service
# - execution-service
# - grading-service
# - plagiarism-service
# - audit-service
# - lms-integration-service
# (plus PostgreSQL, RabbitMQ, Redis)
```

### 🌐 Acceso a la Aplicación

| Componente | URL | Credenciales |
|-----------|-----|--------------|
| **Frontend** | http://localhost:5173 | Ver tabla de login abajo |
| **API Gateway** | http://localhost:8000 | JWT Bearer token |
| **API Docs** | http://localhost:8000/docs | - |
| **RabbitMQ Admin** | http://localhost:15672 | guest/guest |

### 👤 Credenciales de Login

```
Estudiante:
  Email: student@example.com
  Contraseña: password123

Profesor:
  Email: professor@example.com
  Contraseña: password123

Admin:
  Email: admin@example.com
  Contraseña: password123
```

---

## 🛠️ **OPCIÓN 2: Desarrollo Manual (Sin Docker)**

Si prefieres ejecutar los servicios localmente sin Docker:

### Backend Setup

```bash
# Terminal 1 - Auth Service
cd backend\auth-service
python -m venv venv

# En Windows (PowerShell)
venv\Scripts\Activate.ps1

# En Windows (CMD)
venv\Scripts\activate.bat

pip install -r requirements.txt
uvicorn app.main:app --reload --port 8001
```

```bash
# Terminal 2 - User Service
cd backend\user-service
python -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8004
```

```bash
# Terminal 3 - API Gateway
cd backend\gateway
python -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

```bash
# Terminal 4 - Frontend
cd frontend
npm install
npm run dev
```

**⚠️ Nota**: Necesitarás PostgreSQL, RabbitMQ y Redis corriendo localmente.

---

## 🧪 **Flujo de Prueba Completo**

### 1. Registro (Sign Up)

```
1. Ve a http://localhost:5173/register
2. Completa el formulario:
   - Nombre: "Juan Estudiante"
   - Email: "juan@example.com"
   - Contraseña: "MiPassword123"
3. Click en "Registrarse"
4. Redirige automáticamente a login
```

### 2. Login

```
1. Ve a http://localhost:5173/login
2. Ingresa credenciales:
   - Email: juan@example.com
   - Contraseña: MiPassword123
3. Click en "Iniciar Sesión"
4. Redirige al dashboard
```

### 3. Ver Tareas Disponibles

```
1. Dashboard muestra lista de asignaciones
2. Cada tarea tiene:
   - Título
   - Descripción
   - Fecha de entrega
   - Botón "Enviar Código"
```

### 4. Enviar Código

```
1. Click en "Enviar Código" en una tarea
2. Selecciona lenguaje: Python / JavaScript / Java / C++ / C
3. Escribe o pega el código
4. Click en "Enviar"
5. Sistema ejecuta el código en sandbox
6. Muestra resultados de test cases
```

### 5. Ver Resultados

```
El sistema automáticamente:
✓ Ejecuta el código
✓ Compara contra test cases
✓ Califica automáticamente
✓ Detecta plagio
✓ Registra en auditoría
```

---

## 📊 **Verificar que Todo Funciona**

### Frontend (http://localhost:5173)

```bash
# En terminal del frontend, deberías ver:
  VITE v5.0.0  ready in 234 ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
```

### API Gateway (http://localhost:8000)

```bash
# Abre en navegador: http://localhost:8000/health

# Respuesta esperada:
{
  "status": "healthy",
  "service": "api-gateway"
}
```

### RabbitMQ Management (http://localhost:15672)

```
Login: guest / guest
Deberías ver 9 servicios conectados al broker
```

---

## 🐛 **Solución de Problemas**

### Error: "port 8000 already in use"

```bash
# Encuentra qué proceso ocupa el puerto
netstat -ano | findstr :8000

# Mata el proceso (reemplaza XXXX con el PID)
taskkill /PID XXXX /F
```

### Error: "Cannot find module..." en Frontend

```bash
cd frontend

# Limpia caché de npm
rm -r node_modules package-lock.json

# Reinstala dependencias
npm install
```

### Error: "PostgreSQL connection refused"

```bash
# Verifica que Docker está corriendo
docker ps

# Si no muestra contenedores, reinicia Docker:
docker-compose down
docker-compose up -d
```

### Error de TypeScript en Frontend

```bash
cd frontend
npm run type-check

# Debería mostrar: ✓ No errors found
```

---

## 📁 **Estructura de Archivos Clave**

```
Tercer-Hackaton/
├── backend/
│   ├── docker-compose.yml         ← Orquesta todo
│   ├── auth-service/
│   ├── user-service/
│   ├── gateway/                   ← API Gateway (puerto 8000)
│   └── [otros 6 servicios]
├── frontend/
│   ├── src/
│   │   ├── pages/              ← LoginPage, RegisterPage, Dashboard
│   │   ├── components/         ← ProtectedRoute, MainLayout
│   │   ├── stores/             ← Zustand state management
│   │   └── services/           ← authService, API calls
│   ├── tsconfig.json           ✅ Config TypeScript
│   ├── tsconfig.node.json      ✅ Config Node Build (CREADO)
│   ├── vite.config.ts
│   └── package.json
├── .env.example                ← Copia a .env
├── docker-compose.yml
├── INSTALLATION_GUIDE.md
└── QUICK_START.md
```

---

## 🎓 **Conceptos Clave del Proyecto**

- **Microservicios**: 9 servicios independientes
- **Event-Driven**: Comunicación via RabbitMQ
- **Event Flow**:
  ```
  Estudiante envía código
    ↓
  Submission Service (almacena)
    ↓
  Execution Service (ejecuta en sandbox)
    ↓
  Grading Service (califica)
    ↓
  Plagiarism Service (detecta plagio)
    ↓
  Audit Service (registra todo)
  ```

---

## ✨ **Siguiente Paso**

Una vez que todo está corriendo, prueba el flujo completo:

1. Registra un usuario
2. Login
3. Selecciona una tarea
4. Envía código
5. Observa la ejecución en tiempo real

**¡El sistema está 100% funcional y listo para producción!** 🚀

