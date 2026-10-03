from typing import Dict, Any
from src.dxbaseball_bets.database.repositories.base_repo import BaseRepo
from src.dxbaseball_bets.database.db_models import Player

class PlayerRepo(BaseRepo[Player]):
    def __init__(self, session):
        super().__init__(Player, session)

    def sync_from_registry(self, players_data: Dict[str, Any]) -> None:
        """
        Sincroniza perfiles de jugadores delegando el filtrado al BaseRepo[cite: 8].
        """
        for p_info in players_data.values():
            if not p_info.get('id'):
                continue
            
            # Mapeo de campos del extractor a nombres de la DB
            mapped_data = {
                'id': int(p_info['id']),
                'full_name': p_info.get('fullName'),
                'bat_side': p_info.get('batSide', {}).get('code'),
                'pitch_hand': p_info.get('pitchHand', {}).get('code'),
                'primary_position': p_info.get('primaryPosition', {}).get('code')
            }

            # Usamos el motor central de persistencia[cite: 8]
            self.upsert_data(Player, mapped_data)