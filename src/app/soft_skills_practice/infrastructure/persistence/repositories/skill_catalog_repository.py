from typing import List, Optional, Dict, Any
from ..models.simulation_models import SkillCatalog
from .base_repository import BaseRepository

class SkillCatalogRepository(BaseRepository[SkillCatalog]):
    """Repositorio para gestionar catálogo de skills"""
    
    def __init__(self):
        super().__init__(SkillCatalog)
    
    async def find_by_skill_name(self, skill_name: str) -> Optional[SkillCatalog]:
        """Buscar skill por nombre"""
        return await SkillCatalog.find_one(
            SkillCatalog.skill_name == skill_name
        )
    
    async def find_by_category(self, category: str) -> List[SkillCatalog]:
        """Buscar skills por categoría"""
        return await SkillCatalog.find(
            SkillCatalog.category == category,
            SkillCatalog.is_active == True
        ).sort(SkillCatalog.display_order).to_list()
    
    async def find_active_skills(self) -> List[SkillCatalog]:
        """Buscar skills activas"""
        return await SkillCatalog.find(
            SkillCatalog.is_active == True
        ).sort(SkillCatalog.category, SkillCatalog.display_order).to_list()
    
    async def find_featured_skills(self) -> List[SkillCatalog]:
        """Buscar skills destacadas"""
        return await SkillCatalog.find(
            SkillCatalog.is_featured == True,
            SkillCatalog.is_active == True
        ).to_list()
    
    async def get_skills_by_category_with_stats(self) -> Dict[str, List[SkillCatalog]]:
        """Obtener skills agrupadas por categoría con estadísticas"""
        skills = await self.find_active_skills()
        
        categories = {}
        for skill in skills:
            category = skill.category
            if category not in categories:
                categories[category] = []
            categories[category].append(skill)
        
        return categories
    
    async def update_skill_statistics(self, skill_name: str, stats_update: Dict[str, Any]) -> bool:
        """Actualizar estadísticas de una skill"""
        skill = await self.find_by_skill_name(skill_name)
        if skill:
            for key, value in stats_update.items():
                if hasattr(skill, key):
                    setattr(skill, key, value)
            
            await skill.save()
            return True
        return False
    
    async def create_skill(self, skill_data: Dict[str, Any]) -> SkillCatalog:
        """Crear nueva skill"""
        new_skill = SkillCatalog(**skill_data)
        await new_skill.insert()
        return new_skill
    
    async def create_skill_if_not_exists(self, skill_data: Dict[str, Any]) -> SkillCatalog:
        """Crear skill si no existe"""
        existing = await self.find_by_skill_name(skill_data["skill_name"])
        if existing:
            return existing
        
        return await self.create_skill(skill_data)
    async def delete_all_skills(self) -> None:
        
        await SkillCatalog.delete_all()
        