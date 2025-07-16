import math
from typing import List
from ..dtos.pagination_dtos import PaginationParamsDTO, PaginationMetaDTO, PaginatedSkillDTO, PaginatedSkillsResponseDTO
from ...infrastructure.persistence.repositories.skill_catalog_repository import SkillCatalogRepository
from ...infrastructure.persistence.repositories.simulation_session_repository import SimulationSessionRepository
from .get_user_progress_use_case import GetUserProgressUseCase


class GetPaginatedUserSkillsUseCase:
    def __init__(self, skill_catalog_repository: SkillCatalogRepository, simulation_session_repository: SimulationSessionRepository):
        self.skill_catalog_repository = skill_catalog_repository
        self.simulation_session_repository = simulation_session_repository
        self.get_progress_use_case = GetUserProgressUseCase(simulation_session_repository)
    
    async def execute(self, user_id: str, pagination_params: PaginationParamsDTO) -> PaginatedSkillsResponseDTO:
        """Obtener skills disponibles con progreso del usuario - paginado"""
        try:
            
            if not user_id or user_id.strip() == "":
                raise ValueError("El user_id no puede estar vacío")
            
           
            all_skills = await self.skill_catalog_repository.find_active_skills()
            
            
           
            user_progress = await self.get_progress_use_case.execute(user_id, auto_register=True)
            
            
            
            skills_with_progress = []
            for skill in all_skills:
                
                progress_percentage = 0.0
                sessions_completed = 0
                average_score = 0.0
                current_level = 1
                points_earned = 0
                
                for progress in user_progress.skills_progress:
                    if progress.skill_id == skill.skill_name:  
                        progress_percentage = progress.progress_percentage
                        sessions_completed = progress.completed_sessions
                        
                        average_score = progress.average_score
                       
                        if sessions_completed> 0 and average_score > 0:
                            points_earned = int(average_score * sessions_completed)
                            current_level = max(1, points_earned // 100 + 1)
                        break
                
                skill_dto = PaginatedSkillDTO(
                    skill_id=skill.skill_name,
                    skill_name=skill.skill_name,
                    skill_type=skill.skill_name,  
                    name=skill.display_name,
                    description=skill.description,
                    category=skill.category,
                    difficulty="intermedio",  
                    visual_config={
                        "icon": skill.icon_name or skill.emoji or "🎯",
                        "color_hex": skill.primary_color or "#4A90E2",
                        "emoji": skill.emoji or "🎯"
                    },
                    estimated_duration_minutes=skill.estimated_time_per_level,
                    user_progress={
                        "progress_percentage": progress_percentage,
                        "current_level": current_level,
                        "points_earned": points_earned,
                        "sessions_completed": sessions_completed,
                        "average_score": average_score
                    },
                    scenarios_count=skill.total_scenarios or 2  
                )
                
                skills_with_progress.append(skill_dto)
            
            
            total_items = len(skills_with_progress)
            total_pages = math.ceil(total_items / pagination_params.page_size)
            
           
            if pagination_params.page > total_pages and total_items > 0:
                raise ValueError(f"Página {pagination_params.page} no existe. Total de páginas: {total_pages}")
            
            
            start_index = (pagination_params.page - 1) * pagination_params.page_size
            end_index = start_index + pagination_params.page_size
            paginated_skills = skills_with_progress[start_index:end_index]
            
            
            pagination_meta = PaginationMetaDTO(
                current_page=pagination_params.page,
                page_size=pagination_params.page_size,
                total_items=total_items,
                total_pages=total_pages,
                has_next=pagination_params.page < total_pages,
                has_previous=pagination_params.page > 1
            )
            
            return PaginatedSkillsResponseDTO(
                user_id=user_id,
                skills=paginated_skills,
                pagination=pagination_meta
            )
            
        except Exception as e:
            raise Exception(f"Error al obtener skills paginadas: {str(e)}")
