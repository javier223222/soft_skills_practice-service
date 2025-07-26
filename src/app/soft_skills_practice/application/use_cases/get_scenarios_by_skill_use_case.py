from typing import List
from ..dtos.scenario_dtos import ScenarioDTO, ScenariosResponseDTO
from ...infrastructure.persistence.repositories.scenario_repository import ScenarioRepository


class GetScenariosBySkillUseCase:
    def __init__(self, scenario_repository: ScenarioRepository):
        self.scenario_repository = scenario_repository
    
    async def execute(self, skill_type: str) -> ScenariosResponseDTO:
        """Obtener escenarios disponibles para una soft skill específica"""
        try:
           
            if not skill_type or skill_type.strip() == "":
                raise ValueError("El skill_type no puede estar vacío")
            
            
            scenarios = await self.scenario_repository.find_by_skill_type(skill_type)
            
            
            scenario_dtos = []
            for scenario in scenarios:
                scenario_dto = ScenarioDTO(
                    scenario_id=scenario.scenario_id,
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
            
           
            popular_scenarios = [s for s in scenario_dtos if s.is_popular]
            
            return ScenariosResponseDTO(
                skill_type=skill_type,
                total_scenarios=len(scenario_dtos),
                popular_scenarios=popular_scenarios,
                all_scenarios=scenario_dtos
            )
            
        except Exception as e:
            raise Exception(f"Error fetching scenarios for {skill_type}: {str(e)}")
