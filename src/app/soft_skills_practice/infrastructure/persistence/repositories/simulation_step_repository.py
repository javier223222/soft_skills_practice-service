from typing import List, Optional, Dict, Any
from ..models.simulation_models import SimulationStep
from ..models.base_models import StepType, MessageType
from .base_repository import BaseRepository

class SimulationStepRepository(BaseRepository[SimulationStep]):
    """Repositorio para gestionar pasos de simulación"""
    
    def __init__(self):
        super().__init__(SimulationStep)
    
    async def find_by_session_id(self, session_id: str) -> List[SimulationStep]:
        """Buscar todos los pasos de una sesión"""
        return await SimulationStep.find(
            SimulationStep.session_id == session_id
        ).sort(SimulationStep.step_number).to_list()
    
    async def find_by_session_and_step(self, session_id: str, step_number: int) -> Optional[SimulationStep]:
        """Buscar un paso específico de una sesión"""
        return await SimulationStep.find_one(
            SimulationStep.session_id == session_id,
            SimulationStep.step_number == step_number
        )
    
    async def find_by_step_type(self, session_id: str, step_type: StepType) -> List[SimulationStep]:
        """Buscar pasos por tipo en una sesión"""
        return await SimulationStep.find(
            SimulationStep.session_id == session_id,
            SimulationStep.step_type == step_type
        ).sort(SimulationStep.step_number).to_list()
    
    async def find_latest_step(self, session_id: str) -> Optional[SimulationStep]:
        """Buscar el último paso de una sesión"""
        return await SimulationStep.find(
            SimulationStep.session_id == session_id
        ).sort(-SimulationStep.step_number).first()
    
    async def count_steps_by_session(self, session_id: str) -> int:
        """Contar pasos de una sesión"""
        return await SimulationStep.find(
            SimulationStep.session_id == session_id
        ).count()
    
    async def get_session_conversation(self, session_id: str) -> List[Dict[str, Any]]:
        """Obtener conversación completa de una sesión"""
        steps = await self.find_by_session_id(session_id)
        
        conversation = []
        for step in steps:
            if step.content.question:
                conversation.append({
                    "type": "question",
                    "content": step.content.question,
                    "step_number": step.step_number,
                    "timestamp": step.created_at
                })
            
            if step.content.user_response:
                conversation.append({
                    "type": "user_response",
                    "content": step.content.user_response,
                    "step_number": step.step_number,
                    "timestamp": step.created_at
                })
            
            if step.content.ai_feedback:
                conversation.append({
                    "type": "ai_feedback",
                    "content": step.content.ai_feedback,
                    "step_number": step.step_number,
                    "timestamp": step.created_at
                })
        
        return conversation
    
    async def get_step_analytics(self, session_id: str) -> Dict[str, Any]:
        """Obtener análiticas de los pasos de una sesión"""
        steps = await self.find_by_session_id(session_id)
        
        if not steps:
            return {
                "total_steps": 0,
                "average_response_time": 0,
                "total_help_requests": 0,
                "average_response_length": 0
            }
        
        response_times = [s.interaction_tracking.time_to_respond for s in steps 
                         if s.interaction_tracking.time_to_respond is not None]
        
        response_lengths = [s.interaction_tracking.response_length for s in steps 
                           if s.interaction_tracking.response_length > 0]
        
        help_requests = sum(1 for s in steps if s.interaction_tracking.help_requested)
        
        return {
            "total_steps": len(steps),
            "average_response_time": sum(response_times) / len(response_times) if response_times else 0,
            "total_help_requests": help_requests,
            "average_response_length": sum(response_lengths) / len(response_lengths) if response_lengths else 0
        }
    
    async def update_step_evaluation(self, session_id: str, step_number: int, 
                                   evaluation_data: Dict[str, Any]) -> bool:
        """Actualizar evaluación de un paso"""
        step = await self.find_by_session_and_step(session_id, step_number)
        if step:
            if step.evaluation:
                step.evaluation.step_score = evaluation_data.get("step_score")
                step.evaluation.criteria_scores = evaluation_data.get("criteria_scores", {})
                step.evaluation.strengths = evaluation_data.get("strengths", [])
                step.evaluation.areas_for_improvement = evaluation_data.get("areas_for_improvement", [])
                step.evaluation.specific_feedback = evaluation_data.get("specific_feedback")
            
            await step.save()
            return True
        return False