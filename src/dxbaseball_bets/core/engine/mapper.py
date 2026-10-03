from typing import Any, Dict, List, Optional
from src.dxbaseball_bets.utils.logger import logger

class DataMapper:
    """
    Responsabilidad: Navegación y extracción estructural de datos.
    Soporta extracción jerárquica mediante la combinación de datos locales y contexto externo.
    """

    @staticmethod
    def get_nested_value(data: Any, path: str, context: Optional[Dict[str, Any]] = None) -> Any:
        """
        Extrae un valor siguiendo una ruta separada por puntos.
        Si el valor no se encuentra en 'data', intenta recuperarlo de 'context'.
        """
        if not path:
            return None

        # 1. Intentar búsqueda en el objeto principal (Local Scope)
        result = DataMapper._navigate_path(data, path)
        
        # 2. Si no se encuentra localmente, buscar en el contexto (External Scope)[cite: 7, 8]
        if result is None and context is not None:
            # En el contexto buscamos por llave directa o ruta simplificada
            result = context.get(path)
        return result

    @staticmethod
    def _navigate_path(data: Any, path: str) -> Any:
        """Navegación recursiva segura por el diccionario."""
        if not data:
            return None
            
        keys = path.split('.')
        current = data
        
        try:
            for key in keys:
                if isinstance(current, dict):
                    current = current.get(key)
                else:
                    return None
            
            # Gestión de objetos tipo Pandas si existieran
            if hasattr(current, 'iloc'):
                return current.iloc[0] if len(current) > 0 else None
                
            return current
        except (AttributeError, TypeError, IndexError):
            return None

    def flatten_structure(
        self, 
        source: Dict[str, Any], 
        mapping: Dict[str, Dict[str, Any]], 
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Transforma una estructura compleja en un diccionario plano basado en el contrato.
        Ahora es capaz de resolver rutas utilizando información de contexto adicional.
        """
        record = {}
        for target_col, metadata in mapping.items():
            api_path = metadata.get("path")
            # Delegamos la resolución de la ruta al método con soporte de contexto
            record[target_col] = self.get_nested_value(source, api_path, context)
            
        return record