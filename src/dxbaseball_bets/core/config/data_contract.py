"""
CONTRATO UNIFICADO DE DATOS (MLB API -> DB)
"""
# --- CONVERSIONES ---
class DataScale:
    """Escalas de punto fijo sincronizadas con los Mixins de la DB."""
    NONE    = "SCALE_1"      # IDs, Strings, Flags
    COUNT   = "SCALE_1"      # Enteros (Hits, HR, K, RBI)
    METRIC  = "SCALE_10"     # x10 (Velocity, Inning Metrics, Distance)
    PCT     = "SCALE_100"    # x100 (Uso general)
    PRECISE = "SCALE_1000"   # x1000 (AVG, OBP, SLG, wOBA, Coordenadas, CSW%)
    HEIGHT  = "FORMAT_HEIGHT"
    DATE    = "FORMAT_DATE"
    CODE_PITCH = "CODE_PITCH"
    CODE_EVENT = "CODE_EVENT"

class CodeMappings:
    """
    Catálogo de normalización de categorías MLB.
    Refactorizado para ser compatible con el DataProcessor declarativo.
    """
    
    # --- MAPEOS SIMPLES (Identidad de Jugador) ---
    HANDS = {
        "R": {"value": 1, "scale": "CODE_HAND"}, 
        "L": {"value": 2, "scale": "CODE_HAND"}, 
        "S": {"value": 3, "scale": "CODE_HAND"},
    }

    SIDES = {
        "R": {"value": 1, "scale": "CODE_SIDE"}, 
        "L": {"value": 2, "scale": "CODE_SIDE"}, 
        "S": {"value": 3, "scale": "CODE_SIDE"}
    }
    
    # --- POSICIONES (Defensa y Roles) ---
    POSITIONS = {
        "1": {"value": 1, "scale": "CODE_POSITION"},
        "2": {"value": 2, "scale": "CODE_POSITION"},
        "3": {"value": 3, "scale": "CODE_POSITION"},
        "4": {"value": 4, "scale": "CODE_POSITION"},
        "5": {"value": 5, "scale": "CODE_POSITION"},
        "6": {"value": 6, "scale": "CODE_POSITION"},
        "7": {"value": 7, "scale": "CODE_POSITION"},
        "8": {"value": 8, "scale": "CODE_POSITION"},
        "9": {"value": 9, "scale": "CODE_POSITION"},
        "10": {"value": 10, "scale": "CODE_POSITION"},
        "11": {"value": 11, "scale": "CODE_POSITION"},
        "12": {"value": 12, "scale": "CODE_POSITION"},
        "13": {"value": 13, "scale": "CODE_POSITION"},
        "BR": {"value": 14, "scale": "CODE_POSITION"},
        "PR": {"value": 12, "scale": "CODE_POSITION"},
        "O": {"value": 15, "scale": "CODE_POSITION"},
        "I": {"value": 16, "scale": "CODE_POSITION"},
        "U": {"value": 20, "scale": "CODE_POSITION"},
        "V": {"value": 21, "scale": "CODE_POSITION"},
        "W": {"value": 22, "scale": "CODE_POSITION"},
        "S": {"value": 17, "scale": "CODE_POSITION"},
        "E": {"value": 18, "scale": "CODE_POSITION"},
        "C": {"value": 19, "scale": "CODE_POSITION"},
        "K": {"value": 23, "scale": "CODE_POSITION"},
        "L": {"value": 24, "scale": "CODE_POSITION"},
        "M": {"value": 25, "scale": "CODE_POSITION"},
        "N": {"value": 26, "scale": "CODE_POSITION"},
        "G": {"value": 27, "scale": "CODE_POSITION"},
        "F": {"value": 28, "scale": "CODE_POSITION"},
        "A": {"value": 29, "scale": "CODE_POSITION"},
        "J": {"value": 30, "scale": "CODE_POSITION"},
        "Z": {"value": 31, "scale": "CODE_POSITION"},
        "Y": {"value": 32, "scale": "CODE_POSITION"},
        "X": {"value": 34, "scale": "CODE_POSITION"},
        "R1": {"value": 35, "scale": "CODE_POSITION"},
        "R2": {"value": 36, "scale": "CODE_POSITION"},
        "R3": {"value": 37, "scale": "CODE_POSITION"},
    }

    # --- RESULTADOS FINALES DEL AT-BAT (EVENT_LOOKUP) ---
    EVENT_LOOKUP = {
        "single": {"value": 11, "scale": "CODE_EVENT"}, 
        "double": {"value": 12, "scale": "CODE_EVENT"}, 
        "triple": {"value": 13, "scale": "CODE_EVENT"}, 
        "home_run": {"value": 14, "scale": "CODE_EVENT"}, 
        "fielders_choice": {"value": 19, "scale": "CODE_EVENT"},
        "field_out": {"value": 20, "scale": "CODE_EVENT"}, 
        "force_out": {"value": 21, "scale": "CODE_EVENT"},
        "sac_fly": {"value": 22, "scale": "CODE_EVENT"},
        "sac_bunt": {"value": 23, "scale": "CODE_EVENT"}, 
        "fielders_choice_out": {"value": 24, "scale": "CODE_EVENT"},
        "strikeout": {"value": 30, "scale": "CODE_EVENT"}, 
        "strike_out": {"value": 31, "scale": "CODE_EVENT"}, 
        "double_play": {"value": 32, "scale": "CODE_EVENT"}, 
        "grounded_into_double_play": {"value": 33, "scale": "CODE_EVENT"}, 
        "strikeout_double_play": {"value": 34, "scale": "CODE_EVENT"}, 
        "strikeout_triple_play": {"value": 35, "scale": "CODE_EVENT"}, 
        "triple_play": {"value": 36, "scale": "CODE_EVENT"},
        "walk": {"value": 40, "scale": "CODE_EVENT"}, 
        "intent_walk": {"value": 41, "scale": "CODE_EVENT"}, 
        "hit_by_pitch": {"value": 42, "scale": "CODE_EVENT"}, 
        "field_error": {"value": 43, "scale": "CODE_EVENT"},
        "catcher_interf": {"value": 44, "scale": "CODE_EVENT"}, 
        "batter_interference": {"value": 45, "scale": "CODE_EVENT"},
        "wild_pitch": {"value": 50, "scale": "CODE_EVENT"}, 
        "passed_ball": {"value": 51, "scale": "CODE_EVENT"}, 
        "balk": {"value": 52, "scale": "CODE_EVENT"}, 
        "forced_balk": {"value": 53, "scale": "CODE_EVENT"}, 
        "other_out": {"value": 54, "scale": "CODE_EVENT"},
    }

    # --- LLAMADAS DEL UMPIRE Y RESULTADOS DE PITCH (PITCH_CALLS) ---
    PITCH_CALLS = {
        "C": {"value": 1, "scale": "CODE_PITCH"},
        "S": {"value": 2, "scale": "CODE_PITCH"},
        "F": {"value": 3, "scale": "CODE_PITCH"},
        "T": {"value": 4, "scale": "CODE_PITCH"},
        "L": {"value": 5, "scale": "CODE_PITCH"},
        "M": {"value": 6, "scale": "CODE_PITCH"},
        "O": {"value": 7, "scale": "CODE_PITCH"},
        "W": {"value": 8, "scale": "CODE_PITCH"},
        "K": {"value": 9, "scale": "CODE_PITCH"},
        "A": {"value": 10, "scale": "CODE_PITCH"},
        "AC": {"value": 11, "scale": "CODE_PITCH"},
        "AB": {"value": 12, "scale": "CODE_PITCH"},
        "R": {"value": 13, "scale": "CODE_PITCH"},
        "Q": {"value": 14, "scale": "CODE_PITCH"},
        "B": {"value": 20, "scale": "CODE_PITCH"},
        "*B": {"value": 21, "scale": "CODE_PITCH"},
        "I": {"value": 22, "scale": "CODE_PITCH"},
        "P": {"value": 23, "scale": "CODE_PITCH"},
        "H": {"value": 24, "scale": "CODE_PITCH"},
        "V": {"value": 25, "scale": "CODE_PITCH"},
        "VB": {"value": 26, "scale": "CODE_PITCH"},
        "VC": {"value": 27, "scale": "CODE_PITCH"},
        "VP": {"value": 28, "scale": "CODE_PITCH"},
        "VS": {"value": 29, "scale": "CODE_PITCH"},
        "X": {"value": 40, "scale": "CODE_PITCH"},
        "D": {"value": 41, "scale": "CODE_PITCH"},
        "E": {"value": 42, "scale": "CODE_PITCH"},
        "Y": {"value": 43, "scale": "CODE_PITCH"},
        "J": {"value": 44, "scale": "CODE_PITCH"},
        "Z": {"value": 45, "scale": "CODE_PITCH"},
        "PSO": {"value": 50, "scale": "CODE_PITCH"},
        "N": {"value": 51, "scale": "CODE_PITCH"},
        ".": {"value": 52, "scale": "CODE_PITCH"},
        "1": {"value": 61, "scale": "CODE_PITCH"},
        "2": {"value": 62, "scale": "CODE_PITCH"},
        "3": {"value": 63, "scale": "CODE_PITCH"},
        "+1": {"value": 64, "scale": "CODE_PITCH"},
        "+2": {"value": 65, "scale": "CODE_PITCH"},
        "+3": {"value": 66, "scale": "CODE_PITCH"}
    }

