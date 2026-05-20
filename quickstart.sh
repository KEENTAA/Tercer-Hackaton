#!/bin/bash

###
### QUICKSTART SCRIPT PARA MS2 - Motor de Ejecución y Evaluación
### Uso: bash quickstart.sh
###

set -e

echo "═══════════════════════════════════════════════════════════════"
echo "🚀 MS2 - Motor de Ejecución y Evaluación"
echo "   Quickstart Script"
echo "═══════════════════════════════════════════════════════════════"
echo ""

# Detectar SO
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
    VENV_ACTIVATE=".venv\\Scripts\\activate"
else
    VENV_ACTIVATE=".venv/bin/activate"
fi

# 1. Crear virtual environment
echo "📦 Creando virtual environment..."
if [ ! -d ".venv" ]; then
    python -m venv .venv
    echo "✓ Virtual environment creado"
else
    echo "✓ Virtual environment ya existe"
fi

# 2. Activar venv y instalar dependencias
echo ""
echo "📥 Instalando dependencias..."
source "$VENV_ACTIVATE"
pip install -q -r requirements.txt
echo "✓ Dependencias instaladas"

# 3. Crear .env si no existe
echo ""
echo "⚙️  Configurando .env..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "✓ .env creado (modifica DATABASE_URL si es necesario)"
else
    echo "✓ .env ya existe"
fi

# 4. Mensaje final
echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "✅ Setup completado!"
echo ""
echo "Para iniciar el servidor:"
echo ""
echo "  Linux/Mac:"
echo "    source .venv/bin/activate"
echo "    uvicorn app.main:app --reload --port 8000"
echo ""
echo "  Windows:"
echo "    .venv\\Scripts\\activate"
echo "    uvicorn app.main:app --reload --port 8000"
echo ""
echo "O usa Docker Compose:"
echo "    docker compose up --build"
echo ""
echo "Documentación interactiva:"
echo "    http://localhost:8000/docs"
echo ""
echo "═══════════════════════════════════════════════════════════════"
