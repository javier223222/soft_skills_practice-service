import uuid
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from ..dtos.simulation_dtos import (
    RespondSimulationRequestDTO,
    SimulationResponseDTO,
    SimulationCompletedResponseDTO
)
from ...infrastructure.persistence.repositories.simulation_session_repository import SimulationSessionRepository
from ...infrastructure.persistence.repositories.simulation_step_repository import SimulationStepRepository
from ...infrastructure.persistence.repositories.scenario_repository import ScenarioRepository
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
    EvaluationData,
    ResponseAnalysis
)
from ..services.gemini_service import GeminiService
from ..services.user_mobile_service import UserMobileService
from .generate_completion_feedback_use_case import GenerateCompletionFeedbackUseCase


from ...infrastructure.messaging.event_publisher import EventPublisher
class RespondSimulationUseCase:
    def __init__(
        self,
        simulation_session_repository: SimulationSessionRepository,
        simulation_step_repository: SimulationStepRepository,
        scenario_repository: ScenarioRepository,
        gemini_service: GeminiService,
        generate_completion_feedback_use_case: GenerateCompletionFeedbackUseCase = None,
        event_publisher: EventPublisher = None,
       
    ):
        self.simulation_session_repository = simulation_session_repository
        self.simulation_step_repository = simulation_step_repository
        self.scenario_repository = scenario_repository
        self.gemini_service = gemini_service
        self.generate_completion_feedback_use_case = generate_completion_feedback_use_case
        self.event_publisher = event_publisher
      
    
    async def execute(self, session_id: str, request: RespondSimulationRequestDTO):
        
        try:
            print(f"🔄 Procesando respuesta de simulación para sesión {session_id}...")
            session = await self._get_active_session(session_id)
            if not session:
                raise ValueError(f"Sesión {session_id} no encontrada o no está activa")
            
           
            current_step = await self._get_current_step(session)
            if not current_step:
                raise ValueError(f"No se encontró el paso actual para la sesión {session_id}")
            
            
            updated_step = await self._update_step_with_response(current_step, request)
            
           
            scenario = await self.scenario_repository.find_by_id(session.scenario_id)
            
            
            evaluation = await self._evaluate_response(session, updated_step, scenario, request.user_response)
            
            
            ai_feedback = await self._generate_feedback(evaluation, session, scenario)
            
           
            await self._update_step_evaluation(updated_step, evaluation, ai_feedback)
            
            
            next_step_info = await self._determine_next_step(session, updated_step, evaluation)
            
            
            next_step = None
            if next_step_info and not next_step_info.get("is_completed", False):
                next_step = await self._create_next_step(session, next_step_info)
            
            
            await self._update_session_progress(session, evaluation, next_step_info)
            
            
            is_completed = next_step_info.get("is_completed", False) if next_step_info else False

            
            if is_completed and self.generate_completion_feedback_use_case:
                
                completion_feedback = await self.generate_completion_feedback_use_case.execute(session_id)
          
        
                await self.event_publisher.publish_simulation_finished(
                   feedbackResult={
                "is_completed": True,
                "completion_feedback": {
                    "session_id": completion_feedback.session_id,
                    "user_id": completion_feedback.user_id,
                    "scenario_title": completion_feedback.scenario_title,
                    "skill_type": completion_feedback.skill_type,
                    "completion_status": completion_feedback.completion_status,
                    "performance": {
                        "overall_score": completion_feedback.performance.overall_score,
                        "average_step_score": completion_feedback.performance.average_step_score,
                        "total_time_minutes": completion_feedback.performance.total_time_minutes,
                        "average_response_time_seconds": completion_feedback.performance.average_response_time_seconds,
                        "help_requests_count": completion_feedback.performance.help_requests_count,
                        "completion_percentage": completion_feedback.performance.completion_percentage,
                        "confidence_level": completion_feedback.performance.confidence_level
                    },
                }
                   }
                )


                
                return SimulationCompletedResponseDTO(
                    session_id=session_id,
                    is_completed=True,
                    completion_feedback=completion_feedback,
                    message="¡Simulación completada exitosamente! Revisa tu feedback detallado."
                )
            
           
            response = SimulationResponseDTO(
                session_id=session_id,
                step_number=updated_step.step_number,
                user_response=request.user_response,
                ai_feedback=ai_feedback,
                evaluation=self._format_evaluation_for_response(evaluation),
                next_step=self._format_next_step_for_response(next_step, next_step_info),
                is_completed=is_completed,
                message=self._generate_response_message(updated_step, evaluation, next_step_info)
            )
            
            return response
            
        except Exception as e:
            raise Exception(f"Error al procesar respuesta de simulación: {str(e)}")
    
    async def _get_active_session(self, session_id: str) -> Optional[SimulationSession]:
        """Obtener sesión activa por ID"""
        session = await self.simulation_session_repository.find_by_session_id(session_id)
        if not session or session.status != SimulationStatus.STARTED or session.status != SimulationStatus.SIMULATION or session.status != SimulationStatus.PRE_TEST or session.status == SimulationStatus.COMPLETED or session.status == SimulationStatus.ABANDONED:
            return None
        
        return session
        
    
    async def _get_current_step(self, session: SimulationSession) -> Optional[SimulationStep]:
        """Obtener el paso actual de la simulación"""
        steps = await self.simulation_step_repository.find_by_session_id(session.session_id)
        if steps:
            
            steps.sort(key=lambda x: x.step_number, reverse=True)
            return steps[0]
        return None
    
    async def _update_step_with_response(self, step: SimulationStep, request: RespondSimulationRequestDTO) -> SimulationStep:
        """Actualizar el paso con la respuesta del usuario"""
        
        step.content.user_response = request.user_response
        
        
        step.interaction_tracking.time_to_respond = request.response_time_seconds
        step.interaction_tracking.response_length = len(request.user_response)
        step.interaction_tracking.help_requested = request.help_requested
        
       
        words = request.user_response.split()
        sentences = request.user_response.split('.')
        
        step.response_analysis = ResponseAnalysis(
            word_count=len(words),
            sentence_count=len([s for s in sentences if s.strip()]),
            confidence_level=self._analyze_confidence_level(request.user_response)
        )
        
        
        await step.save()
        return step
    
    async def _evaluate_response(self, session: SimulationSession, step: SimulationStep, scenario, user_response: str) -> Dict[str, Any]:
        """Evaluar la respuesta del usuario con IA"""
        
       
        scenario_context = f"""
Escenario: {scenario.title}
Descripción: {scenario.description}
Situación inicial: {scenario.initial_situation}
Habilidad objetivo: {session.skill_type}
Nivel de dificultad: {session.session_metadata.difficulty_level}
"""
        
        if step.step_type == StepType.PRE_TEST:
            
            evaluation_prompt = f"""
Evalúa esta respuesta de test inicial para la habilidad "{session.skill_type}":

CONTEXTO DEL TEST:
{step.content.context}

PREGUNTA:
{step.content.question}

RESPUESTA DEL USUARIO:
{user_response}

Evalúa considerando:
1. Nivel de experiencia demostrado
2. Autoconciencia sobre la habilidad
3. Capacidad de reflexión
4. Ejemplos concretos proporcionados

Responde ÚNICAMENTE en formato JSON:
{{
    "overall_score": 75,
    "experience_level": "intermedio",
    "criteria_scores": {{
        "experience_demonstration": 80,
        "self_awareness": 70,
        "reflection_ability": 75,
        "concrete_examples": 80
    }},
    "strengths": ["Fortaleza 1", "Fortaleza 2"],
    "areas_for_improvement": ["Área 1", "Área 2"],
    "recommended_difficulty": 2,
    "specific_feedback": "Comentarios específicos sobre la respuesta"
}}
"""
        else:
           
            try:
                evaluation = await self.gemini_service.evaluate_response(scenario_context, user_response, session.skill_type)
                return evaluation
            except Exception as e:
               
                return {
                    "overall_score": 75,
                    "criteria_scores": {
                        "skill_application": 75,
                        "communication_clarity": 75,
                        "problem_solving": 75
                    },
                    "strengths": ["Respuesta estructurada"],
                    "areas_for_improvement": ["Agregar más detalles específicos"],
                    "specific_feedback": "Respuesta adecuada. Continúa desarrollando la habilidad."
                }
        
        try:
            response = await self.gemini_service._generate_content(evaluation_prompt)
            return self.gemini_service._parse_evaluation_response(response.content)
        except Exception as e:
           
            return {
                "overall_score": 75,
                "experience_level": "intermedio",
                "criteria_scores": {
                    "experience_demonstration": 75,
                    "self_awareness": 70,
                    "reflection_ability": 75,
                    "concrete_examples": 75
                },
                "strengths": ["Respuesta reflexiva"],
                "areas_for_improvement": ["Proporcionar más ejemplos específicos"],
                "recommended_difficulty": 2,
                "specific_feedback": "Buen punto de partida. Vamos a trabajar en desarrollar esta habilidad."
            }
    
    async def _generate_feedback(self, evaluation: Dict[str, Any], session: SimulationSession, scenario) -> str:
        """Generar feedback personalizado con IA"""
        try:
            feedback = await self.gemini_service.generate_feedback(evaluation)
            return feedback
        except Exception as e:
            
            score = evaluation.get("overall_score", 75)
            if score >= 80:
                return "¡Excelente respuesta! Demuestras un buen entendimiento de la situación. Continúa con el siguiente paso."
            elif score >= 60:
                return "Buena respuesta. Hay algunos aspectos que puedes mejorar, pero vas por buen camino."
            else:
                return "Tu respuesta muestra esfuerzo. Te ayudaremos a desarrollar mejor esta habilidad en los siguientes pasos."
    
    async def _update_step_evaluation(self, step: SimulationStep, evaluation: Dict[str, Any], ai_feedback: str):
        """Actualizar el paso con la evaluación y feedback"""
        step.evaluation = EvaluationData(
            step_score=evaluation.get("overall_score"),
            criteria_scores=evaluation.get("criteria_scores", {}),
            strengths=evaluation.get("strengths", []),
            areas_for_improvement=evaluation.get("areas_for_improvement", []),
            specific_feedback=evaluation.get("specific_feedback")
        )
        
        step.content.ai_feedback = ai_feedback
        
        await step.save()
    
    async def _determine_next_step(self, session: SimulationSession, current_step: SimulationStep, evaluation: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Determinar el siguiente paso de la simulación"""
        
        if current_step.step_type == StepType.PRE_TEST:
            
            return {
                "step_type": StepType.SIMULATION,
                "message_type": MessageType.SIMULATION_PROMPT,
                "step_number": current_step.step_number + 1,
                "is_completed": False
            }
        elif current_step.step_type == StepType.SIMULATION:
           
            if current_step.step_number >= session.total_steps - 1:
                return {
                    "step_type": StepType.FEEDBACK,
                    "message_type": MessageType.FINAL_SUMMARY,
                    "step_number": current_step.step_number + 1,
                    "is_completed": True
                }
            else:
               
                return {
                    "step_type": StepType.SIMULATION,
                    "message_type": MessageType.SIMULATION_PROMPT,
                    "step_number": current_step.step_number + 1,
                    "is_completed": False
                }
        else:
            
            return {
                "is_completed": True
            }
    
    async def _create_next_step(self, session: SimulationSession, next_step_info: Dict[str, Any]) -> Optional[SimulationStep]:
        """Crear el siguiente paso de la simulación"""
        
        if next_step_info.get("step_type") == StepType.SIMULATION:
            
            scenario = await self.scenario_repository.find_by_id(session.scenario_id)
            
            prompt = f"""
Genera el siguiente paso en la simulación de la habilidad "{session.skill_type}".

CONTEXTO DEL ESCENARIO:
- Título: {scenario.title}
- Situación: {scenario.initial_situation}
- Paso número: {next_step_info['step_number']}

Genera una situación específica que requiera aplicar "{session.skill_type}" con mayor profundidad.

Responde ÚNICAMENTE en formato JSON:
{{
    "prompt": "Descripción de la nueva situación",
    "question": "Pregunta específica para el usuario",
    "context": "Contexto adicional para este paso",
    "expected_response_type": "práctica"
}}
"""
            
            try:
                response = await self.gemini_service._generate_content(prompt)
                content_data = self.gemini_service._parse_scenario_response(response.content)
            except Exception as e:
                
                content_data = {
                    "prompt": f"Continuando con el escenario de {scenario.title}",
                    "question": f"¿Cómo aplicarías {session.skill_type} en esta nueva fase de la situación?",
                    "context": "Profundiza en la aplicación de la habilidad",
                    "expected_response_type": "práctica"
                }
            
            step = SimulationStep(
                session_id=session.session_id,
                step_number=next_step_info["step_number"],
                step_type=next_step_info["step_type"],
                message_type=next_step_info["message_type"],
                content=StepContent(
                    question=content_data["question"],
                    context=content_data["context"]
                ),
                interaction_tracking=InteractionTracking(),
                context={
                    "prompt": content_data["prompt"],
                    "expected_response_type": content_data["expected_response_type"]
                }
            )
            
            return await self.simulation_step_repository.create(step)
        
        return None
    
    async def _update_session_progress(self, session: SimulationSession, evaluation: Dict[str, Any], next_step_info: Optional[Dict[str, Any]]):
        """Actualizar el progreso de la sesión"""
        
        if next_step_info:
            if next_step_info.get("is_completed"):
                session.status = SimulationStatus.COMPLETED
                session.session_metadata.completed_at = datetime.now(timezone.utc)
            else:
                session.current_step = next_step_info["step_number"]
                if session.status == SimulationStatus.STARTED:
                    session.status = SimulationStatus.SIMULATION
        
        session.end_at = datetime.now(timezone.utc) if session.status == SimulationStatus.COMPLETED else None
        if evaluation.get("overall_score"):
            session.scores.simulation_steps_scores.append(evaluation["overall_score"])
            if session.status == SimulationStatus.COMPLETED:
                session.scores.final_score = sum(session.scores.simulation_steps_scores) // len(session.scores.simulation_steps_scores)
        
        session.updated_at = datetime.now(timezone.utc)
        await self.simulation_session_repository.update(session)
    
    def _analyze_confidence_level(self, response: str) -> int:
        """Analizar nivel de confianza basado en palabras clave"""
        confidence_words = ["seguro", "confiado", "definitivamente", "ciertamente", "absolutamente"]
        uncertainty_words = ["tal vez", "quizás", "posiblemente", "creo que", "no estoy seguro"]
        
        confidence_count = sum(1 for word in confidence_words if word.lower() in response.lower())
        uncertainty_count = sum(1 for word in uncertainty_words if word.lower() in response.lower())
        
        base_confidence = 5
        confidence_score = base_confidence + (confidence_count * 2) - (uncertainty_count * 1)
        
        return max(1, min(10, confidence_score))
    
    def _format_evaluation_for_response(self, evaluation: Dict[str, Any]) -> Dict[str, Any]:
        """Formatear evaluación para la respuesta al cliente"""
        return {
            "score": evaluation.get("overall_score"),
            "level": evaluation.get("experience_level", "intermedio"),
            "strengths": evaluation.get("strengths", []),
            "improvements": evaluation.get("areas_for_improvement", [])
        }
    
    def _format_next_step_for_response(self, next_step: Optional[SimulationStep], next_step_info: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Formatear información del siguiente paso"""
        if next_step:
            return {
                "step_id": str(next_step.id),
                "step_number": next_step.step_number,
                "question": next_step.content.question,
                "context": next_step.content.context,
                "type": next_step.step_type.value
            }
        elif next_step_info and next_step_info.get("is_completed"):
            return {
                "type": "completed",
                "message": "Simulación completada exitosamente"
            }
        return None
    
    def _generate_response_message(self, step: SimulationStep, evaluation: Dict[str, Any], next_step_info: Optional[Dict[str, Any]]) -> str:
        """Generar mensaje de respuesta"""
        score = evaluation.get("overall_score", 75)
        
        if next_step_info and next_step_info.get("is_completed"):
            return f"¡Simulación completada! Puntuación final: {score}/100. ¡Excelente trabajo!"
        elif step.step_type == StepType.PRE_TEST:
            return f"Test inicial completado (Puntuación: {score}/100). Continuando con la simulación."
        else:
            return f"Respuesta evaluada (Puntuación: {score}/100). Continuando con el siguiente paso."
