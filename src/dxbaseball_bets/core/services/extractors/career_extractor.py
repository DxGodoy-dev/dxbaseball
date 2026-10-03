from typing import Dict, Any, Optional
from src.dxbaseball_bets.api.mlb_client import MLBClient
from src.dxbaseball_bets.core.engine.processor import DataProcessor
from src.dxbaseball_bets.core.config.data_contract import CareerMappings
from src.dxbaseball_bets.utils.logger import logger

class CareerExtractor:
    """
    Especialista en datos históricos y de carrera.
    Delega la transformación de promedios (Fixed-Point) al DataProcessor.
    """

    def __init__(self):
        self.client = MLBClient()
        self.processor = DataProcessor() # Nuevo motor centralizado[cite: 2]
        self.mappings = CareerMappings()

    def get_career_payload(self, player_id: int, group: str) -> Dict[str, Any]:
        """
        Obtiene datos de por vida y los transforma en el formato del contrato.
        """
        clean_id = self._sanitize_player_id(player_id)

        # 1. Obtención de datos crudos
        raw_stats = self.client.get_player_stats(clean_id, group=group, stat_type="career")
        
        if not raw_stats:
            logger.warning(f"CareerExtractor: Sin datos para ID {player_id} en grupo {group}")
            return {}

        # 2. Selección del mapeo contractual
        mapping = self.mappings.HISTORICAL.get(group)
        if not mapping:
            logger.error(f"CareerExtractor: El grupo '{group}' no definido en CareerMappings")
            return {}

        # 3. Transformación Unificada
        # El Processor ahora maneja el escalamiento y evita errores de tipo
        payload = self.processor.process_data(raw_stats, mapping)
        
        if not payload:
            return {}

        # 4. Inyección de Identidad
        payload['player_id'] = clean_id
        
        return payload

    def _sanitize_player_id(self, pid: Any) -> int:
        """Limpia prefijos de ID y asegura retorno de entero."""
        try:
            return int(str(pid).upper().replace("ID", ""))
        except (ValueError, TypeError):
            logger.error(f"CareerExtractor: Error al sanitizar ID: {pid}")
            return 0