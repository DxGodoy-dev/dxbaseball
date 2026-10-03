from typing import Any, Union, Callable
from src.dxbaseball_bets.core.config.scaling_factors import SCALES

class DataTransformer:
    """
    Responsabilidad: Ejecución de estrategias de transformación (Escalado o Formateo).
    No conoce la naturaleza del dato, solo ejecuta la función vinculada a la etiqueta.
    """

    @staticmethod
    def scale_value(value: Any, scale_label: str) -> Any:
        """
        Aplica la transformación registrada (punto fijo o formato de utilidad).
        """
        # 1. Recuperamos la función (estrategia) del registro
        # Si la etiqueta no existe, usamos una función identidad por defecto (lambda v: v)
        transform_func = SCALES.get(scale_label, lambda v: v)

        if value is None:
            return 0 if "SCALE_" in scale_label and scale_label != "SCALE_1" else None

        try:
            # 2. Ejecutamos la transformación (sea matemática o de formato)
            return transform_func(value)
        except (TypeError, ValueError, AttributeError):
            # Fallback seguro en caso de datos corruptos o errores en la función de utilidad
            return 0 if "SCALE_" in scale_label else None

    @staticmethod
    def unscale_value(value: Any, scale_label: str) -> Union[float, Any]:
        """
        Revierte el escalado numérico si la etiqueta corresponde a una escala.
        """
        # El des-escalado solo tiene sentido para métricas numéricas (SCALE_10, etc.)
        # Si es un formato (HEIGHT, DATE), devolvemos el valor tal cual.
        if "SCALE_" not in scale_label or scale_label == "SCALE_1":
            return value

        # Extraemos el factor numérico de la etiqueta para la operación inversa
        # Nota: Esto asume que mantenemos la convención de nombres SCALE_X[cite: 5]
        try:
            factor = int(scale_label.split('_')[1])
            if value is None:
                return 0.0[cite: 3]
            return float(value / factor)[cite: 2]
        except (IndexError, ValueError, TypeError):
            return value