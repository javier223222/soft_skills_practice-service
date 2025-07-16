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
        gemini_service: GeminiService
    ):
        self.scenario_repository = scenario_repository
        self.simulation_session_repository = simulation_session_repository
        self.simulation_step_repository = simulation_step_repository
        self.gemini_service = gemini_service
    
    
    
    async def _create_scenario_by_ai(self,request:StartSimulationRequestBySoftSkillDTO):
        try:
            prompt =  f"""
Eres un experto en diseño de simulaciones interactivas para el desarrollo de habilidades blandas.

Genera un escenario de práctica realista que ayude al usuario a fortalecer la habilidad blanda: "{request.skill_type}". 
El escenario debe adaptarse a las siguientes características del usuario:
- Especialización técnica: "{request.tecnical_specialization}"
- Nivel de seniority: "{request.seniority_level}"
- Nivel de dificultad deseado: {request.difficulty_preference} (escala del 1 al 5)

Crea un escenario que cumpla los siguientes requisitos:
1. Sea relevante para la habilidad blanda indicada.
2. Presente una situación realista del entorno laboral, sin enfocarse en aspectos técnicos.
3. Permita al usuario interactuar en una simulación tipo chat de texto.
4. Esté completamente enfocado en el desarrollo de la habilidad blanda, sin incluir retos técnicos.

La salida debe estar en el siguiente formato JSON, sin comentarios ni explicaciones adicionales:
{{
  "title": "Título del escenario",
  "description": "Descripción general del contexto del escenario",
  "difficulty_level": {request.difficulty_preference},
  "estimated_duration": Duración estimada en minutos ,
  "steps":Numero de pasos de la simulación debe ser siempre  mayor a 4 ,
  "initial_situation": "Situación inicial que presenta el reto o dilema al usuario",
  "tags": ["etiquetas", "relacionadas", "a la habilidad"]
}}

Este escenario debe invitar a la reflexión, toma de decisiones o análisis, y enfocarse únicamente en poner a prueba la habilidad blanda: "{request.skill_type}".
no debe durar mas de 20 minutos en completarse.

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
        
        
        prompt = f"""
Eres un experto en evaluación de soft skills. Genera un test inicial para evaluar el nivel base del usuario en la habilidad "{scenario.skill_type}" antes de comenzar la simulación.

CONTEXTO DEL ESCENARIO:
- Título: {scenario.title}
- Descripción: {scenario.description}
- Situación inicial: {scenario.initial_situation}
- Nivel de dificultad: {scenario.difficulty_level}/5


Genera un test inicial que:
1. Evalúe el conocimiento previo del usuario sobre la habilidad en base a su area de especializacion tecnica que es "{request.tecnical_specialization}" y su seniority level "{request.seniority_level}"
2. Sea relevante al contexto del escenario
3. Ayude a personalizar la experiencia de simulación
4. Tome entre 3-5 minutos en responder

Responde ÚNICAMENTE en formato JSON:
{{
    "question": "Pregunta principal del test inicial",
    "context": "Contexto específico para la pregunta",
    "instructions": "Instrucciones claras para el usuario",
    "expected_skills": ["{scenario.skill_type}"],
    "estimated_time_minutes": 5,
    "evaluation_criteria": ["criterio1", "criterio2", "criterio3"]
}}

La pregunta debe ser abierta y permitir evaluar la experiencia previa del usuario.
"""

        try:
            response = await self.gemini_service._generate_content(prompt)
            initial_test_data = self.gemini_service._parse_scenario_response(response.content)
            
            return initial_test_data
        except Exception as e:
           
            return {
                "question": f"Antes de comenzar con el escenario '{scenario.title}', cuéntanos sobre tu experiencia previa con {scenario.skill_type}. ¿Has enfrentado situaciones similares antes? ¿Cómo las manejaste?",
                "context": f"Vamos a trabajar en un escenario sobre {scenario.skill_type}. Tu respuesta nos ayudará a personalizar la experiencia.",
                "instructions": "Responde de forma honesta y detallada. No hay respuestas correctas o incorrectas, solo queremos conocer tu punto de partida.",
                "expected_skills": [scenario.skill_type],
                "estimated_time_minutes": 5,
                "evaluation_criteria": ["experiencia_previa", "autoconciencia", "reflexion"]
            }
    
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
    