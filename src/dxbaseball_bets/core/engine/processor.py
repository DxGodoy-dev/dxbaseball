from typing import Any, Dict, List, Union, Optional
from src.dxbaseball_bets.core.engine.mapper import DataMapper
from src.dxbaseball_bets.core.engine.transformer import DataTransformer
from src.dxbaseball_bets.utils.logger import logger

class DataProcessor:
    """
    Motor Central de Procesamiento Declarativo.
    Responsabilidad: Coordinar la extracción (Mapper) y el escalado (Transformer) 
    utilizando opcionalmente datos de contexto para resolver jerarquías complejas.
    """

    def __init__(self):
        self.mapper = DataMapper()
        self.transformer = DataTransformer()

    def process_data(
        self, 
        source: Union[Dict, List], 
        mapping: Dict[str, Dict], 
        context: Optional[Dict[str, Any]] = None
    ) -> Union[List[Dict], Dict]:
        """
        Extrae y escala datos en un solo ciclo. 
        Si se provee un 'context', se utiliza para resolver rutas que no existan en el 'source'[cite: 7, 10, 11].
        """
        if not source:
            return {} if isinstance(source, dict) else []

        is_single = isinstance(source, dict)
        items = [source] if is_single else source
        processed_records = []

        for item in items:
            clean_record = {}
            for target_col, metadata in mapping.items():
                # 1. Extracción: Se pasa el contexto al Mapper para resolución jerárquica
                raw_val = self.mapper.get_nested_value(
                    item, 
                    metadata.get("path"), 
                    context=context
                )
                
                # 2. Transformación: Escalado de valores crudos
                clean_record[target_col] = self.transformer.scale_value(
                    raw_val, 
                    metadata.get("scale")
                )
            processed_records.append(clean_record)

        return processed_records[0] if is_single else processed_records

    def batch_process(
        self, 
        items: List[Dict], 
        mapping: Dict[str, Dict],
        context: Optional[Dict[str, Any]] = None
    ) -> List[Dict]:
        """Procesa colecciones de datos (ej: lista de lanzamientos) compartiendo un mismo contexto[cite: 11]."""
        return self.process_data(items, mapping, context=context)