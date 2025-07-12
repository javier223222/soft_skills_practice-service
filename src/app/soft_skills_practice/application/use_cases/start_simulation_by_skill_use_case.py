from ..use_cases.start_simulation_use_case import StartSimulationUseCase
from ..dtos.simulation_dtos import (
    StartSimulationRequestBySoftSkillDTO
)
class StartSimulationBySkillUseCase(StartSimulationUseCase):
    async def execute(self,request:StartSimulationRequestBySoftSkillDTO):
        """Iniciar una simulación por soft skill"""
        try:
            # Validar que el user_id no esté vacío
            if not request.user_id or request.user_id.strip() == "":
                raise ValueError("El user_id no puede estar vacío")
            
            # Validar que el skill_type no esté vacío
            if not request.skill_type or request.skill_type.strip() == "":
                raise ValueError("El skill_type no puede estar vacío")
            
            # Llamar al caso de uso base para iniciar la simulación
            scenario=await self._create_scenario_by_ai(request)
            return scenario
        
        except Exception as e:
            raise Exception(f"Error al iniciar simulación por soft skill: {str(e)}")