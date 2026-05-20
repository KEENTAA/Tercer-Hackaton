# GUÍA DE DESPLIEGUE EN PRODUCCIÓN

## 1. Requisitos

- Docker y Docker Compose instalados
- Servidor con al menos 4GB RAM
- Dominio configurado (para HTTPS)
- Certificado SSL/TLS

## 2. Preparación del Servidor

### 2.1 Actualizar el servidor

```bash
sudo apt-get update
sudo apt-get upgrade -y
sudo apt-get install -y docker.io docker-compose git
sudo systemctl enable docker
```

### 2.2 Clonar el repositorio

```bash
git clone <repo-url> /opt/codigo-evaluacion
cd /opt/codigo-evaluacion
```

### 2.3 Crear archivo .env para producción

```bash
# .env.production
ENVIRONMENT=production
DEBUG=false

# Database
DB_PASSWORD=GenerarContraseñaSegura123!
DB_HOST=postgres
DB_PORT=5432

# JWT
JWT_SECRET_KEY=GenerarClaveJWTSegura_MinimumCharacters32
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=60
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# RabbitMQ
RABBITMQ_USER=amqp_user
RABBITMQ_PASSWORD=GenerarContraseñaRabbitMQ123!

# Redis
REDIS_PASSWORD=GenerarContraseñaRedis123!

# Frontend
REACT_APP_API_URL=https://api.tudominio.com

# Execution Service
EXECUTION_TIMEOUT_SECONDS=30
SANDBOX_ENABLED=true

# Plagiarism
PLAGIARISM_THRESHOLD=0.75

# CORS
CORS_ORIGINS=https://tudominio.com,https://www.tudominio.com

# Email
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=tu-email@gmail.com
SMTP_PASSWORD=tu-app-password
```

## 3. Configuración de Seguridad

### 3.1 Firewall

```bash
sudo ufw enable
sudo ufw allow 22/tcp      # SSH
sudo ufw allow 80/tcp      # HTTP
sudo ufw allow 443/tcp     # HTTPS
sudo ufw allow 5672/tcp    # RabbitMQ (solo desde red interna)
```

### 3.2 Certificado SSL con Let's Encrypt

```bash
sudo apt-get install -y certbot python3-certbot-nginx
sudo certbot certonly --standalone -d tudominio.com -d www.tudominio.com
```

### 3.3 Configurar Nginx como Reverse Proxy

```bash
sudo apt-get install -y nginx

# Crear archivo de configuración
sudo nano /etc/nginx/sites-available/codigo-evaluacion
```

```nginx
upstream backend {
    server localhost:8000;
}

upstream frontend {
    server localhost:3000;
}

# Redirigir HTTP a HTTPS
server {
    listen 80;
    server_name tudominio.com www.tudominio.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name tudominio.com www.tudominio.com;

    ssl_certificate /etc/letsencrypt/live/tudominio.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/tudominio.com/privkey.pem;

    # SSL configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    # API Gateway
    location /api/ {
        proxy_pass http://backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }

    # Frontend
    location / {
        proxy_pass http://frontend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }

    # Compression
    gzip on;
    gzip_types text/plain text/css application/json application/javascript;
    gzip_min_length 1024;
}
```

```bash
# Habilitar configuración
sudo ln -s /etc/nginx/sites-available/codigo-evaluacion /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## 4. Despliegue con Docker Compose

### 4.1 Actualizar docker-compose.prod.yml

```yaml
version: '3.9'

services:
  # Usar image en lugar de build para producción
  auth-service:
    image: turegistro.azurecr.io/auth-service:latest
    environment:
      DATABASE_URL: postgresql://postgres:${DB_PASSWORD}@auth-db:5432/auth_db
      # ... otras configuraciones
    restart: always

  # ... otros servicios
```

### 4.2 Construir y subir imágenes

```bash
cd backend/auth-service
docker build -t turegistro.azurecr.io/auth-service:1.0.0 .
docker push turegistro.azurecr.io/auth-service:1.0.0

# Repetir para todos los servicios
```

### 4.3 Iniciar contenedores

```bash
docker-compose -f docker-compose.prod.yml up -d

# Verificar estado
docker-compose ps
```

## 5. Monitoreo y Logging

### 5.1 Docker Logs

```bash
# Ver logs de un servicio
docker-compose logs -f auth-service

# Ver logs de todos los servicios
docker-compose logs -f
```

### 5.2 Configurar ELK Stack (Elasticsearch, Logstash, Kibana)

```yaml
elasticsearch:
  image: docker.elastic.co/elasticsearch/elasticsearch:8.0.0
  environment:
    - discovery.type=single-node
    - xpack.security.enabled=false
  ports:
    - "9200:9200"

