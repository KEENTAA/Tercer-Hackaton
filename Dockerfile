# Stage 1 — builder: instalar dependencias Python
FROM python:3.11-slim AS builder

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip setuptools wheel

COPY requirements.txt .
RUN pip install --prefix=/install -r requirements.txt


# Stage 2 — runtime: imagen final lean
FROM python:3.11-slim AS runtime

# Instalar dependencias de runtime: compiladores, runtimes y librerías
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    default-jdk-headless \
    nodejs \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Copiar dependencias Python compiladas del builder
COPY --from=builder /install /usr/local

# Crear usuario no-root
RUN groupadd -r runner && useradd -r -g runner runner

# Configurar directorio de trabajo
WORKDIR /app
COPY --chown=runner:runner . .

# Usuario no-root
USER runner

# Variables de entorno
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PATH="/usr/local/bin:$PATH"

# Puerto
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health').read()"

# Comando
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