# --- CONDICIONES DEL JUEGO ---
class GameEnvironmentMappings:
    """
    Mapeo refactorizado para facilitar la inserción en tablas separadas.
    Mantiene compatibilidad total con DataTransformer[cite: 3, 6].
    """
    
    # TABLA: venues (Datos estáticos del estadio)
    VENUE = {
        "venue_id":      {"path": "id", "scale": DataScale.NONE},
        "venue_name":    {"path": "name", "scale": DataScale.NONE},
        "city":          {"path": "location.city", "scale": DataScale.NONE},
        "state":         {"path": "location.state", "scale": DataScale.NONE},
        "turf_type":     {"path": "fieldInfo.turfType", "scale": DataScale.NONE},
        "roof_type":     {"path": "fieldInfo.roofType", "scale": DataScale.NONE},
        "capacity":      {"path": "fieldInfo.capacity", "scale": DataScale.COUNT},
        "elevation":     {"path": "location.elevation", "scale": DataScale.COUNT},
        "left_line":     {"path": "fieldInfo.leftLine", "scale": DataScale.COUNT},
        "left":          {"path": "fieldInfo.left", "scale": DataScale.COUNT},
        "left_center":   {"path": "fieldInfo.leftCenter", "scale": DataScale.COUNT},
        "center_field":  {"path": "fieldInfo.center", "scale": DataScale.COUNT},
        "right_center":  {"path": "fieldInfo.rightCenter", "scale": DataScale.COUNT},
        "right":         {"path": "fieldInfo.right", "scale": DataScale.COUNT},
        "right_line":    {"path": "fieldInfo.rightLine", "scale": DataScale.COUNT},
        "latitude":      {"path": "location.defaultCoordinates.latitude", "scale": DataScale.PRECISE},
        "longitude":     {"path": "location.defaultCoordinates.longitude", "scale": DataScale.PRECISE},
        "azimuth_angle": {"path": "location.azimuthAngle", "scale": DataScale.METRIC},
    }

    # TABLA: game_context (Datos volátiles unidos por game_id)
    GAME_CONTEXT = {
        "datetime":      {"path": "datetime.dateTime", "scale": DataScale.DATE},
        "day_night":     {"path": "datetime.dayNight", "scale": DataScale.NONE},
        "temperature":   {"path": "weather.temp", "scale": DataScale.COUNT},
        "condition":     {"path": "weather.condition", "scale": DataScale.NONE},
        "wind":          {"path": "weather.wind", "scale": DataScale.NONE},
        "umpire_id":     {"path": "umpire.id", "scale": DataScale.NONE},
        "venue_id":      {"path": "venue.id", "scale": DataScale.NONE},
        "home_id":       {"path": "venue.id", "scale": DataScale.NONE},
        "away_id":       {"path": "venue.id", "scale": DataScale.NONE},
    }

