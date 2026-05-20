# ⚡ INICIO RÁPIDO - 30 SEGUNDOS

## Comando Único para Iniciar TODO

```bash
# OPCIÓN 1: Con Docker (RECOMENDADO - Una sola terminal)
cd backend && docker-compose up -d && cd ../frontend && npm install && npm run dev

# LUEGO ABRE EN NAVEGADOR: http://localhost:5173
```

## Credenciales para Login

```
Email: student@example.com
Contraseña: password123
```

## URLs de Acceso

| Componente | URL |
|-----------|-----|
| 🌐 Frontend | http://localhost:5173 |
| 🔌 API Gateway | http://localhost:8000 |
| 📚 API Docs | http://localhost:8000/docs |
| 📧 RabbitMQ | http://localhost:15672 (guest/guest) |
| 💾 PostgreSQL | localhost:5401-5409 |

## ¿Problema?

✅ **El error de TypeScript ya fue solucionado** - Se creó `tsconfig.node.json`

👉 **Para guía completa**: Ver [RUNNING_GUIDE.md](RUNNING_GUIDE.md)

## Parar Todo

```bash
cd backend && docker-compose down
```

---

**¡Listo! El proyecto está 100% funcional.** ✨
