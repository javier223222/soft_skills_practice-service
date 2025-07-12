from abc import ABC,abstractmethod
from typing import TypeVar,Generic,Optional,List,Dict,Any
from beanie import Document
from datetime import datetime
T = TypeVar('T', bound=Document)

class BaseRepository(Generic[T], ABC):
    """Repositorio base con operaciones CRUD genéricas"""
    
    def __init__(self, model_class: type[T]):
        self.model_class = model_class
    
    async def create(self, entity: T) -> T:
        """Crear una nueva entidad"""
        await entity.insert()
        return entity
    
    async def find_by_id(self, entity_id: str) -> Optional[T]:
        """Buscar entidad por ID"""
        return await self.model_class.get(entity_id)
    
    async def find_all(self, limit: int = 100, skip: int = 0) -> List[T]:
        """Buscar todas las entidades con paginación"""
        return await self.model_class.find().skip(skip).limit(limit).to_list()
    
    async def update(self, entity: T) -> T:
        """Actualizar entidad existente"""
        entity.updated_at = datetime.utcnow()
        await entity.save()
        return entity
    
    async def delete_by_id(self, entity_id: str) -> bool:
        """Eliminar entidad por ID"""
        entity = await self.find_by_id(entity_id)
        if entity:
            await entity.delete()
            return True
        return False
    
    async def delete(self, entity: T) -> bool:
        """Eliminar entidad"""
        await entity.delete()
        return True
    
    async def count(self) -> int:
        """Contar total de entidades"""
        return await self.model_class.count()
    
    async def exists(self, entity_id: str) -> bool:
        """Verificar si existe una entidad"""
        entity = await self.find_by_id(entity_id)
        return entity is not None
