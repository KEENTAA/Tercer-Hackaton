"""
Motor Sandbox para ejecución segura de código de estudiantes.

Soporta múltiples lenguajes: Python, JavaScript, Java, C, C++
Implementa: timeout, captura de output, AST scanning para Python
"""

import ast
import json
import logging
import os
import platform
import subprocess
import tempfile
import time
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

# ══════════════════════════════════════════════════════════════════
# CLASES DE DATOS PARA RESULTADOS
# ══════════════════════════════════════════════════════════════════


@dataclass
class ResultadoCaso:
    """Resultado de la ejecución de un único caso de prueba"""

    id_caso: int
    descripcion: Optional[str]
    entrada_datos: Optional[str]
    salida_esperada: str
    salida_obtenida: str
    paso: bool
    tiempo_ms: Optional[int]
    es_obligatorio: bool
    error: Optional[str] = None


@dataclass
class ResultadoEjecucionSandbox:
    """Resultado general de la ejecución en el sandbox"""

    estado_compilacion: str  # SUCCESS | COMPILATION_ERROR | RUNTIME_ERROR | TIMEOUT
    aprobado: bool
    tiempo_usado_ms: Optional[int]
    memoria_usada_kb: Optional[int]
    salida_consola: Optional[str]
    detalle_casos: list[ResultadoCaso]
    casos_totales: int
    casos_aprobados: int


# ══════════════════════════════════════════════════════════════════
# MÓDULOS Y SÍMBOLOS BLOQUEADOS PARA PYTHON
# ══════════════════════════════════════════════════════════════════

MODULOS_BLOQUEADOS_PYTHON = {
    "os",
    "sys",
    "subprocess",
    "shutil",
    "socket",
    "ctypes",
    "multiprocessing",
    "threading",
    "signal",
    "importlib",
    "pickle",
    "__import__",
}

SIMBOLOS_BLOQUEADOS_PYTHON = {
    "exec",
    "eval",
    "compile",
    "open",
    "__import__",
}


# ══════════════════════════════════════════════════════════════════
# CLASE PRINCIPAL DEL SANDBOX
# ══════════════════════════════════════════════════════════════════


