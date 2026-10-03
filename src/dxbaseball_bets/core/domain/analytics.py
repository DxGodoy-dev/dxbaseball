from typing import Dict, Any, List
from src.dxbaseball_bets.core.domain.formulas import (
    calculate_woba, calculate_fip, calculate_iso
)
from src.dxbaseball_bets.core.engine.analytics_bridge import AnalyticsBridge
from src.dxbaseball_bets.core.config.data_contract import GameEnvironmentMappings as GEM
from src.dxbaseball_bets.utils.logger import logger

class DailyStatsAnalytics:
    """
    Servicio de Analítica de Corto Plazo.
    Responsabilidad: Cálculo de métricas avanzadas sobre valores des-escalados.
    """
    def __init__(self, constants: Dict[str, float]):
        self.constants = constants

    def process_hitter_performance(self, flat_hitters: List[Dict], game_id: int) -> List[Dict]:
            """
            Calcula wOBA e ISO sobre una lista de bateadores ya aplanada y mapeada.
            """
            bridge = AnalyticsBridge(GEM.HITTER)
            hitter_records = []
            
            for stats in flat_hitters:
                # El bridge ahora recibe un dict mapeado, no un objeto de la API[cite: 9, 13].
                if stats.get('pa', 0) == 0:
                    continue

                # 1. Traducción a Floats (Des-escalado)
                clean_stats = bridge.prepare_for_calculation(stats)

                # 2. Cálculo matemático puro[cite: 12, 13]
                metrics = {
                    "iso": calculate_iso(
                        h=clean_stats.get('h', 0), d=clean_stats.get('d', 0), 
                        t=clean_stats.get('t', 0), hr=clean_stats.get('hr', 0), 
                        ab=clean_stats.get('ab', 0)
                    ),
                    "woba": calculate_woba(
                        h=clean_stats.get('h', 0), d=clean_stats.get('d', 0), 
                        t=clean_stats.get('t', 0), hr=clean_stats.get('hr', 0), 
                        bb=clean_stats.get('bb', 0), ab=clean_stats.get('ab', 0)
                    )
                }
                
                # 3. Re-escalado de resultados (woba/iso -> SCALE_1000)[cite: 5, 9]
                scaled_metrics = bridge.finalize_calculation(metrics)
                
                performance_record = {
                    "game_id": game_id,
                    "player_id": stats.get("player_id"),
                    **scaled_metrics 
                }
                hitter_records.append(performance_record)
                    
            return hitter_records

    def process_pitcher_performance(self, flat_pitchers: List[Dict], game_id: int) -> List[Dict]:
        """Calcula FIP sobre una lista de lanzadores ya mapeada[cite: 13]."""
        bridge = AnalyticsBridge(GEM.PITCHER)
        pitcher_records = []
        c_fip = self.constants.get("cFIP", 3.10)

        for stats in flat_pitchers:
            # Ahora 'stats' es un dict con llaves como 'innings_pitched', 'hr', etc.[cite: 14]
            clean_stats = bridge.prepare_for_calculation(stats)
            
            if clean_stats.get('innings_pitched', 0) == 0:
                continue

            metrics = {
                "fip": calculate_fip(
                    hr=clean_stats.get('hr', 0),
                    bb=clean_stats.get('bb', 0),
                    k=clean_stats.get('k', 0),
                    ip=clean_stats.get('innings_pitched', 0),
                    constant_c=c_fip
                )
            }

            scaled_metrics = bridge.finalize_calculation(metrics)
            
            pitcher_records.append({
                "game_id": game_id,
                "player_id": stats.get("player_id"),
                **scaled_metrics
            })
                
        return pitcher_records