kibana:
  image: docker.elastic.co/kibana/kibana:8.0.0
  ports:
    - "5601:5601"
```

### 5.3 Configurar Prometheus para métricas

```yaml
prometheus:
  image: prom/prometheus:latest
  volumes:
    - ./prometheus.yml:/etc/prometheus/prometheus.yml
  ports:
    - "9090:9090"
```

## 6. Backups

### 6.1 Script de backup automático

```bash
#!/bin/bash

BACKUP_DIR="/opt/backups"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Backup de cada base de datos
for DB in auth submission execution grading plagiarism audit; do
    docker-compose exec -T ${DB}-db pg_dump -U postgres ${DB}_db > \
        $BACKUP_DIR/${DB}_db_$DATE.sql
done

# Backup de Redis
docker-compose exec -T redis redis-cli BGSAVE

# Comprimir backups
tar -czf $BACKUP_DIR/backups_$DATE.tar.gz $BACKUP_DIR/*.sql

# Eliminar backups más antiguos de 30 días
find $BACKUP_DIR -name "*.tar.gz" -mtime +30 -delete

echo "Backup completado: $BACKUP_DIR/backups_$DATE.tar.gz"
```

### 6.2 Configurar ejecución automática

```bash
# Agregar a crontab
0 2 * * * /opt/codigo-evaluacion/scripts/backup.sh
```

## 7. Escalado

### 7.1 Múltiples instancias de servicios

```yaml
version: '3.9'

services:
  auth-service-1:
    image: auth-service:latest
    ports:
      - "8001:8001"

  auth-service-2:
    image: auth-service:latest
    ports:
      - "8011:8001"

  auth-service-3:
    image: auth-service:latest
    ports:
      - "8021:8001"

  load-balancer:
    image: nginx:latest
    ports:
      - "8000:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
```

### 7.2 Load Balancer (nginx)

```nginx
upstream auth_service {
    server auth-service-1:8001;
    server auth-service-2:8001;
    server auth-service-3:8001;
}

server {
    listen 80;

    location /auth {
        proxy_pass http://auth_service;
        proxy_set_header Host $host;
    }
}
```

## 8. Health Checks

### 8.1 Verificar servicios

```bash
curl http://localhost:8001/health
curl http://localhost:8004/health
curl http://localhost:8006/health

# Esperado: {"status": "healthy"}
```

### 8.2 Script de monitoreo

```bash
#!/bin/bash

SERVICES=(
    "http://localhost:8001"
    "http://localhost:8004"
    "http://localhost:8006"
    "http://localhost:8007"
)

for service in "${SERVICES[@]}"; do
    if curl -f "$service/health" > /dev/null 2>&1; then
        echo "✅ $service is UP"
    else
        echo "❌ $service is DOWN"
        # Reiniciar servicio si está caído
        # docker-compose restart $(basename $service)
    fi
done
```

## 9. Actualizaciones

### 9.1 Actualizar servicios sin downtime

```bash
# 1. Construir nueva imagen
docker build -t auth-service:1.0.1 .

# 2. Usar rolling updates
docker-compose up -d --no-deps --build auth-service

# 3. Verificar que está corriendo
docker-compose ps auth-service
```

## 10. Solución de Problemas

### Error: "Port already in use"

```bash
# Encontrar proceso usando el puerto
lsof -i :8001

# Matar proceso
kill -9 <PID>
```

### Error: "Connection refused"

```bash
# Verificar que contenedores estén corriendo
docker-compose ps

# Revisar logs
docker-compose logs servicename

# Reiniciar servicio
docker-compose restart servicename
```

### Error: "Database connection failed"

```bash
# Verificar DB está corriendo
docker-compose logs auth-db

# Reiniciar base de datos
docker-compose restart auth-db

# Verificar conexión
docker-compose exec auth-service psql -h auth-db -U postgres -d auth_db
```

## 11. Checklist de Despliegue

- [ ] Servidor actualizado
- [ ] Docker instalado
- [ ] Certificado SSL configurado
- [ ] Variables de entorno (.env) creadas
- [ ] Imágenes Docker construidas y registradas
- [ ] docker-compose.prod.yml preparado
- [ ] Firewall configurado
- [ ] Nginx configurado como reverse proxy
- [ ] Base de datos inicial migrada
- [ ] Servicios iniciados y verificados
- [ ] Logs monitoreados
- [ ] Backups configurados
- [ ] Alertas establecidas