# --- JUGADORES ---
class PlayerMappings:
    """
    DOMINIO DE JUGADOR: Especificación de identidad y rendimiento.
    
    Responsabilidad: Centralizar los mapeos de la API de MLB hacia el esquema 
    de la DB para las entidades de Jugador, Bateador y Lanzador.
    """

    # --- SECCIÓN BIO: Identidad y Atributos Físicos ---
    BIO = {
        "player_id":       {"path": "id", "scale": DataScale.NONE},
        "debut":           {"path": "mlbDebutDate", "scale": DataScale.DATE},
        "full_name":       {"path": "fullName", "scale": DataScale.NONE},
        "age":             {"path": "currentAge", "scale": DataScale.NONE},
        "weight":          {"path": "weight", "scale": DataScale.NONE},
        "height":          {"path": "height", "scale": DataScale.HEIGHT},
        "position_code":   {"path": "primaryPosition.code", "scale": DataScale.NONE},
        "bat_side_code":   {"path": "batSide.code", "scale": DataScale.NONE},
        "pitch_hand_code": {"path": "pitchHand.code", "scale": DataScale.NONE},
        "sz_top":          {"path": "strikeZoneTop", "scale": DataScale.PRECISE},
        "sz_bottom":       {"path": "strikeZoneBottom", "scale": DataScale.PRECISE},
    }

    # --- SECCIÓN STATS: Rendimiento en Juego (Boxscore) ---
    
    HITTER = {
        "player_id":     {"path": "person.id", "scale": DataScale.NONE},
        "pa":            {"path": "stats.batting.plateAppearances", "scale": DataScale.COUNT},
        "ab":            {"path": "stats.batting.atBats", "scale": DataScale.COUNT},
        "h":             {"path": "stats.batting.hits", "scale": DataScale.COUNT},
        "d":             {"path": "stats.batting.doubles", "scale": DataScale.COUNT},
        "t":             {"path": "stats.batting.triples", "scale": DataScale.COUNT},
        "hr":            {"path": "stats.batting.homeRuns", "scale": DataScale.COUNT},
        "bb":            {"path": "stats.batting.baseOnBalls", "scale": DataScale.COUNT},
        "k":             {"path": "stats.batting.strikeOuts", "scale": DataScale.COUNT},
        "hbp":           {"path": "stats.batting.hitByPitch", "scale": DataScale.COUNT},
        "sf":            {"path": "stats.batting.sacrificeFlies", "scale": DataScale.COUNT},
        "sh":            {"path": "stats.batting.sacrificeBunts", "scale": DataScale.COUNT},
    }

    PITCHER = {
        "player_id":     {"path": "person.id", "scale": DataScale.NONE},
        "innings_pitched": {"path": "stats.pitching.inningsPitched", "scale": DataScale.METRIC},
        "er":            {"path": "stats.pitching.earnedRuns", "scale": DataScale.COUNT},
        "h":             {"path": "stats.pitching.hits", "scale": DataScale.COUNT},
        "k":             {"path": "stats.pitching.strikeOuts", "scale": DataScale.COUNT},
        "bb":            {"path": "stats.pitching.walks", "scale": DataScale.COUNT},
        "hr":            {"path": "stats.pitching.homeRuns", "scale": DataScale.COUNT},
    }

    HISTORICAL = {
        "hitting": {
            "avg":   {"path": "avg", "scale": DataScale.PRECISE},
            "obp":   {"path": "obp", "scale": DataScale.PRECISE},
            "slg":   {"path": "slg", "scale": DataScale.PRECISE},
            "ops":   {"path": "ops", "scale": DataScale.PRECISE},
            "babip": {"path": "babip", "scale": DataScale.PRECISE}
        },
        "pitching": {
            "era":   {"path": "era", "scale": DataScale.PRECISE}, # x1000 en DB
            "whip":  {"path": "whip", "scale": DataScale.PRECISE}, # x1000 en DB
            "fip":   {"path": "fip", "scale": DataScale.PRECISE}   # x1000 en DB
        }
    }

