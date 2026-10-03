import sys
from pathlib import Path
from sqlalchemy import text
from alembic.config import Config
from alembic import command

# 1. Configuración de rutas para importar módulos del proyecto
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))

from src.dxbaseball_bets.database.session_manager import SessionManager
from src.dxbaseball_bets.utils.paths import DB_PATH, ensure_directories
from src.dxbaseball_bets.utils.logger import logger

def run_migrations():
    """
    Ejecuta las migraciones de Alembic para asegurar que el esquema físico
    esté actualizado con los modelos de SQLAlchemy.
    """
    logger.info("Iniciando migración de base de datos...")
    ensure_directories()
    
    # Cargar la configuración de Alembic (asumiendo alembic.ini en la raíz)
    alembic_cfg = Config(BASE_DIR / "alembic.ini")
    
    try:
        # Ejecuta 'upgrade head'
        command.upgrade(alembic_cfg, "head")
        logger.info("Migración completada exitosamente.")
    except Exception as e:
        logger.error(f"Error durante la migración: {e}")
        raise

def verify_connection():
    """
    Verifica que la conexión a la base de datos física sea funcional
    y que las tablas críticas existan.
    """
    logger.info(f"Verificando conexión en: {DB_PATH}")
    
    with SessionManager.get_session() as session:
        try:
            # Intento de consulta simple
            result = session.execute(text("SELECT name FROM sqlite_master WHERE type='table';"))
            tables = [row[0] for row in result]
            
            logger.info(f"Conexión exitosa. Tablas detectadas: {len(tables)}")
            for table in tables:
                logger.debug(f" - Tabla encontrada: {table}")
                
            return True
        except Exception as e:
            logger.error(f"Error de verificación de base de datos: {e}")
            return False

def init_db():
    """
    Punto de entrada principal para inicializar la infraestructura de datos.
    """
    print("\n" + "="*50)
    print("SISTEMA DE INICIALIZACIÓN DE BASE DE DATOS (DXBASEBALL)")
    print("="*50)
    
    try:
        run_migrations()
        if verify_connection():
            print("\n✅ BASE DE DATOS LISTA PARA OPERAR")
            print(f"📍 Ubicación: {DB_PATH}")
        else:
            print("\n❌ LA VERIFICACIÓN DE CONEXIÓN FALLÓ")
    except Exception as e:
        print(f"\n❌ ERROR CRÍTICO: {e}")

if __name__ == "__main__":
    init_db()