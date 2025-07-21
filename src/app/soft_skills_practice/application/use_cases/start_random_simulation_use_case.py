from ..use_cases.start_simulation_use_case import StartSimulationUseCase
from ..dtos.simulation_dtos import (
    StartSimulationResponseDTO,SimulationSessionDTO,StartSimulationRequestBaseModel,
    StartSimulationRequestBySoftSkillDTO
)
from ...infrastructure.persistence.repositories.skill_catalog_repository import SkillCatalogRepository
import random
class StartRandomSimulationUseCase(StartSimulationUseCase):
    def __init__(self, scenario_repository, 
                 simulation_session_repository, 
                 simulation_step_repository,
                 gemini_service,
                 skill_catalog_repository: SkillCatalogRepository ):
        self.skill_catalog_repository = skill_catalog_repository
        super().__init__(scenario_repository, simulation_session_repository, simulation_step_repository, gemini_service)
    
    async def execute(self, request: StartSimulationRequestBaseModel) -> StartSimulationResponseDTO:
        
        try:
            
            skills=await self.skill_catalog_repository.find_active_skills()
            start=random.randint(0, len(skills) - 1)
            skills = skills[start]  
            print(skills)

            scenario=await self._create_scenario_by_ai(StartSimulationRequestBySoftSkillDTO(
                user_id=request.user_id,
                tecnical_specialization=request.tecnical_specialization,
                seniority_level=request.seniority_level,
                skill_type=skills.skill_name,
                difficulty_preference=request.difficulty_preference if request.difficulty_preference is not None else random.randint(1, 5)
            ))


            session=await self._create_simulation_session(request,scenario)
            initial_test=await self._generate_initial_test(scenario,request)
            initial_step=await self._create_initial_step(session,initial_test)
            response = StartSimulationResponseDTO(
                session_id=session.session_id,
                user_id=session.user_id,
                scenario_id=str(scenario.id),
                scenario={
                    "scenario_id": str(scenario.id),
                    "title": scenario.title,
                    "description": scenario.description,
                    "skill_type": scenario.skill_type,
                    "difficulty_level": scenario.difficulty_level,
                    "estimated_duration": scenario.estimated_duration,
                    "initial_situation": scenario.initial_situation
                },
                initial_situation= scenario.initial_situation,
                first_test={
                    "test_id": str(initial_step.id),
                    "question": initial_test["question"],
                    "context": initial_test["context"],
                    "instructions": initial_test["instructions"],
                    "expected_skills": initial_test.get("expected_skills", [scenario.skill_type])
                },
                session_info=SimulationSessionDTO(
                    session_id=session.session_id,
                    user_id=session.user_id,
                    scenario_id=str(scenario.id),
                    skill_type=scenario.skill_type,
                    status=session.status.value,
                    current_step=session.current_step,
                    total_steps=session.total_steps,
                    started_at=session.session_metadata.started_at,
                    difficulty_level=session.session_metadata.difficulty_level
                ),
                message="Simulación iniciada exitosamente. Complete el test inicial para continuar.",
                skill_focus=[scenario.skill_type],  
                scenario_metadata={
                    "estimated_duration_minutes": scenario.estimated_duration,
                    "skill_focus": [scenario.skill_type],
                    "scenario_context": {
                        "scenario_title": scenario.title,
                        "skill_type": scenario.skill_type
                    }
                }

            )
            response=self.response(response)
            
            return response
          

           
        
        except Exception as e:
            print(f"Error al iniciar la simulación: {e}")