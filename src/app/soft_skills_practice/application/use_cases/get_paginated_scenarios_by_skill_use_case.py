import math
from typing import List
from ..dtos.pagination_dtos import PaginationParamsDTO, PaginationMetaDTO, PaginatedScenariosResponseDTO
from ..dtos.scenario_dtos import ScenarioDTO
from ...infrastructure.persistence.repositories.scenario_repository import ScenarioRepository


class GetPaginatedScenariosBySkillUseCase:
    def __init__(self, scenario_repository: ScenarioRepository):
        self.scenario_repository = scenario_repository
    
    async def execute(self, skill_type: str, pagination_params: PaginationParamsDTO) -> PaginatedScenariosResponseDTO:
        """Obtener escenarios por skill con paginación"""
        try:
            print("Ejecutando GetPaginatedScenariosBySkillUseCase")
           
            # Validar que el skill_type no esté vacío
            if not skill_type or skill_type.strip() == "":
                raise ValueError("El skill_type no puede estar vacío")
            
            # Obtener todos los escenarios para esta skill
            scenarios,total_counts = await self.scenario_repository.find_by_skill_type(skill_type,pagination_params.page, pagination_params.page_size)
            
            if not scenarios:
                # Si no hay escenarios, retornar respuesta vacía pero válida
                pagination_meta = PaginationMetaDTO(
                    current_page=pagination_params.page,
                    page_size=pagination_params.page_size,
                    total_items=0,
                    total_pages=0,
                    has_next=False,
                    has_previous=False
                )
                
                return PaginatedScenariosResponseDTO(
                    skill_type=skill_type,
                    scenarios=[],
                    pagination=pagination_meta
                )
            
            # Convertir a DTOs
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
            
            # Ordenar por popularidad y uso
            scenario_dtos.sort(key=lambda x: (x.is_popular, x.usage_count), reverse=True)
            
            
            
            
            # Crear metadatos de paginación
            pagination_meta = self.scenario_repository.calculate_pagination_info(
                page=pagination_params.page,
                limit=pagination_params.page_size,
                total_counts=total_counts  # Total de escenarios obtenidos
            )
            
            print(pagination_meta["total_pages"])
            return PaginatedScenariosResponseDTO(
                skill_type=skill_type,
                scenarios=scenario_dtos,
                pagination={
                    "current_page": pagination_params.page,
                    "page_size": pagination_params.page_size,
                    "total_items": total_counts,
                    "total_pages": pagination_meta["total_pages"],
                    "has_next": pagination_meta["has_next"],
                    "has_previous": pagination_meta["has_previous"]
                }
            )
            
        except Exception as e:
            raise Exception(f"Error al obtener escenarios paginados: {str(e)}")
