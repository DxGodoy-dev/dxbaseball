from typing import Dict, Any, Optional
from src.dxbaseball_bets.api.mlb_client import MLBClient
from src.dxbaseball_bets.utils.logger import logger

class GameExtractor:
    """
    EXTRACTOR DE INFRAESTRUCTURA: Localiza y provee datos crudos.
    Responsabilidad: Centralizar el acceso a la API y segmentar los bloques 
    principales del JSON sin transformar valores[cite: 1, 5].
    """

    def __init__(self):
        self.client = MLBClient()

    def get_data_package(self, game_id: int) -> Optional[Dict[str, Any]]:
        """
        Descarga el feed y entrega un DTO segmentado por dominios[cite: 1].
        """
        try:
            raw_feed = self.client.get_live_feed(game_id)
            if not raw_feed:
                logger.warning(f"Feed vacío o no encontrado para el juego {game_id}")
                return None

            officials = raw_feed.get('liveData', {}).get('boxscore', {}).get('officials', [])
            hp_umpire = next((o.get('official') for o in officials if o.get('officialType') == 'Home Plate'), {})

            return {
                "game_id": game_id,
                "environment_block": {
                    **raw_feed.get('gameData', {}),
                    "umpire": hp_umpire
                }, 
                    "live_events_block": raw_feed.get('liveData', {})
                }
            
        except Exception as e:
            logger.error(f"Error de red o acceso en el extractor para el juego {game_id}: {e}")
            return None