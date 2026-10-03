from typing import Dict
from src.dxbaseball_bets.core.services.extractors.game_extractor import GameExtractor
from src.dxbaseball_bets.core.engine.game_processor import GameProcessor

# Repositorios de Persistencia
from src.dxbaseball_bets.database.repositories.player_repo import PlayerRepo
from src.dxbaseball_bets.database.repositories.game_repo import GameRepo
from src.dxbaseball_bets.database.repositories.stats_repo import StatsRepo

from src.dxbaseball_bets.utils.logger import logger

class GameCoordinator:
    """
    ORQUESTADOR ATÓMICO: Gestiona el ciclo de vida de la persistencia de un juego.
    Flujo: Extracción -> Procesamiento -> Persistencia.
    """

    def __init__(self, session, constants: Dict[str, float]):
        self.session = session
        # Motores
        self.extractor = GameExtractor()
        self.processor = GameProcessor(constants)
        
        # Repositorios
        self.player_repo = PlayerRepo(session)
        self.game_repo = GameRepo(session)
        self.stats_repo = StatsRepo(session)

    def process_and_save_game(self, game_id: int) -> None:
        """
        Ejecuta la tubería completa de un encuentro.
        """
        try:

            # 1. EXTRACCIÓN: Obtención de datos crudos
            raw_package = self.extractor.get_data_package(game_id)
            if not raw_package:
                logger.warning(f"No se obtuvieron datos para el juego {game_id}")
                return

            # 2. PROCESAMIENTO: Transformación y Analítica
            # Ahora toda la complejidad de bridges y mapeos ocurre aquí.
            game_data = self.processor.process_full_game(raw_package)
            logger.debug("Paso 1.5 Completado")

            # 3. PERSISTENCIA: Sincronización de Identidades y Hechos

            # A. Limpieza previa para permitir re-procesamiento
            self.stats_repo.clear_existing_game_data(game_id)
            logger.debug("Paso 2 Completado")

            # B. Sincronización de dimensiones (Jugadores y Equipos)
            self.player_repo.sync_from_registry(game_data["players_registry"])
            self.game_repo.sync_teams(game_data["teams"])
            logger.debug("Paso 3 Completado")

            # C. Persistencia del entorno y cabecera[cite: 14]
            # El objeto 'environment' ya viene procesado con Venue y Weather.
            game_context = {
                "game_id": game_id,
                "game_date": game_data["game_date"],
                **game_data["environment"] 
            }
            self.game_repo.save_environment(game_context)
            self.game_repo.create_game_header(game_context)
            logger.debug("Paso 4 Completado")

            # D. Persistencia de hechos (Lanzamientos y Performance)[cite: 12]
            self.stats_repo.persist_facts({
                "stc_pitches": game_data["pitches"],
                "hitter_performance": game_data["hitter_performance"],
                "pitcher_performance": game_data["pitcher_performance"]
            })

            logger.debug("Paso 5 Completado")
            # 4. FINALIZACIÓN
            self.session.commit()
            logger.info(f"== JUEGO {game_id} COMPLETADO: ARQUITECTURA DESACOPLADA ==")
            logger.debug("Paso 6 Completado")
        except Exception as e:
            self.session.rollback()
            logger.error(f"Falla crítica en la orquestación del juego {game_id}: {e}")
            raise e