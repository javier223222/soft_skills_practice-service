from ..use_cases.start_simulation_use_case import StartSimulationUseCase
from ..dtos.simulation_dtos import (
    StartSimulationRequestBySoftSkillDTO,
    StartSimulationResponseDTO,
    SimulationSessionDTO

)

class StartSimulationBySkillUseCase(StartSimulationUseCase):
    async def execute(self,request:StartSimulationRequestBySoftSkillDTO):
        """Iniciar una simulación por soft skill"""
        try:
           
            if not request.user_id or request.user_id.strip() == "":
                raise ValueError("El user_id no puede estar vacío")
            
            
            if not request.skill_type or request.skill_type.strip() == "":
                raise ValueError("El skill_type no puede estar vacío")
            
            
           
            scenario=await self._create_scenario_by_ai(request)
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
            raise Exception(f"Error al iniciar simulación por soft skill: {str(e)}")