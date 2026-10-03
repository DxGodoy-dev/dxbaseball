from typing import Dict, Any, List, Union, Callable
from src.dxbaseball_bets.core.engine.transformer import DataTransformer

class AnalyticsBridge:
    """
    Responsabilidad: Adaptador bidireccional y Ejecutor de Analítica.
    Transforma escalas y coordina la ejecución de fórmulas matemáticas.
    """

    def __init__(self, mapping: Dict[str, Dict]):
        self.transformer = DataTransformer()
        self.mapping = mapping

    def execute_full_analysis(self, raw_data: Union[Dict, List], 
                            analysis_func: Callable, 
                            *args, **kwargs) -> Union[Dict, List]:
        """
        NUEVO: Ciclo de vida completo del cálculo.
        1. Des-escala (Int -> Float)
        2. Ejecuta función de Analytics (Fórmulas)
        3. Re-escala (Float -> Int).
        """
        if not raw_data:
            return raw_data

        # 1. Preparar datos para el motor matemático (Floats)
        calculation_ready = self.prepare_for_calculation(raw_data)

        # 2. Ejecutar la lógica de negocio (Fórmulas puras)
        # Se pasan args adicionales como game_id o constantes.
        results = analysis_func(calculation_ready, *args, **kwargs)

        # 3. Finalizar para persistencia en DB (Integers escalados)
        return self.finalize_calculation(results)

    def prepare_for_calculation(self, data: Union[Dict, List]) -> Union[Dict, List]:
        """Convierte Integers escalados a Floats reales[cite: 9]."""
        return self._process_scale(data, self.transformer.unscale_value)

    def finalize_calculation(self, calculated_data: Union[Dict, List]) -> Union[Dict, List]:
        """Convierte Floats de cálculo a Integers de Punto Fijo[cite: 9]."""
        return self._process_scale(calculated_data, self.transformer.scale_value)

    def _process_scale(self, data: Union[Dict, List], transform_func: Callable) -> Union[Dict, List]:
        """Método interno para evitar duplicidad de bucles[cite: 9]."""
        if not data:
            return data

        is_single = isinstance(data, dict)
        items = [data] if is_single else data
        
        results = []
        for item in items:
            processed_item = {}
            for key, value in item.items():
                metadata = self.mapping.get(key, {})
                scale_label = metadata.get("scale", "SCALE_1")
                processed_item[key] = transform_func(value, scale_label)
            results.append(processed_item)

        return results[0] if is_single else results