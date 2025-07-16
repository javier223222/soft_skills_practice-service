from typing import List
from ..dtos.simple_skill_dtos import SimpleSkillDTO, SimpleAvailableSkillsResponseDTO
from ...infrastructure.persistence.repositories.skill_catalog_repository import SkillCatalogRepository


class GetAvailableSkillsUseCase:
    def __init__(self, skill_catalog_repository: SkillCatalogRepository):
        self.skill_catalog_repository = skill_catalog_repository
    
    async def execute(self) -> SimpleAvailableSkillsResponseDTO:
        """Obtener todas las soft skills disponibles"""
        try:
           
            skills = await self.skill_catalog_repository.find_active_skills()
            
            
            skill_dtos = []
            for skill in skills:
                skill_dto = SimpleSkillDTO(
                    skill_id=skill.skill_name, 
                    name=skill.display_name,
                    description=skill.description,
                    category=skill.category,
                    difficulty="intermedio",  
                    icon=skill.icon_name or skill.emoji,
                    color=skill.primary_color,
                    estimated_duration_minutes=skill.estimated_time_per_level
                )
                skill_dtos.append(skill_dto)
            
            return SimpleAvailableSkillsResponseDTO(
                total_skills=len(skill_dtos),
                skills=skill_dtos
            )
            
        except Exception as e:
            raise Exception(f"Error al obtener skills disponibles: {str(e)}")