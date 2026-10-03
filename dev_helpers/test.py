import asyncio
import json
from src.dxbaseball_bets.core.services.extractors.game_extractor import GameExtractor
from src.dxbaseball_bets.core.engine.game_processor import GameProcessor
from src.dxbaseball_bets.core.engine.processor import DataProcessor
from src.dxbaseball_bets.core.config.data_contract import GameEnvironmentMappings as GEM
from src.dxbaseball_bets.utils.logger import logger

async def run_scale_debug_test(game_id: int):
    extractor = GameExtractor()
    data_processor = DataProcessor()
    processor = GameProcessor()
    
    raw_package = extractor.get_data_package(game_id)
    game_processed = processor.process_full_game(raw_package)

    print(game_processed.get("teams", {}))

if __name__ == "__main__":
    asyncio.run(run_scale_debug_test(748537))