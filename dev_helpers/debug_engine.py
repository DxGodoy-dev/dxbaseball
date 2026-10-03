import json
import os
import sys
# IMPORTACIONES REALES DE TU PROYECTO
from src.dxbaseball_bets.core.engine.game_processor import GameProcessor
from src.dxbaseball_bets.core.config.data_contract import GameEnvironmentMappings as GEM

def debug_live_mapping():
    # 1. EL JSON REAL QUE NOS PASASTE
    raw_env_block = {
        'game': {'pk': 748537},
        'datetime': {
            'dateTime': '2023-10-25T00:07:00Z',
            'officialDate': '2023-10-24'
        }
    }

    # 2. INSTANCIA REAL DEL PROCESADOR
    # Esto probará si tu DataProcessor interno está bien configurado
    gp = GameProcessor()
    
    print("=== DEBUG DE INTEGRIDAD DE DATOS ===")
    
    # 3. PRUEBA DE NAVEGACIÓN (Ruta del Contrato)
    path_en_contrato = GEM.DATE["datetime"]["path"]
    print(f"Path definido en GEM.DATE: '{path_en_contrato}'")
    
    # Intentamos extraer usando el mapper real de tu DataProcessor
    extracted_val = gp.processor.mapper.get_nested_value(raw_env_block, path_en_contrato)
    
    if extracted_val:
        print(f"✅ VALOR EXTRAÍDO: {extracted_val}")
    else:
        print(f"❌ FALLO DE EXTRACCIÓN: El mapper devolvió None para el path '{path_en_contrato}'")
        print(f"Estructura recibida por el mapper: {list(raw_env_block.keys())}")

    # 4. PRUEBA DE CONTEXTO (at_bat_id)
    # Simulamos lo que hace el StatcastTransformer
    test_context = {"at_bat_id": 748537001, "game_id": 748537}
    
    # Probamos el procesamiento de una entidad pequeña usando el contexto
    # Usamos un diccionario vacío como 'data' porque queremos ver si saca el ID del contexto
    processed_at_bat = gp.processor.process_data({}, STCMAP.AT_BAT, context=test_context)
    
    at_bat_id_result = processed_at_bat.get("at_bat_id")
    
    if at_bat_id_result:
        print(f"✅ CONTEXTO OK: at_bat_id procesado como {at_bat_id_result}")
    else:
        print(f"❌ FALLO DE CONTEXTO: El procesador ignoró el at_bat_id del contexto.")
        print(f"Resultado del process_data: {processed_at_bat}")

if __name__ == "__main__":
    try:
        debug_live_mapping()
    except Exception as e:
        print(f"💥 ERROR DE IMPORTACIÓN O EJECUCIÓN: {e}")