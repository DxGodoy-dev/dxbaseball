"""
CATÁLOGO DE ESCALAMIENTO (Punto Fijo)
Define los factores de multiplicación para cada etiqueta lógica del contrato.
"""
import re
from datetime import datetime
from typing import Union, Optional

from src.dxbaseball_bets.core.config.data_contract import CodeMappings, DataScale

def map_code(mapping_dict: dict):
    """Crea una función que busca en el diccionario y devuelve 0 si no existe."""
    return lambda v: mapping_dict.get(v, {}).get("value", 0)

def scale_by(factor: int):
    return lambda v: int(round(v * factor)) if isinstance(v, (int, float)) else 0

def height_to_inches(height: str) -> int:
    """
    Normaliza el string de altura (ej: '5\' 9"') a pulgadas totales (int).
    """
    if not height or not isinstance(height, str):
        return 0
    
    try:
        # Limpieza de comillas y espacios laterales
        clean_height = height.replace('"', '').strip()
        parts = clean_height.split("'")
        
        feet = int(parts[0].strip())
        # Maneja casos donde no se especifican pulgadas tras la comilla
        inches = int(parts[1].strip()) if len(parts) > 1 and parts[1].strip() else 0
        
        return (feet * 12) + inches
    except (ValueError, IndexError):
        return 0

def format_date_to_int(date_input: Union[str, datetime]) -> Optional[int]:
    """
    Transforma fechas o timestamps ISO a entero YYYYMMDDHHMM.
    Ejemplo: '2023-10-25T00:07:00Z' -> 202310250007.
    """
    if not date_input:
        return None

    try:
        if isinstance(date_input, str):
            # Normalizamos el formato: reemplazamos 'Z' por '+00:00' para que 
            # fromisoformat lo reconozca correctamente como UTC.
            clean_date = date_input.replace('Z', '+00:00')
            dt = datetime.fromisoformat(clean_date)
        elif isinstance(date_input, datetime):
            dt = date_input
        else:
            return None
            
        # Retornamos el entero de 12 dígitos (YYYYMMDDHHMM)
        return int(dt.strftime("%Y%m%d%H%M"))
        
    except (ValueError, TypeError):
        return None

SCALES = {
    # --- ESCALAS ARITMÉTICAS (Existentes) ---
    "SCALE_1":    lambda v: v, # Identidad (IDs, Strings)
    "SCALE_10":   scale_by(10), # Velocidad, IP
    "SCALE_100":  scale_by(100), # Porcentajes, ERA
    "SCALE_1000": scale_by(1000), # AVG, wOBA, Coordenadas

    # --- TRANSFORMACIONES DE FORMATO ---
    "FORMAT_HEIGHT": height_to_inches,
    "FORMAT_DATE":   format_date_to_int,

    # --- TRANSFORMACIONES DE MAPEO ---
    "CODE_PITCH":    map_code(CodeMappings.PITCH_CALLS),
    "CODE_EVENT":    map_code(CodeMappings.EVENT_LOOKUP),
    "CODE_POSITION": map_code(CodeMappings.POSITIONS),
    "CODE_HAND":     map_code(CodeMappings.HANDS),
    "CODE_SIDE":     map_code(CodeMappings.SIDES),  
}