from datetime import datetime
from typing import List, Optional
from src.dxbaseball_bets.api.mlb_client import MLBClient
from src.dxbaseball_bets.utils.logger import logger

class GameDiscoveryService:
    def __init__(self, client: MLBClient):
        self.client = client

    def get_season_games(self, year: int, regular: bool = True, playoffs: bool = True) -> List[int]:
        """
        Obtiene todos los IDs de juegos de una temporada completa.
        """
        game_types = []
        if regular: game_types.append('R')
        if playoffs: game_types.append('P')
        
        all_ids = []
        
        for g_type in game_types:
            logger.info(f"Descubriendo juegos tipo '{g_type}' para la temporada {year}...")
            # Nota: MLB API v1/schedule permite filtrar por season y gameType
            # Usaremos el cliente para traer esta lista
            ids = self._fetch_ids_by_season(year, g_type)
            all_ids.extend(ids)
            
        return list(set(all_ids))

    def _fetch_ids_by_season(self, year: int, game_type: str) -> List[int]:
        """
        Lógica interna para consultar el schedule por año y tipo.
        """
        import statsapi
        try:
            # statsapi permite filtrar por año y tipo directamente
            schedule = statsapi.schedule(year=year, gameType=game_type)
            return [game['game_id'] for game in schedule if game.get('game_id')]
        except Exception as e:
            logger.error(f"Error al obtener temporada {year} [{game_type}]: {e}")
            return []

    def get_games_by_date(self, target_date: datetime) -> List[int]:
        """Consulta básica por fecha usando el cliente."""
        return self.client.get_game_ids_by_date(target_date)