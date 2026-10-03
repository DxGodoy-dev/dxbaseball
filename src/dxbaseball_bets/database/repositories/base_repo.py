from typing import TypeVar, Generic, Type, Optional, List, Any, Dict
from sqlalchemy.orm import Session
from src.dxbaseball_bets.database.db_models import Base

# Definición de tipo genérico para modelos de SQLAlchemy
T = TypeVar("T", bound=Base)

class BaseRepo(Generic[T]):
    """
    Interfaz genérica para operaciones CRUD con filtrado dinámico 
    y persistencia segura integrada.
    """
    def __init__(self, model: Type[T], session: Session):
        self.model = model
        self.session = session

    def _filter_allowed_cols(self, model_class: Type[Any], data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Filtra un diccionario para que solo contenga llaves que existen como 
        columnas en el modelo de SQLAlchemy[cite: 9].
        Evita TypeErrors al intentar instanciar modelos con campos extra del extractor.
        """
        valid_columns = {c.name for c in model_class.__table__.columns}
        return {k: v for k, v in data.items() if k in valid_columns}

    def upsert_data(self, model_class: Type[Any], data: Dict[str, Any]) -> Any:
        """
        Realiza un 'merge' (Upsert) de datos después de filtrarlos dinámicamente[cite: 9].
        Este método centraliza la lógica que antes se repetía en cada repositorio hijo.
        """
        clean_data = self._filter_allowed_cols(model_class, data)
        obj = model_class(**clean_data)
        return self.session.merge(obj)

    def get_by_id(self, id: Any) -> Optional[T]:
        """Busca un registro por su Primary Key[cite: 9]."""
        return self.session.query(self.model).filter(self.model.id == id).first()

    def get_all(self, skip: int = 0, limit: int = 100) -> List[T]:
        """Retorna una lista paginada de registros[cite: 9]."""
        return self.session.query(self.model).offset(skip).limit(limit).all()

    def create(self, obj_in: T) -> T:
        """Crea un nuevo registro en la sesión[cite: 9]."""
        self.session.add(obj_in)
        self.session.flush() 
        return obj_in

    def update(self, db_obj: T, obj_in: Dict[str, Any]) -> T:
        """Actualiza campos específicos de un objeto existente[cite: 9]."""
        for field, value in obj_in.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)
        self.session.add(db_obj)
        return db_obj

    def delete(self, id: Any) -> bool:
        """Elimina un registro por ID[cite: 9]."""
        obj = self.get_by_id(id)
        if obj:
            self.session.delete(obj)
            return True
        return False