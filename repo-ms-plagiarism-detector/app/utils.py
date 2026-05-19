import hashlib
import re
from difflib import SequenceMatcher

def generate_code_hash(source_code: str) -> str:
    """
    Genera un hash SHA-256 del código fuente normalizado.
    """
    if not source_code:
        return ""
    clean_code = re.sub(r'(#|//).*', '', source_code)
    clean_code = "".join(clean_code.split())
    return hashlib.sha256(clean_code.encode()).hexdigest()

def calculate_fuzzy_similarity(code1: str, code2: str) -> float:
    """
    Calcula el porcentaje de similitud entre dos bloques de texto.
    Ideal para detectar cambios menores en el código.
    """
    # Normalizamos antes de comparar
    c1 = "".join(code1.split())
    c2 = "".join(code2.split())
    
    ratio = SequenceMatcher(None, c1, c2).ratio()
    return round(ratio * 100, 2)

def mock_turnitin_check(source_code: str) -> dict:
    """
    Simula una llamada a la API de TurnItIn.
    """
    similarity = 0.0
    if "copy" in source_code.lower():
        similarity = 75.0
    else:
        # Devolvemos un valor aleatorio pequeño para que se vea dinámico
        similarity = (len(source_code) % 10) + 5.0
        
    return {
        "external_id": f"TII-{hashlib.md5(source_code.encode()).hexdigest()[:8]}",
        "similarity": similarity
    }
