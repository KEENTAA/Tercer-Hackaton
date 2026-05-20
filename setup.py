"""
Setup script para instalar MS2 como paquete de Python (opcional).
Permite: pip install -e .
"""

from setuptools import setup, find_packages

setup(
    name="ms2-code-runner",
    version="1.0.0",
    description="MS2 - Motor de Ejecución y Evaluación de Código",
    author="Frog Software Ltda.",
    author_email="dev@frog-software.com",
    url="https://github.com/FrogSoftware/repo-ms-code-runner",
    python_requires=">=3.11",
    packages=find_packages(),
    install_requires=[
        "fastapi==0.111.0",
        "uvicorn[standard]==0.29.0",
        "sqlalchemy==2.0.30",
        "alembic==1.13.1",
        "psycopg2-binary==2.9.9",
        "python-dotenv==1.0.1",
        "pydantic==2.7.1",
        "pydantic-settings==2.2.1",
        "httpx==0.27.0",
    ],
    extras_require={
        "dev": [
            "pytest==8.2.0",
            "pytest-asyncio==0.23.6",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Framework :: FastAPI",
        "Topic :: Education",
        "License :: OSI Approved :: MIT License",
    ],
)
