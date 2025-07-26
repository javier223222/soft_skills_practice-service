from ..use_cases.start_simulation_use_case import StartSimulationUseCase
from ..dtos.simulation_dtos import (
    StartSimulationResponseDTO,StartSimulationRequestDTO,SimulationSessionDTO
)
class StartSimulationByScenarioUseCase(StartSimulationUseCase):
    async def execute(self, request: StartSimulationRequestDTO) -> StartSimulationResponseDTO:
        """Iniciar una nueva simulación de soft skills"""
        try:
            
            print(f"Iniciando simulación para el escenario {request.scenario_id} y usuario {request.user_id}")
            scenario = await self._get_scenario(request.scenario_id)
            
            if not scenario:
                raise ValueError(f"Escenario {request.scenario_id} not found")
            
            
            session = await self._create_simulation_session(request, scenario)
            
            
            initial_test = await self._generate_initial_test(scenario,request)
            
            
            initial_step = await self._create_initial_step(session, initial_test)
            print(f"initial step was crreated ", initial_step)
        
            
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
                message="Simulation started successfully. Please complete the initial test to continue. ",
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
            response = self.response(response)
            
            return response
            
        except Exception as e:
            raise Exception(f"Error initiating simulation: {str(e)}")