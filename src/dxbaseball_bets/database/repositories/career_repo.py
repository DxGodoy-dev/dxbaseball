from typing import Dict, Any, Type, Union
from src.dxbaseball_bets.database.repositories.base_repo import BaseRepo
from src.dxbaseball_bets.database.db_models import HitterCareerStats, PitcherCareerStats
from src.dxbaseball_bets.utils.logger import logger

class CareerRepo(BaseRepo):
    """
    Gestiona estadísticas de carrera (Hitting/Pitching) usando upsert centralizado[cite: 9].
    """
    def __init__(self, session):
        # Iniciamos con HitterCareerStats por defecto
        super().__init__(model=HitterCareerStats, session=session)
        
    def sync_career_stats(self, stats_data: Dict[str, Any], group: str) -> None:
        """
        Realiza el upsert dinámico según el grupo del jugador[cite: 9].
        """
        model_class: Type[Union[HitterCareerStats, PitcherCareerStats]] = (
            HitterCareerStats if group == "hitting" else PitcherCareerStats
        )
        
        player_id = stats_data.get("player_id")
        if not player_id:
            logger.error(f"Falta player_id en payload de carrera: {stats_data}")
            return

        try:
            # Delegación total al padre para filtrado e inserción[cite: 9]
            self.upsert_data(model_class, stats_data)
            self.session.flush()
            logger.debug(f"Carrera sincronizada: ID {player_id} ({group})")
            
        except Exception as e:
            logger.error(f"Error en CareerRepo para {player_id}: {e}")
            self.session.rollback()
            raise