class SandboxExecutor:
    """
    Motor de ejecución segura de código en sandbox.
    Soporta múltiples lenguajes de programación.
    """

    def __init__(self, max_timeout_ms: int = 10000):
        """
        Inicializar el executor.

        Args:
            max_timeout_ms: Timeout máximo en milisegundos (default: 10000)
        """
        self.max_timeout_ms = max_timeout_ms
        self.sistema_operativo = platform.system()

    def ejecutar(
        self,
        lenguaje: str,
        codigo_fuente: str,
        casos_prueba: list,
    ) -> ResultadoEjecucionSandbox:
        """
        Ejecutar código en sandbox y evaluar contra casos de prueba.

        Args:
            lenguaje: Lenguaje de programación ('python', 'javascript', 'java', 'c', 'cpp')
            codigo_fuente: Código completo como string
            casos_prueba: Lista de objetos CasoPrueba de la BD

        Returns:
            ResultadoEjecucionSandbox: Resultado de la ejecución
        """
        lenguaje = lenguaje.lower().strip()

        # Validar AST de Python antes de ejecutar
        if lenguaje == "python":
            try:
                self._validar_ast_python(codigo_fuente)
            except ValueError as e:
                logger.warning(f"Código Python bloqueado: {e}")
                return ResultadoEjecucionSandbox(
                    estado_compilacion="COMPILATION_ERROR",
                    aprobado=False,
                    tiempo_usado_ms=None,
                    memoria_usada_kb=None,
                    salida_consola=str(e),
                    detalle_casos=[],
                    casos_totales=len(casos_prueba),
                    casos_aprobados=0,
                )

        # Crear directorio temporal para los archivos
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            try:
                # Compilar si es necesario
                if lenguaje in {"java", "c", "cpp"}:
                    resultado_compilacion = self._compilar(
                        lenguaje, codigo_fuente, temp_path
                    )
                    if resultado_compilacion["error"]:
                        return ResultadoEjecucionSandbox(
                            estado_compilacion="COMPILATION_ERROR",
                            aprobado=False,
                            tiempo_usado_ms=None,
                            memoria_usada_kb=None,
                            salida_consola=resultado_compilacion["stderr"],
                            detalle_casos=[],
                            casos_totales=len(casos_prueba),
                            casos_aprobados=0,
                        )
                    archivo_ejecutable = resultado_compilacion["ejecutable"]
                else:
                    # Escribir archivo fuente para Python y JavaScript
                    if lenguaje == "python":
                        archivo_fuente = temp_path / "main.py"
                    elif lenguaje == "javascript":
                        archivo_fuente = temp_path / "main.js"

                    archivo_fuente.write_text(codigo_fuente, encoding="utf-8")
                    archivo_ejecutable = str(archivo_fuente)

                # Ejecutar cada caso de prueba
                detalles_casos = []
                tiempo_total = 0
                casos_aprobados = 0

                for caso in casos_prueba:
                    inicio = time.time()
                    resultado_caso = self._ejecutar_caso(
                        lenguaje, archivo_ejecutable, caso
                    )
                    fin = time.time()

                    resultado_caso.tiempo_ms = int((fin - inicio) * 1000)
                    tiempo_total += resultado_caso.tiempo_ms

                    if resultado_caso.paso and resultado_caso.es_obligatorio:
                        casos_aprobados += 1

                    detalles_casos.append(resultado_caso)

                # Determinar estado general
                aprobado = all(
                    caso.paso for caso in detalles_casos if caso.es_obligatorio
                )
                estado = "SUCCESS"

                return ResultadoEjecucionSandbox(
                    estado_compilacion=estado,
                    aprobado=aprobado,
                    tiempo_usado_ms=tiempo_total,
                    memoria_usada_kb=None,  # No se captura en el sandbox simple
                    salida_consola=None,
                    detalle_casos=detalles_casos,
                    casos_totales=len(casos_prueba),
                    casos_aprobados=casos_aprobados,
                )

            except Exception as e:
                logger.error(f"Error fatal en sandbox: {e}")
                return ResultadoEjecucionSandbox(
                    estado_compilacion="RUNTIME_ERROR",
                    aprobado=False,
                    tiempo_usado_ms=None,
                    memoria_usada_kb=None,
                    salida_consola=str(e),
                    detalle_casos=[],
                    casos_totales=len(casos_prueba),
                    casos_aprobados=0,
                )

    def _validar_ast_python(self, codigo: str) -> None:
        """
        Validar el AST del código Python para detectar módulos/símbolos peligrosos.

        Args:
            codigo: Código Python a validar

        Raises:
            ValueError: Si se detectan imports o símbolos bloqueados
        """
        try:
            tree = ast.parse(codigo)
        except SyntaxError as e:
            raise ValueError(f"Error de sintaxis: {e}")

        # Analizar el AST
        for node in ast.walk(tree):
            # Detectar imports
            if isinstance(node, ast.Import):
                for alias in node.names:
                    nombre_modulo = alias.name.split(".")[0]
                    if nombre_modulo in MODULOS_BLOQUEADOS_PYTHON:
                        raise ValueError(
                            f"El módulo '{nombre_modulo}' está bloqueado por razones de seguridad"
                        )

            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    nombre_modulo = node.module.split(".")[0]
                    if nombre_modulo in MODULOS_BLOQUEADOS_PYTHON:
                        raise ValueError(
                            f"El módulo '{nombre_modulo}' está bloqueado por razones de seguridad"
                        )

            # Detectar llamadas a funciones peligrosas
            elif isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    if node.func.id in SIMBOLOS_BLOQUEADOS_PYTHON:
                        raise ValueError(
                            f"La función '{node.func.id}' está bloqueada por razones de seguridad"
                        )

    def _compilar(
        self, lenguaje: str, codigo_fuente: str, temp_path: Path
    ) -> dict:
        """
        Compilar código (Java, C, C++).

        Args:
            lenguaje: Lenguaje a compilar
            codigo_fuente: Código fuente como string
            temp_path: Directorio temporal donde guardar archivos

        Returns:
            dict: {error: bool, stderr: str, ejecutable: str}
        """
        try:
            if lenguaje == "java":
                return self._compilar_java(codigo_fuente, temp_path)
            elif lenguaje == "c":
                return self._compilar_c(codigo_fuente, temp_path)
            elif lenguaje == "cpp":
                return self._compilar_cpp(codigo_fuente, temp_path)
        except Exception as e:
            logger.error(f"Error compilando {lenguaje}: {e}")
            return {"error": True, "stderr": str(e), "ejecutable": None}

    def _compilar_java(self, codigo_fuente: str, temp_path: Path) -> dict:
        """Compilar código Java"""
        # La clase principal DEBE llamarse Main
        archivo = temp_path / "Main.java"
        archivo.write_text(codigo_fuente, encoding="utf-8")

        cmd = ["javac", str(archivo)]
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30,
                cwd=str(temp_path),
            )

            if result.returncode != 0:
                return {"error": True, "stderr": result.stderr, "ejecutable": None}

            # El ejecutable es el comando "java -cp {temp_path} Main"
            return {
                "error": False,
                "stderr": "",
                "ejecutable": f"java -cp {temp_path} Main",
            }
        except subprocess.TimeoutExpired:
            return {
                "error": True,
                "stderr": "Compilación de Java excedió timeout",
                "ejecutable": None,
            }

    def _compilar_c(self, codigo_fuente: str, temp_path: Path) -> dict:
        """Compilar código C"""
        archivo = temp_path / "main.c"
        archivo.write_text(codigo_fuente, encoding="utf-8")
        ejecutable = temp_path / "main"

        cmd = ["gcc", str(archivo), "-o", str(ejecutable), "-lm"]
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30,
                cwd=str(temp_path),
            )

            if result.returncode != 0:
                return {"error": True, "stderr": result.stderr, "ejecutable": None}

            return {
                "error": False,
                "stderr": "",
                "ejecutable": str(ejecutable),
            }
        except subprocess.TimeoutExpired:
            return {
                "error": True,
                "stderr": "Compilación de C excedió timeout",
                "ejecutable": None,
            }

    def _compilar_cpp(self, codigo_fuente: str, temp_path: Path) -> dict:
        """Compilar código C++"""
        archivo = temp_path / "main.cpp"
        archivo.write_text(codigo_fuente, encoding="utf-8")
        ejecutable = temp_path / "main"

        cmd = ["g++", str(archivo), "-o", str(ejecutable), "-std=c++17"]
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30,
                cwd=str(temp_path),
            )

            if result.returncode != 0:
                return {"error": True, "stderr": result.stderr, "ejecutable": None}

            return {
                "error": False,
                "stderr": "",
                "ejecutable": str(ejecutable),
            }
        except subprocess.TimeoutExpired:
            return {
                "error": True,
                "stderr": "Compilación de C++ excedió timeout",
                "ejecutable": None,
            }

    def _ejecutar_caso(self, lenguaje: str, archivo_ejecutable: str, caso) -> ResultadoCaso:
        """
        Ejecutar un caso de prueba individual.

        Args:
            lenguaje: Lenguaje del código
            archivo_ejecutable: Ruta del archivo a ejecutar o comando
            caso: Objeto CasoPrueba con los datos del caso

        Returns:
            ResultadoCaso: Resultado de la ejecución del caso
        """
        stdin_bytes = (caso.entrada_datos or "").encode("utf-8")
        timeout_segundos = caso.tiempo_limite_ms / 1000.0

        try:
            # Construir el comando según el lenguaje
            if lenguaje == "python":
                cmd = ["python3", archivo_ejecutable]
            elif lenguaje == "javascript":
                cmd = ["node", archivo_ejecutable]
            elif lenguaje == "java":
                # archivo_ejecutable es "java -cp {temp_path} Main"
                cmd = archivo_ejecutable.split()
            elif lenguaje in {"c", "cpp"}:
                cmd = [archivo_ejecutable]
            else:
                return ResultadoCaso(
                    id_caso=caso.id_caso,
                    descripcion=caso.descripcion,
                    entrada_datos=caso.entrada_datos,
                    salida_esperada=caso.salida_esperada,
                    salida_obtenida="",
                    paso=False,
                    tiempo_ms=None,
                    es_obligatorio=caso.es_obligatorio,
                    error="Lenguaje no soportado",
                )

            # Ejecutar el proceso
            result = subprocess.run(
                cmd,
                input=stdin_bytes,
                capture_output=True,
                text=True,
                timeout=timeout_segundos,
            )

            salida_obtenida = result.stdout

        except subprocess.TimeoutExpired:
            return ResultadoCaso(
                id_caso=caso.id_caso,
                descripcion=caso.descripcion,
                entrada_datos=caso.entrada_datos,
                salida_esperada=caso.salida_esperada,
                salida_obtenida="",
                paso=False,
                tiempo_ms=int(timeout_segundos * 1000),
                es_obligatorio=caso.es_obligatorio,
                error="Timeout: El código tardó más del tiempo permitido",
            )

        except FileNotFoundError as e:
            return ResultadoCaso(
                id_caso=caso.id_caso,
                descripcion=caso.descripcion,
                entrada_datos=caso.entrada_datos,
                salida_esperada=caso.salida_esperada,
                salida_obtenida="",
                paso=False,
                tiempo_ms=None,
                es_obligatorio=caso.es_obligatorio,
                error=f"Archivo no encontrado: {e}",
            )

        except Exception as e:
            return ResultadoCaso(
                id_caso=caso.id_caso,
                descripcion=caso.descripcion,
                entrada_datos=caso.entrada_datos,
                salida_esperada=caso.salida_esperada,
                salida_obtenida="",
                paso=False,
                tiempo_ms=None,
                es_obligatorio=caso.es_obligatorio,
                error=f"Error en ejecución: {str(e)}",
            )

        # Comparar salidas
        salida_esperada_limpia = caso.salida_esperada.strip()
        salida_obtenida_limpia = salida_obtenida.strip()
        paso = salida_esperada_limpia == salida_obtenida_limpia

        return ResultadoCaso(
            id_caso=caso.id_caso,
            descripcion=caso.descripcion,
            entrada_datos=caso.entrada_datos,
            salida_esperada=caso.salida_esperada,
            salida_obtenida=salida_obtenida,
            paso=paso,
            tiempo_ms=None,  # Se calcula en ejecutar()
            es_obligatorio=caso.es_obligatorio,
            error=None if paso else "Salida no coincide",
        )
