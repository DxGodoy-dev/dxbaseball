from typing import Dict, List, Any
from src.dxbaseball_bets.database.repositories.base_repo import BaseRepo
from src.dxbaseball_bets.database.db_models import Venue, Umpire, Team, GameContext

class GameRepo(BaseRepo[GameContext]):
    """
    Repositorio para la gestión del entorno del juego y metadatos del encuentro.
    """
    def __init__(self, session):
        super().__init__(GameContext, session)

    def save_environment(self, context: Dict[str, Any]) -> None:
        """
        Persiste Venue y Umpire utilizando la lógica centralizada de upsert_data.
        """
        # A. Sincronizar Estadio (Venue)
        if venue_data := context.get("venue"):
            self.upsert_data(Venue, venue_data)

        # B. Sincronizar Umpire
        if ump_data := context.get("umpire", {}):
            if ump_data.get("id"):
                # Normalización: 'name' del extractor a 'full_name' de la DB
                if 'name' in ump_data and 'full_name' not in ump_data:
                    ump_data['full_name'] = ump_data.pop('name')
                
                self.upsert_data(Umpire, ump_data)

    def create_game_header(self, context: Dict[str, Any]) -> None:
        """
        Crea o actualiza la cabecera del encuentro. 
        """
        weather = context.get("weather", {})
        venue_id = context.get("venue", {}).get("id")
        umpire_id = context.get("umpire", {}).get("id")
        
        # Mapeo explícito para asegurar tipos e integridad de nombres
        header_data = {
            "game_id": int(context["game_id"]),
            "game_date": context.get("game_date"),
            "venue_id": int(venue_id) if venue_id else None,
            "home_plate_umpire_id": int(umpire_id) if umpire_id else None,
            "temperature": int(weather.get("temperature", 0)),
            "condition": weather.get("condition", "Unknown"),
            "wind": weather.get("wind")
        }
        
        self.upsert_data(GameContext, header_data)

    def sync_teams(self, teams_data: List[Dict[str, Any]]) -> None:
        """
        Sincroniza los equipos involucrados en el encuentro.
        """
        for team in teams_data:
            if team.get('id'):
                self.upsert_data(Team, team)