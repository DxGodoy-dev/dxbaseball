import sys
from pathlib import Path
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context

# 1. Configuración de Paths para que Alembic encuentre los módulos del proyecto
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent.parent
sys.path.append(str(BASE_DIR))

# 2. Importaciones del proyecto
from src.dxbaseball_bets.database.db_models import Base
from src.dxbaseball_bets.utils.paths import SQLITE_URL, ensure_directories

# 3. Preparación del entorno
config = context.config

# Sobreescribimos la URL del .ini con la de paths.py para asegurar que use la carpeta /data
config.set_main_option("sqlalchemy.url", SQLITE_URL)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Metadata para autogenerate
target_metadata = Base.metadata

def run_migrations_offline() -> None:
    """Ejecuta migraciones en modo 'offline'."""
    url = config.get_main_option("sqlalchemy.url")
    ensure_directories() # Asegura que exista la carpeta /data
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    """Ejecuta migraciones en modo 'online'."""
    ensure_directories() # Asegura que exista la carpeta /data
    
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, 
            target_metadata=target_metadata,
            render_as_batch=True
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()