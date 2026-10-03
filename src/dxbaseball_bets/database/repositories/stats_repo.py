from typing import Dict, Any, Type
from src.dxbaseball_bets.database.repositories.base_repo import BaseRepo
from src.dxbaseball_bets.database.db_models import (
    Pitch, AtBat, HitterPerformanceDaily, 
    PitcherPerformanceDaily, InningMetric, Base
)

class StatsRepo(BaseRepo[Base]):
    """
    Gestiona la persistencia de eventos Statcast y métricas analíticas aisladas.
    """
    
    # Mapeo de llaves del payload a modelos de base de datos
    MODEL_MAP: Dict[str, Type[Base]] = {
        'stc_pitches': Pitch,
        'stc_at_bats': AtBat,
        'hitter_performance': HitterPerformanceDaily,
        'pitcher_performance': PitcherPerformanceDaily,
        'inning_metrics': InningMetric
    }

    def __init__(self, session):
        # Inicializamos con Base para soportar múltiples modelos en un solo repo
        super().__init__(Base, session)

    def persist_facts(self, results: Dict[str, Any]) -> None:
        """
        Itera sobre los resultados analíticos y los guarda masivamente.
        Delegamos el filtrado de columnas al motor de BaseRepo.
        """
        for key, model_class in self.MODEL_MAP.items():
            records = results.get(key, [])
            
            if not isinstance(records, list) or not records:
                continue

            for record in records:
                # El payload ya viene con tipos correctos (Fixed-Point Integers)[cite: 3, 4, 7]
                self.upsert_data(model_class, record)

    def clear_existing_game_data(self, game_id: int) -> None:
        """
        Elimina registros previos de un juego para permitir re-procesamiento limpio.
        """
        for model_class in self.MODEL_MAP.values():
            self.session.query(model_class).filter(model_class.game_id == game_id).delete()
        
        self.session.flush()