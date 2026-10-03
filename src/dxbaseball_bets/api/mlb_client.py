import statsapi
from datetime import datetime
from typing import Dict, Any, Optional, List, Union
from src.dxbaseball_bets.utils.logger import logger

class MLBClient:
    """
    Cliente Blindado para la API de MLB.
    Única fuente de verdad para la obtención de datos crudos.
    """
    
    def __init__(self):
        self.current_year = datetime.now().year
        logger.debug(f"Sincronizando MLBClient - Temporada {self.current_year}")

    def get_game_ids_by_date(self, target_date: Optional[Union[str, datetime]] = None) -> List[int]:
        """
        Obtiene exclusivamente los IDs (gamePk) de los juegos para una fecha.
        
        Args:
            target_date: Puede ser un string 'MM/DD/YYYY' o un objeto datetime.
            Si es None, usa la fecha actual.
        Returns:
            Lista de enteros con los IDs de los juegos.
        """
        if isinstance(target_date, datetime):
            date_str = target_date.strftime('%m/%d/%Y')
        else:
            date_str = target_date or datetime.now().strftime('%m/%d/%Y')

        try:
            # Usamos el método schedule de statsapi que ya manejas
            schedule = statsapi.schedule(date=date_str)
            
            # Extraemos únicamente los IDs que tengan un estado de juego válido
            # Podrías añadir filtros aquí (ej. solo juegos finalizados)
            game_ids = [
                game['game_id'] for game in schedule 
                if game.get('game_id')
            ]
            
            logger.info(f"MLB_API: {len(game_ids)} IDs de juegos encontrados para {date_str}")
            return game_ids
            
        except Exception as e:
            logger.error(f"Error al obtener IDs de juegos para {date_str}: {e}")
            return []

    def get_player_stats(self, player_id: Union[str, int], group: str, stat_type: str = "career") -> Dict[str, Any]:
        """
        Obtiene estadísticas de un jugador (Carrera o Temporada).
        Blindaje: Limpia prefijos de ID y centraliza la captura de errores.
        """
        try:
            clean_id = str(player_id).lower().replace("id", "")
            logger.info(f"MLB_API: Solicitando {stat_type} para ID {clean_id} (Grupo: {group})")
            
            data = statsapi.player_stat_data(clean_id, group=group, type=stat_type)
            
            if not data or 'stats' not in data or not data['stats']:
                logger.warning(f"MLB_API: Sin contenido para ID {clean_id}")
                return {}
            
            return data['stats'][0]['stats']
            
        except Exception as e:
            logger.error(f"Error de conexión en MLBClient (Jugador {player_id}): {e}")
            return {}

    def get_live_feed(self, game_id: int) -> Optional[Dict[str, Any]]:
        """
        Obtiene el 'Live Feed' completo (Statcast y Boxscore).
        """
        try:
            logger.info(f"MLB_API: Descargando feed del juego {game_id}")
            data = statsapi.get('game', {'gamePk': game_id})
            
            if not data or 'message' in data:
                logger.warning(f"MLB_API: El ID {game_id} no devolvió datos válidos")
                return None
            
            return data
        except Exception as e:
            logger.exception(f"Falla crítica al obtener feed del juego {game_id}: {e}")
            return None

    def get_day_schedule(self, date: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Consulta el calendario de juegos completo para una fecha específica (MM/DD/YYYY).
        """
        target_date = date or datetime.now().strftime('%m/%d/%Y')
        try:
            schedule = statsapi.schedule(date=target_date)
            logger.info(f"MLB_API: {len(schedule)} juegos encontrados para {target_date}")
            return schedule
        except Exception as e:
            logger.error(f"Error al consultar calendario ({target_date}): {e}")
            return []