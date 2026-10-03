import math
from typing import Any

def height_to_inches(height: str) -> int:
    """
    Convierte formato '5\' 9"' a pulgadas totales (69).
    """
    if not height:
        return 0
    
    try:
        clean_height = height.replace('"', '').strip()
        parts = clean_height.split("'")
        
        feet = int(parts[0].strip())
        inches = int(parts[1].strip()) if len(parts) > 1 and parts[1].strip() else 0

        return (feet * 12) + inches
    except (ValueError, IndexError):
        return 0

def _to_float(value: Any) -> float:
    """Convierte de forma segura cualquier entrada a float para evitar TypeErrors."""
    try:
        return float(value) if value is not None else 0.0
    except (ValueError, TypeError):
        return 0.0

# --- MÉTRICAS DE BATEO (HITTING STATS) ---

def calculate_iso(h, d, t, hr, ab):
    """
    Poder aislado (Isolated Power).
    Blindaje: Evita TypeError entre None y int.
    """
    h, d, t, hr, ab = map(_to_float, [h, d, t, hr, ab])
    
    if ab <= 0: 
        return 0.0
        
    extra_bases = d + (2 * t) + (3 * hr)
    return round(extra_bases / ab, 3)

def calculate_woba(h, d, t, hr, bb, ab, hbp=0, sf=0, uBB=None):
    """
    Promedio de embasado ponderado (wOBA).
    Blindaje: Maneja denominadores de cero y nulos en componentes secundarios.
    """
    h, d, t, hr, bb, ab, hbp, sf = map(_to_float, [h, d, t, hr, bb, ab, hbp, sf])
    unintentional_bb = _to_float(uBB) if uBB is not None else bb
    
    singles = h - (d + t + hr)
    
    numerator = (0.69 * unintentional_bb) + (0.72 * hbp) + (0.89 * singles) + \
                (1.27 * d) + (1.62 * t) + (2.10 * hr)
    
    denominator = ab + bb + sf + hbp
    return round(numerator / denominator, 3) if denominator > 0 else 0.0

def calculate_slg(h, d, t, hr, ab):
    """Slugging Percentage reforzado."""
    h, d, t, hr, ab = map(_to_float, [h, d, t, hr, ab])
    
    if ab <= 0: 
        return 0.0
        
    total_bases = (h - d - t - hr) + (2 * d) + (3 * t) + (4 * hr)
    return round(total_bases / ab, 3)

# --- MÉTRICAS DE PITCHO (PITCHING STATS) ---

def calculate_fip(hr, bb, k, ip, constant_c=3.10, hbp=0):
    """Pitcheo independiente de la defensa (FIP)[cite: 11]."""
    hr, bb, k, ip, constant_c, hbp = map(_to_float, [hr, bb, k, ip, constant_c, hbp])
    
    if ip <= 0: 
        return 0.0
        
    return round(((13 * hr + 3 * (bb + hbp) - 2 * k) / ip) + constant_c, 2)

def calculate_csw_pct(strikes_cantados, strikes_abanicados, total_pitches):
    """Strikes cantados + abanicos (CSW%)[cite: 11]."""
    sc, sa, tp = map(_to_float, [strikes_cantados, strikes_abanicados, total_pitches])
    
    if tp <= 0: 
        return 0.0
        
    return round((sc + sa) / tp, 4)

# --- MÉTRICAS ADICIONALES ---

def calculate_babip(h, hr, ab, k, sf=0):
    """Promedio de pelotas puestas en juego (BABIP)[cite: 11]."""
    h, hr, ab, k, sf = map(_to_float, [h, hr, ab, k, sf])
    
    denominator = ab - k - hr + sf
    if denominator <= 0: 
        return 0.0
        
    return round((h - hr) / denominator, 3)

def calculate_siera(k_pct, bb_pct, gb_pct):
    """ERA ajustada por habilidad (SIERA) con protección de nulos[cite: 11]."""
    k_pct, bb_pct, gb_pct = map(_to_float, [k_pct, bb_pct, gb_pct])
    
    if k_pct <= 0: 
        return 0.0
        
    siera_val = 6.145 - 16.986*(k_pct) + 11.434*(bb_pct) - 1.858*(gb_pct) + 7.653*(k_pct**2)
    return round(siera_val, 2)

def calculate_velocity_loss(current_median, start_median):
    """Diferencia de velocidad (Fatiga)[cite: 11]."""
    curr, start = map(_to_float, [current_median, start_median])
    return round(start - curr, 2)