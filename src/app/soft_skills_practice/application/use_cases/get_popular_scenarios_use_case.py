import math
from typing import List
from ..dtos.pagination_dtos import PaginationParamsDTO, PaginationMetaDTO, PaginatedScenariosResponseDTO
from ..dtos.scenario_dtos import ScenarioDTO
from ...infrastructure.persistence.repositories.scenario_repository import ScenarioRepository
class GetPopularScenariosUseCase:
    def __init__(self, scenario_repository:ScenarioRepository):
        self.scenario_repository = scenario_repository
    async def execute(self, pagination_params: PaginationParamsDTO) -> PaginatedScenariosResponseDTO:
        """Obtener escenarios por skill con paginación"""
        try:
           
            
            
            scenarios,total_counts = await self.scenario_repository.find_popular_scenarios(pagination_params.page,pagination_params.page_size)
            
            

            if not scenarios:
                
                pagination_meta = PaginationMetaDTO(
                    current_page=pagination_params.page,
                    page_size=pagination_params.page_size,
                    total_items=0,
                    total_pages=0,
                    has_next=False,
                    has_previous=False
                )
                
                return PaginatedScenariosResponseDTO(
                    
                    scenarios=[],
                    pagination=pagination_meta
                )
            
            
            scenario_dtos = []
            for scenario in scenarios:
                scenario_dto = ScenarioDTO(
                    scenario_id=str(scenario.id),
                    skill_type=scenario.skill_type,
                    title=scenario.title,
                    description=scenario.description,
                    difficulty_level=scenario.difficulty_level,
                    estimated_duration=scenario.estimated_duration,
                    initial_situation=scenario.initial_situation,
                    scenario_icon=scenario.scenario_icon,
                    scenario_image_url=scenario.scenario_image_url,
                    scenario_color=scenario.scenario_color,
                    usage_count=scenario.usage_count,
                    is_popular=scenario.is_popular,
                    average_rating=scenario.average_rating,
                    tags=scenario.tags
                )
                scenario_dtos.append(scenario_dto)
            
           

            
            
            print
            pagination_meta = self.scenario_repository.calculate_pagination_info(
                page=pagination_params.page,
                limit=pagination_params.page_size,
                total_counts=total_counts
            )
            
            return {
                
                "scenarios":scenario_dtos,
                "pagination":{
                    "current_page": pagination_params.page,
                    "page_size": pagination_params.page_size,
                    "total_items": total_counts,
                    "total_pages": pagination_meta["total_pages"],
                    "has_next": pagination_meta["has_next"],
                    "has_previous": pagination_meta["has_previous"]
                }
            
            }
        except Exception as e:
            raise Exception(f"Error al obtener escenarios paginados: {str(e)}")



  