import os
from pathlib import Path

# Buscamos la raíz del proyecto (donde reside el .env y la carpeta data)
# .parent.parent.parent sube desde src/dxbaseball_bets/utils/ hasta la raíz
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent

# Definición de rutas principales
DATA_DIR = BASE_DIR / "data"
LOGS_DIR = BASE_DIR / "logs"
ENV_FILE = BASE_DIR / ".env"

# Ruta específica de la DB
DB_PATH = DATA_DIR / "betting_system.db"
SQLITE_URL = f"sqlite:///{DB_PATH}"

def ensure_directories():
    """
    Crea las carpetas necesarias si no existen al iniciar el programa.
    """
    for directory in [DATA_DIR, LOGS_DIR]:
        directory.mkdir(parents=True, exist_ok=True)
