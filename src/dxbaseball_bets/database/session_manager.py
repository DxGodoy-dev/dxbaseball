from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager
from typing import Generator
from src.dxbaseball_bets.utils.paths import SQLITE_URL, ensure_directories

class SessionManager:
    """
    Gestor centralizado de conexiones.
    Ahora utiliza las rutas definidas en paths.py para persistencia física.
    """
    _engine = None
    _SessionLocal = None

    @classmethod
    def initialize(cls):
        """Inicializa el engine usando la ruta física del proyecto."""
        if cls._engine is None:
            # Aseguramos que la carpeta /data exista antes de conectar
            ensure_directories()
            
            cls._engine = create_engine(
                SQLITE_URL, # f"sqlite:///{DB_PATH}"
                connect_args={"check_same_thread": False}
            )
            cls._SessionLocal = sessionmaker(
                autocommit=False, 
                autoflush=False, 
                bind=cls._engine
            )

    @classmethod
    @contextmanager
    def get_session(cls) -> Generator[Session, None, None]:
        """Provee una sesión que se sincroniza con el archivo en /data."""
        if cls._SessionLocal is None:
            cls.initialize()
        
        session = cls._SessionLocal()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()