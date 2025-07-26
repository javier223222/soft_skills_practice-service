import uuid
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from ..dtos.simulation_dtos import (
    StartSimulationRequestDTO, 
   
    StartSimulationRequestBySoftSkillDTO,
    
)
from ...infrastructure.persistence.repositories.scenario_repository import ScenarioRepository
from ...infrastructure.persistence.repositories.simulation_session_repository import SimulationSessionRepository
from ...infrastructure.persistence.repositories.simulation_step_repository import SimulationStepRepository
from ...infrastructure.persistence.models.simulation_models import (
    SimulationSession, 
    SimulationStep
)
from ...infrastructure.persistence.models.base_models import (
    SimulationStatus,
    StepType,
    MessageType,
    StepContent,
    InteractionTracking,
    SessionMetadata
)
from ..services.gemini_service import GeminiService

class StartSimulationUseCase:
    def __init__(
        self, 
        scenario_repository: ScenarioRepository,
        simulation_session_repository: SimulationSessionRepository,
        simulation_step_repository: SimulationStepRepository,
        gemini_service: GeminiService,
    
    ):
        self.scenario_repository = scenario_repository
        self.simulation_session_repository = simulation_session_repository
        self.simulation_step_repository = simulation_step_repository
        self.gemini_service = gemini_service
    
    
    
    async def _create_scenario_by_ai(self,request:StartSimulationRequestBySoftSkillDTO):
        try:
            prompt =  prompt = f"""
You are an expert in designing interactive simulations for soft skills development.

Generate a realistic practice scenario that helps the user strengthen the soft skill: "{request['skill_type']}". 
The scenario must adapt to the following user characteristics:
- Technical specialization: "{request['tecnical_specialization']}"
- Seniority level: "{request['seniority_level']}"
- Desired difficulty level: {request['difficulty_preference']} (scale from 1 to 5)

Scenario requirements:
1. Direct relevance to the indicated soft skill.
2. Set in a realistic work situation, without technical challenges.
3. Designed for a text-based chat simulation.
4. Must allow for decision-making and reflection.
5. Maximum estimated duration: 20 minutes.
6. ALL CONTENT MUST BE IN ENGLISH ONLY.

Return only a valid JSON, without explanations, without headers, without single quotes. Make sure it is well-formed.

JSON:
{{
  "title": "Scenario title",
  "description": "General description of the scenario context",
  "difficulty_level": {request['difficulty_preference']},
  "estimated_duration": "Estimated duration in minutes only a integer",
  "steps": "number of steps to follow always 5",
  "initial_situation": "Initial situation that presents the challenge or dilemma to the user",
  "tags": ["tags", "related", "to the skill"]
}}
"""
            response = await self.gemini_service._generate_content(prompt)
            scenario_data = self.gemini_service._parse_scenario_response(response.content)
        
            scenario=await self.scenario_repository.create_scenario({
                "skill_type": request.skill_type,
                "title": scenario_data["title"],
                "description": scenario_data["description"],
                "difficulty_level": scenario_data["difficulty_level"],
                "estimated_duration": scenario_data["estimated_duration"],
                "initial_situation": scenario_data["initial_situation"],
                "steps": int(scenario_data["steps"]) if "steps" in scenario_data else 5,
                
                "scenario_icon": None,
                "scenario_color":None,  
                "tags": scenario_data.get("tags", []),
                "is_popular": False,
                "is_create_by_ai": True



            })
            


            return scenario
        
        except Exception as e:
            raise Exception(f"Error al crear escenario con IA: {str(e)}")

    async def _get_scenario(self, scenario_id: str):
        """Obtener escenario por ID"""

        scenario = await self.scenario_repository.find_by_id(scenario_id)
        if scenario:
            return scenario
        
      
        scenario = await self.scenario_repository.find_by_scenario_id(scenario_id)
        return scenario
    
    async def _create_simulation_session(self, request: StartSimulationRequestDTO, scenario) -> SimulationSession:
        """Crear nueva sesión de simulación"""
        session_id = str(uuid.uuid4())
        
        
        difficulty_level = request.difficulty_preference or scenario.difficulty_level
        
        session = SimulationSession(
            session_id=session_id,
            user_id=request.user_id,
            user_name=request.user_id,  
            skill_type=scenario.skill_type,
            scenario_id=str(scenario.id),
            scenario_title=scenario.title,
            status=SimulationStatus.STARTED,
            current_step=1,
            total_steps= scenario.steps or 5,
            session_metadata=SessionMetadata(
                difficulty_level=difficulty_level,
                estimated_duration=scenario.estimated_duration,
                platform="web"
            )
        )
        
        
        saved_session = await self.simulation_session_repository.create(session)
        return saved_session
    
    async def _generate_initial_test(self, scenario,request:StartSimulationRequestDTO) -> Dict[str, Any]:
        """Generar test inicial con IA para evaluar nivel base del usuario"""
        
        
        prompt = """You are an expert in soft skills assessment. Generate an initial test to evaluate the user's baseline level in "{skill_type}" before starting the simulation.

SCENARIO CONTEXT:
- Title: {title}
- Description: {description}
- Initial situation: {initial_situation}
- Difficulty level: {difficulty_level}/5

Create an initial assessment that:
1. Evaluates user's prior knowledge about the skill based on their technical specialization "{technical_specialization}" and seniority level "{seniority_level}"
2. Is relevant to the scenario context
3. Helps personalize the simulation experience
4. Takes 3-5 minutes to complete

Return ONLY valid JSON format:
{{
    "question": "Main assessment question",
    "context": "Specific context for the question",
    "instructions": "Clear instructions for the user",
    "expected_skills": ["{skill_type}"],
    "estimated_time_minutes": 4,
    "evaluation_criteria": ["criterion1", "criterion2", "criterion3"]
}}

The question must be open-ended and allow evaluation of the user's previous experience."""

        try:
            response = await self.gemini_service._generate_content(prompt)
            initial_test_data = self.gemini_service._parse_scenario_response(response.content)
            
            return initial_test_data
        except Exception as e:
           
            raise Exception(f"Error generating initial test: {str(e)}")
    
    async def _create_initial_step(self, session: SimulationSession, initial_test: Dict[str, Any]) -> SimulationStep:
        """Crear el paso inicial del test"""
        
        step = SimulationStep(
            session_id=session.session_id,
            step_number=1,
            step_type=StepType.PRE_TEST,
            message_type=MessageType.PRE_TEST_QUESTION,
            content=StepContent(
                question=initial_test["question"],
                context=initial_test["context"]
            ),
            interaction_tracking=InteractionTracking(),
            context={
                "is_initial_test": True,
                "instructions": initial_test["instructions"],
                "expected_skills": initial_test["expected_skills"],
                "evaluation_criteria": initial_test.get("evaluation_criteria", []),
                "scenario_context": {
                    "scenario_title": session.scenario_title,
                    "skill_type": session.skill_type
                }
            }
        )
        
       
        saved_step = await self.simulation_step_repository.create(step)
        return saved_step
    def response(self,simulation_response):
         return {
            "success": True,
            "session_id": simulation_response.session_id,
            "user_id": simulation_response.user_id,
            "scenario": simulation_response.scenario,
            "initial_test": simulation_response.first_test,
            "session_info": {
                "session_id": simulation_response.session_info.session_id,
                "skill_type": simulation_response.session_info.skill_type,
                "status": simulation_response.session_info.status,
                "current_step": simulation_response.session_info.current_step,
                "total_steps": simulation_response.session_info.total_steps,
                "difficulty_level": simulation_response.session_info.difficulty_level,
                "started_at": simulation_response.session_info.started_at.isoformat()
            },
            "message": simulation_response.message,
            "next_action": "complete_initial_test"
        }
    