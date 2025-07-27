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
            print(f" Procesando respuesta de simulación para sesión {session_id}...")
            session = await self._get_active_session(session_id)
            if not session:
                raise ValueError(f"Sesión {session_id} not found or not active")
            
           
            current_step = await self._get_current_step(session)
            if not current_step:
                raise ValueError(f"Current step not found for session {session_id}")


            updated_step = await self._update_step_with_response(current_step, request)
            
           
            scenario = await self.scenario_repository.find_by_id(session.scenario_id)
            
            
            evaluation = await self._evaluate_response(session, updated_step, scenario, request.user_response)
            
            
            ai_feedback = await self._generate_feedback(evaluation)
            
           
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
                    points_earned=session.scores.final_score if session.scores.final_score else 0,
                    user_id=session.user_id
                   
                
                )


                
                return SimulationCompletedResponseDTO(
                    session_id=session_id,
                    is_completed=True,
                    completion_feedback=completion_feedback,
                    message="Simulation completed successfully! Check your detailed feedback."
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
            raise Exception(f"Error processing simulation response: {str(e)}")
    
    async def _get_active_session(self, session_id: str) -> Optional[SimulationSession]:
        """Get active session by ID"""
        print(f"🔍 Looking for session: {session_id}")
        session = await self.simulation_session_repository.find_by_session_id(session_id)
        
        if not session:
            print(f"❌ Session {session_id} not found in database")
            return None
        
        print(f"✅ Session found: {session_id}, status: {session.status}")
        
        if session.status in [SimulationStatus.COMPLETED, SimulationStatus.ABANDONED]:
            print(f"❌ Session {session_id} is not active (status: {session.status})")
            return None
        
        print(f"✅ Session {session_id} is active")
        return session
        
    
    async def _get_current_step(self, session: SimulationSession) -> Optional[SimulationStep]:
        """Get current step of the simulation"""
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
        """Evaluate user response with AI"""
        
       
        scenario_context = f"""
    Scenario: {scenario.title}
    Description: {scenario.description}
    Initial situation: {scenario.initial_situation}
    Target skill: {session.skill_type}
    Difficulty level: {session.session_metadata.difficulty_level}
    """
        if step.step_type == StepType.PRE_TEST:
            
            evaluation_prompt = f"""
Evaluate this initial test response for the skill "{session.skill_type}":

TEST CONTEXT:
{step.content.context}

QUESTION:
{step.content.question}

USER RESPONSE:
{user_response}

Evaluate considering:
1. Level of experience demonstrated
2. Self-awareness about the skill
3. Reflection ability
4. Concrete examples provided

Respond ONLY in JSON format:
{{
    "overall_score": 75,
    "experience_level": "intermediate",
    "criteria_scores": {{
        "experience_demonstration": 80,
        "self_awareness": 70,
        "reflection_ability": 75,
        "concrete_examples": 80
    }},
    "strengths": ["Strength 1", "Strength 2"],
    "areas_for_improvement": ["Area 1", "Area 2"],
    "recommended_difficulty": 2,
    "specific_feedback": "Specific comments about the response"
}}
"""
        else:
           
            try:
                evaluation = await self.gemini_service.evaluate_response(scenario_context, user_response, session.skill_type)
                return evaluation
            except Exception as e:
               
                raise Exception(f"Error evaluating response: {str(e)}")
        
        try:
            response = await self.gemini_service._generate_content(evaluation_prompt)
            return self.gemini_service._parse_evaluation_response(response.content)
        except Exception as e:

           raise Exception(f"Error generating evaluation content: {str(e)}")

    async def _generate_feedback(self, evaluation: Dict[str, Any]) -> str:
        """Generate personalized feedback with AI"""
        try:
            feedback = await self.gemini_service.generate_feedback(evaluation)
            return feedback
        except Exception as e:
            
            score = evaluation.get("overall_score", 75)
            if score >= 80:
                return "Excellent answer! You demonstrate a good understanding of the situation. Continue to the next step."
            elif score >= 60:
                return "Good answer. There are some aspects you can improve, but you are on the right track."
            else:
                return "Your answer shows effort. We will help you further develop this skill in the next steps."
    
    async def _update_step_evaluation(self, step: SimulationStep, evaluation: Dict[str, Any], ai_feedback: str):
       
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
        """Determine next step of the simulation"""
        
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
        """Create next step of the simulation"""
        
        if next_step_info.get("step_type") == StepType.SIMULATION:
            
            scenario = await self.scenario_repository.find_by_id(session.scenario_id)
            
            prompt = f"""
Generate the next step in the simulation for the skill "{session.skill_type}".

SCENARIO CONTEXT:
- Title: {scenario.title}
- Situation: {scenario.initial_situation}
- Step number: {next_step_info['step_number']}

Create a specific situation that requires applying "{session.skill_type}" in greater depth.

Respond ONLY in JSON format:
{{
    "prompt": "Description of the new situation",
    "question": "Specific question for the user",
    "context": "Additional context for this step",
    "expected_response_type": "practice"
}}
"""
            
            try:
                response = await self.gemini_service._generate_content(prompt)
                content_data = self.gemini_service._parse_scenario_response(response.content)
            except Exception as e:
                
                raise Exception(f"Error generating next step content: {str(e)}")
            
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
        confidence_words = ["confident", "sure", "definitely", "certainly", "absolutely"]
        uncertainty_words = ["maybe", "perhaps", "possibly", "I think", "I'm not sure"]
        
        confidence_count = sum(1 for word in confidence_words if word.lower() in response.lower())
        uncertainty_count = sum(1 for word in uncertainty_words if word.lower() in response.lower())
        
        base_confidence = 5
        confidence_score = base_confidence + (confidence_count * 2) - (uncertainty_count * 1)
        
        return max(1, min(10, confidence_score))
    
    def _format_evaluation_for_response(self, evaluation: Dict[str, Any]) -> Dict[str, Any]:
        
        return {
            "score": evaluation.get("overall_score"),
            "level": evaluation.get("experience_level", "intermedio"),
            "strengths": evaluation.get("strengths", []),
            "improvements": evaluation.get("areas_for_improvement", [])
        }
    
    def _format_next_step_for_response(self, next_step: Optional[SimulationStep], next_step_info: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        
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
                "message": "Simulation completed successfully"
            }
        return None
    
    def _generate_response_message(self, step: SimulationStep, evaluation: Dict[str, Any], next_step_info: Optional[Dict[str, Any]]) -> str:
        
        score = evaluation.get("overall_score", 75)
        
        if next_step_info and next_step_info.get("is_completed"):
            return f"Simulation completed! Final score: {score}/100. Excellent work!"
        elif step.step_type == StepType.PRE_TEST:
            return f"Initial test completed (Score: {score}/100). Continuing with the simulation."
        else:
            return f"Response evaluated (Score: {score}/100). Proceeding to the next step."