# --- STATCAST ---
class StatcastMappings:
    """Mapeo de métricas de radar sincronizado con tabla stc_pitches."""
    AT_BAT = {
        # --- Identificadores de Contexto ---
        "at_bat_id":     {"path": "at_bat_id", "scale": DataScale.NONE}, 
        "game_id":       {"path": "game_id", "scale": DataScale.NONE},
        "pitcher_id":    {"path": "pitcher_id", "scale": DataScale.NONE}, 
        "batter_id":     {"path": "batter_id", "scale": DataScale.NONE},
        "inning":        {"path": "inning", "scale": DataScale.COUNT},
        
        # --- Resultado del Turno ---
        "event_type":    {"path": "result.eventType", "scale": DataScale.NONE},
        "event_code":    {"path": "result.event", "scale": DataScale.NONE},
        "is_out":        {"path": "result.isOut", "scale": DataScale.NONE},
        "rbi":           {"path": "result.rbi", "scale": DataScale.COUNT},
        "away_score":    {"path": "result.awayScore", "scale": DataScale.COUNT},
        "home_score":    {"path": "result.homeScore", "scale": DataScale.COUNT},
    }

    PITCH = {
        # --- Identificadores +---
        "at_bat_id":     {"path": "at_bat_id", "scale": DataScale.NONE}, 
        "game_id":       {"path": "game_id", "scale": DataScale.NONE},
        "pitcher_id":    {"path": "pitcher_id", "scale": DataScale.NONE},
        "batter_id":     {"path": "batter_id", "scale": DataScale.NONE},
        "inning":        {"path": "inning", "scale": DataScale.COUNT},
        "pitch_number":  {"path": "pitchNumber", "scale": DataScale.COUNT},
        
        # --- Estado del Juego ---
        "balls":         {"path": "count.balls", "scale": DataScale.COUNT},
        "strikes":       {"path": "count.strikes", "scale": DataScale.COUNT},
        "outs":          {"path": "count.outs", "scale": DataScale.COUNT},

        # --- Análisis de Lanzamiento y Arbitraje ---
        "pitch_type":    {"path": "details.type.code", "scale": DataScale.NONE},
        "event_code":    {"path": "details.code", "scale": DataScale.NONE},      
        "zone":          {"path": "pitchData.zone", "scale": DataScale.COUNT},   

        # --- Datos Físicos de lanzamiento (Coordenadas restauradas) ---
        "velocity":      {"path": "pitchData.startSpeed", "scale": DataScale.METRIC},
        "px":            {"path": "pitchData.coordinates.pX", "scale": DataScale.PRECISE},
        "pz":            {"path": "pitchData.coordinates.pZ", "scale": DataScale.PRECISE},
        "sz_top":        {"path": "pitchData.strikeZoneTop", "scale": DataScale.PRECISE},
        "sz_bottom":     {"path": "pitchData.strikeZoneBottom", "scale": DataScale.PRECISE},

        # --- Datos de contacto (hitData completo) ---
        "launch_speed":  {"path": "hitData.launchSpeed", "scale": DataScale.METRIC},
        "launch_angle":  {"path": "hitData.launchAngle", "scale": DataScale.COUNT},
        "total_distance":{"path": "hitData.totalDistance", "scale": DataScale.COUNT},
        "hit_trajectory":{"path": "hitData.trajectory", "scale": DataScale.NONE},
        "hit_location":  {"path": "hitData.location", "scale": DataScale.NONE},
    }