from typing import Dict, Any, List
from src.dxbaseball_bets.core.engine.processor import DataProcessor
from src.dxbaseball_bets.core.config.data_contract import (
    GameEnvironmentMappings as GEM,
    StatcastMappings as STCMAP,
    PlayerMappings as PMAP,
)

from src.dxbaseball_bets.utils.logger import logger

class GameProcessor:
    """
    TRADUCTOR DE NEGOCIO: Orquestador de transformaciones por dominios.
    Responsabilidad: Segmentar el paquete de la API y coordinar el flujo 
    hacia el DataProcessor utilizando contextos de ejecución[cite: 7, 12].
    """
    def __init__(self):
        self.processor = DataProcessor()
        self.statcast_transformer = StatcastTransformer(self.processor)

    def process_full_game(self, pkg: Dict[str, Any]) -> Dict[str, Any]:
        """Orquestador principal actualizado para mappings planos."""
        gid = pkg["game_id"]
        env_block = pkg["environment_block"]
        live_block = pkg["live_events_block"]

        # Transformación de Statcast (At-Bats y Pitches)
        statcast = self.statcast_transformer.transform(
            gid, 
            live_block.get('plays', {}).get('allPlays', [])
        )

        return {
            "game_id":            gid,
            "venue":              self._process_venue(env_block),        
            "game_context":       self._process_game_context(gid, env_block), 
            "teams":              self._process_teams(env_block),         
            "at_bats":            statcast["at_bats"],
            "pitches":            statcast["pitches"],
            "hitter_performance":  self._process_performance(live_block, "hitter"),
            "pitcher_performance": self._process_performance(live_block, "pitcher"),
            "players_registry":    self._process_players_registry(env_block),
        }

    # --- FUNCIONES DE MAPEO INDEPENDIENTES ---

    def _process_venue(self, env_block: Dict) -> Dict:
        """Procesa la información estática del estadio."""
        venue_raw = env_block.get("venue", {})
        return self.processor.process_data(venue_raw, GEM.VENUE)

    def _process_game_context(self, game_id: int, env_block: Dict) -> Dict:
        """
        Une clima, fecha y umpire en un solo bloque de contexto.
        Inyecta el game_id manualmente al contexto para la transformación.
        """
        # Construimos el objeto plano que espera GEM.GAME_CONTEXT
        context_raw = {
            "game_id":  game_id,
            "datetime": env_block.get("datetime", {}),
            "weather":  env_block.get("weather", {}),
            "umpire":   env_block.get("umpire", {}),
            "venue":    env_block.get("venue", {})
        }
        # Pasamos el contexto explícito para que el mapper resuelva los paths
        return self.processor.process_data(context_raw, GEM.GAME_CONTEXT)

    def _process_teams(self, env_block: Dict) -> List[Dict]:
        """Extrae la información de ambos equipos usando GEM.TEAM."""
        teams_raw = env_block.get("teams", {})
        return [
            self.processor.process_data(teams_raw.get("home", {}), GEM.TEAM),
            self.processor.process_data(teams_raw.get("away", {}), GEM.TEAM)
        ]

    def _process_statcast(self, game_id: int, live_block: Dict) -> List[Dict]:
        """
        Resuelve la jerarquía Play -> Event inyectando contexto de At-Bat[cite: 9, 12].
        """
        all_plays = live_block.get('plays', {}).get('allPlays', [])
        processed_pitches = []

        for play in all_plays:
            # Definición del contexto del At-Bat para el motor de mapeo[cite: 7, 8]
            at_bat_context = {
                "play_id_int": game_id,
                "pitcher_id":  self.processor.mapper.get_nested_value(play, 'matchup.pitcher.id'),
                "batter_id":   self.processor.mapper.get_nested_value(play, 'matchup.batter.id'),
                "inning":      self.processor.mapper.get_nested_value(play, 'about.inning')
            }
            
            # Filtramos solo eventos de pitcheo[cite: 12]
            pitch_events = [e for e in play.get('playEvents', []) if e.get('isPitch')]
            
            if pitch_events:
                # El DataProcessor usará el contexto para llenar los campos ausentes en el evento[cite: 10, 11]
                batch = self.processor.batch_process(pitch_events, STCMAP.PITCH, context=at_bat_context)
                processed_pitches.extend(batch)

        return processed_pitches

    def _process_performance(self, live_block: Dict, role: str) -> List[Dict]:
        """Procesa las estadísticas del boxscore para bateadores o lanzadores[cite: 12]."""
        teams_box = live_block.get('boxscore', {}).get('teams', {})
        mapping = PMAP.HITTER if role == "hitter" else PMAP.PITCHER
        stat_key = "batting" if role == "hitter" else "pitching"
        
        flat_results = []
        for side in ["home", "away"]:
            players = list(teams_box.get(side, {}).get('players', {}).values())
            # Filtrado por actividad en el rol específico[cite: 12]
            active_players = [p for p in players if p.get('stats', {}).get(stat_key)]
            
            if active_players:
                flat_results.extend(self.processor.batch_process(active_players, mapping))
        
        return flat_results

    def _process_teams(self, env_block: Dict) -> List[Dict]:
        """Extrae la información básica de ambos equipos[cite: 12]."""
        teams_raw = env_block.get("teams", {})
        return [+
            self.processor.process_data(teams_raw.get("home", {}), GEM.TEAM),
            self.processor.process_data(teams_raw.get("away", {}), GEM.TEAM)
        ]

    def _process_players_registry(self, env_block: Dict) -> List[Dict]:
        """Procesa el catálogo biográfico de todos los jugadores en el juego[cite: 12]."""
        players_list = list(env_block.get('players', {}).values())
        return self.processor.batch_process(players_list, PMAP.BIO)

