import sys
from loguru import logger
from pathlib import Path

# Configuración de rutas
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

class AppLogger:
    """
    Configuración centralizada de logging para el ecosistema de analítica.
    Registra el flujo completo: Extracción -> Transformación -> Cálculo.
    """
    
    @staticmethod
    def setup_logger():
        # Eliminamos la configuración por defecto
        logger.remove()

        # 1. Log en consola: Formato limpio y con colores para desarrollo
        logger.add(
            sys.stderr,
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
            level="DEBUG" # Captura todo el proceso de construcción
        )

        # 2. Log en archivo: Rotativo e informativo para auditoría de datos
        logger.add(
            LOG_DIR / "app_processing.log",
            rotation="10 MB",      # Crea un nuevo archivo cada 10MB
            retention="10 days",   # Mantiene logs de los últimos 10 días
            compression="zip",     # Comprime los logs viejos
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}",
            level="INFO",
            serialize=False        # Cambiar a True si prefieres formato JSON para ELK/Datadog
        )

        # 3. Log de Errores Críticos: Archivo separado para depuración rápida
        logger.add(
            LOG_DIR / "errors.log",
            level="ERROR",
            backtrace=True,        # Muestra el rastro completo del error
            diagnose=True          # Muestra valores de variables en el error
        )

        return logger

# Inicializamos la instancia global
app_logger = AppLogger.setup_logger()