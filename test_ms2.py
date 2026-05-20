"""
Tests básicos para validar funcionalidad del MS2.
Uso: pytest tests/ o pytest tests/test_*.py
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import Base, get_db
from app.models import CasoPrueba, ResultadoEjecucion


# Database setup para testing
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


@pytest.fixture
def db():
    """Crear tablas y retornar sesión para testing"""
    Base.metadata.create_all(bind=engine)
    yield TestingSessionLocal()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client(db):
    """Cliente de testing para FastAPI"""

    def override_get_db():
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    yield TestClient(app)

    del app.dependency_overrides[get_db]


# ══════════════════════════════════════════════════════════════════
# TESTS
# ══════════════════════════════════════════════════════════════════


def test_health_check(client):
    """Probar health check"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "servicio" in data
    assert "version" in data


def test_crear_casos_prueba(client):
    """Probar creación de casos de prueba"""
    response = client.post(
        "/api/v1/runner/test-cases",
        json={
            "casos": [
                {
                    "id_tarea_ref": 1,
                    "entrada_datos": "5 3",
                    "salida_esperada": "8",
                    "tiempo_limite_ms": 3000,
                    "descripcion": "Suma",
                    "es_obligatorio": True,
                }
            ]
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert len(data) == 1
    assert data[0]["id_caso"] == 1
    assert data[0]["id_tarea_ref"] == 1


def test_listar_casos_por_tarea(client, db):
    """Probar listado de casos por tarea"""
    # Crear un caso
    caso = CasoPrueba(
        id_tarea_ref=1,
        entrada_datos="test",
        salida_esperada="test",
        tiempo_limite_ms=3000,
    )
    db.add(caso)
    db.commit()

    # Listar
    response = client.get("/api/v1/runner/test-cases/assignment/1")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["id_tarea_ref"] == 1


def test_listar_casos_no_existen(client):
    """Probar 404 si no hay casos"""
    response = client.get("/api/v1/runner/test-cases/assignment/999")
    assert response.status_code == 404


def test_validacion_lenguaje_invalido(client):
    """Probar validación de lenguaje"""
    response = client.post(
        "/api/v1/runner/execute",
        json={
            "id_intento_ref": 1,
            "id_tarea_ref": 1,
            "lenguaje": "rust",
            "codigo_fuente": "print('hola')",
        },
    )
    assert response.status_code == 422


def test_validacion_codigo_vacio(client):
    """Probar validación de código vacío"""
    response = client.post(
        "/api/v1/runner/execute",
        json={
            "id_intento_ref": 1,
            "id_tarea_ref": 1,
            "lenguaje": "python",
            "codigo_fuente": "",
        },
    )
    assert response.status_code == 422


def test_ejecutar_sin_casos(client):
    """Probar 404 si no hay casos para la tarea"""
    response = client.post(
        "/api/v1/runner/execute",
        json={
            "id_intento_ref": 1,
            "id_tarea_ref": 999,
            "lenguaje": "python",
            "codigo_fuente": "print('hello')",
        },
    )
    assert response.status_code == 404


def test_ejecutar_python_exitoso(client, db):
    """Probar ejecución exitosa de Python"""
    # Crear caso de prueba
    caso = CasoPrueba(
        id_tarea_ref=1,
        entrada_datos="5 3",
        salida_esperada="8",
        tiempo_limite_ms=3000,
    )
    db.add(caso)
    db.commit()

    # Ejecutar
    response = client.post(
        "/api/v1/runner/execute",
        json={
            "id_intento_ref": 100,
            "id_tarea_ref": 1,
            "lenguaje": "python",
            "codigo_fuente": "a, b = map(int, input().split())\nprint(a + b)",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["aprobado"] is True
    assert data["casos_totales"] == 1
    assert data["casos_aprobados"] == 1


def test_ejecutar_python_fallido(client, db):
    """Probar ejecución fallida de Python"""
    # Crear caso de prueba
    caso = CasoPrueba(
        id_tarea_ref=1,
        entrada_datos="5 3",
        salida_esperada="8",
        tiempo_limite_ms=3000,
    )
    db.add(caso)
    db.commit()

    # Ejecutar (código incorrecto)
    response = client.post(
        "/api/v1/runner/execute",
        json={
            "id_intento_ref": 101,
            "id_tarea_ref": 1,
            "lenguaje": "python",
            "codigo_fuente": "a, b = map(int, input().split())\nprint(a * b)",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["aprobado"] is False
    assert data["casos_aprobados"] == 0


def test_ejecutar_python_bloqueado(client, db):
    """Probar bloqueo de módulos peligrosos"""
    # Crear caso de prueba
    caso = CasoPrueba(
        id_tarea_ref=1,
        entrada_datos="test",
        salida_esperada="test",
        tiempo_limite_ms=3000,
    )
    db.add(caso)
    db.commit()

    # Ejecutar (con import bloqueado)
    response = client.post(
        "/api/v1/runner/execute",
        json={
            "id_intento_ref": 102,
            "id_tarea_ref": 1,
            "lenguaje": "python",
            "codigo_fuente": "import os\nos.system('whoami')",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["estado_compilacion"] == "COMPILATION_ERROR"
    assert "bloqueado" in data["salida_consola"].lower()


def test_obtener_resultado(client, db):
    """Probar obtención de resultado"""
    # Crear resultado
    resultado = ResultadoEjecucion(
        id_intento_ref=200,
        id_tarea_ref=1,
        lenguaje="python",
        estado_compilacion="SUCCESS",
        aprobado=True,
        casos_totales=1,
        casos_aprobados=1,
    )
    db.add(resultado)
    db.commit()

    # Obtener
    response = client.get("/api/v1/runner/results/200")
    assert response.status_code == 200
    data = response.json()
    assert data["id_intento_ref"] == 200
    assert data["aprobado"] is True


def test_obtener_resultado_no_existe(client):
    """Probar 404 si no existe resultado"""
    response = client.get("/api/v1/runner/results/999")
    assert response.status_code == 404


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