class StatcastTransformer:
    """
    Encapsula la lógica de transformación de la jerarquía Statcast.
    Genera identidades únicas y desglosa At-Bats y Pitches [source: 1].
    """
    def __init__(self, processor: DataProcessor):
        self.processor = processor

    def transform(self, game_id: int, plays: List[Dict]) -> Dict[str, List[Dict]]:
        """
        Orquestador de transformación jerárquica [source: 1].
        """
        at_bats = []
        pitches = []

        for play in plays:
            # 1. Generar la Identidad Única del At-Bat
            # Usamos el atBatIndex de la API para garantizar orden y unicidad por juego
            play_idx = play.get('atBatIndex', 0)
            at_bat_id = self._generate_unique_id(game_id, play_idx)
            
            # 2. Construir el contexto para inyectar en los contratos
            context = self._build_context(game_id, at_bat_id, play)
            
            # 3. Procesar Entidades
            at_bats.append(self.processor.process_data(play, STCMAP.AT_BAT, context=context))
            
            # Extraer y procesar lanzamientos inyectando la misma identidad [source: 1]
            pitch_events = [e for e in play.get('playEvents', []) if e.get('isPitch')]
            if pitch_events:
                pitches.extend(self.processor.batch_process(pitch_events, STCMAP.PITCH, context=context))

        return {"at_bats": at_bats, "pitches": pitches}

    def _generate_unique_id(self, game_id: int, play_index: int) -> int:
        """
        Crea un ID numérico único para el At-Bat [source: 1].
        Formato: [GameID][Index de 3 dígitos] (Ej: 741234 + 005 = 741234005).
        """
        return (game_id * 1000) + play_index

    def _build_context(self, game_id: int, at_bat_id: int, play: Dict) -> Dict:
        """
        Centraliza la resolución de identidad y herencia [source: 1].
        """
        return {
            "at_bat_id":   at_bat_id,
            "game_id":     game_id,
            "pitcher_id":  self.processor.mapper.get_nested_value(play, 'matchup.pitcher.id'),
            "batter_id":   self.processor.mapper.get_nested_value(play, 'matchup.batter.id'),
            "inning":      self.processor.mapper.get_nested_value(play, 'about.inning')
        }