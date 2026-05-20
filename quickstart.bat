@echo off
REM QUICKSTART SCRIPT PARA MS2 - Motor de Ejecución y Evaluación
REM Uso: quickstart.bat

setlocal enabledelayedexpansion

echo.
echo ═══════════════════════════════════════════════════════════════
echo 🚀 MS2 - Motor de Ejecución y Evaluación
echo    Quickstart Script
echo ═══════════════════════════════════════════════════════════════
echo.

REM 1. Crear virtual environment
echo 📦 Creando virtual environment...
if not exist ".venv" (
    python -m venv .venv
    echo ✓ Virtual environment creado
) else (
    echo ✓ Virtual environment ya existe
)

REM 2. Instalar dependencias
echo.
echo 📥 Instalando dependencias...
call .venv\Scripts\activate.bat
pip install -q -r requirements.txt
echo ✓ Dependencias instaladas

REM 3. Crear .env si no existe
echo.
echo ⚙️  Configurando .env...
if not exist ".env" (
    copy .env.example .env
    echo ✓ .env creado (modifica DATABASE_URL si es necesario)
) else (
    echo ✓ .env ya existe
)

REM 4. Mensaje final
echo.
echo ═══════════════════════════════════════════════════════════════
echo ✅ Setup completado!
echo.
echo Para iniciar el servidor:
echo.
echo   .venv\Scripts\activate
echo   uvicorn app.main:app --reload --port 8000
echo.
echo O usa Docker Compose:
echo   docker compose up --build
echo.
echo Documentación interactiva:
echo   http://localhost:8000/docs
echo.
echo ═══════════════════════════════════════════════════════════════
echo.

pause
