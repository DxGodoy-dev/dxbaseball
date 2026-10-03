import asyncio
from datetime import date
from src.dxbaseball_bets.core.services.game_coordinator import GameCoordinator
from src.dxbaseball_bets.api.mlb_client import MLBClient
from src.dxbaseball_bets.database.session_manager import SessionManager
from src.dxbaseball_bets.utils.logger import logger

async def load_yesterday_games():
    # 1. Configuración de dependencias
    db = SessionLocal()
    mlb_client = MLBClient()
    coordinator = GameCoordinator(db)
    
    target_date = date(2026, 4, 28)
    logger.info(f"Iniciando carga masiva para la fecha: {target_date}")

    try:
        # 2. Obtener IDs de juegos para la fecha
        # Asumiendo que mlb_client tiene un método para listar juegos por fecha
        game_ids = mlb_client.get_game_ids_by_date(target_date)
        
        if not game_ids:
            logger.warning(f"No se encontraron juegos para el {target_date}")
            return

        logger.info(f"Se encontraron {len(game_ids)} juegos. Iniciando procesamiento...")

        # 3. Ejecución Secuencial
        # Procesamos uno a uno para validar la integridad y manejar logs limpiamente
        for g_id in game_ids:
            try:
                logger.info(f"[*] Procesando juego: {g_id}")
                await coordinator.process_and_save_game(g_id)
                logger.info(f"[OK] Juego {g_id} completado con éxito.")
            except Exception as e:
                # El sistema no se detiene si un juego falla; loguea y sigue.
                logger.error(f"[FALLO] Error en juego {g_id}: {str(e)}")
                continue

        logger.info("== PROCESAMIENTO DE JORNADA FINALIZADO ==")

    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(load_yesterday_games())