from typing import Optional, List, Dict, Any
from ..dtos.simulation_dtos import SimulationSessionDTO, SimulationStepDTO
from ...infrastructure.persistence.repositories.simulation_session_repository import SimulationSessionRepository
from ...infrastructure.persistence.repositories.simulation_step_repository import SimulationStepRepository
from ...infrastructure.persistence.repositories.scenario_repository import ScenarioRepository


class GetSimulationStatusDTO:
    """DTO para respuesta del estado de simulación"""
    def __init__(
        self,
        session_info: SimulationSessionDTO,
        scenario_info: Dict[str, Any],
        steps_completed: List[Dict[str, Any]],
        current_step: Optional[Dict[str, Any]],
        progress_summary: Dict[str, Any],
        is_active: bool
    ):
        self.session_info = session_info
        self.scenario_info = scenario_info
        self.steps_completed = steps_completed
        self.current_step = current_step
        self.progress_summary = progress_summary
        self.is_active = is_active


class GetSimulationStatusUseCase:
    def __init__(
        self,
        simulation_session_repository: SimulationSessionRepository,
        simulation_step_repository: SimulationStepRepository,
        scenario_repository: ScenarioRepository
    ):
        self.simulation_session_repository = simulation_session_repository
        self.simulation_step_repository = simulation_step_repository
        self.scenario_repository = scenario_repository
    
    async def execute(self, session_id: str) -> GetSimulationStatusDTO:
        """Obtener el estado completo de una simulación"""
        try:
           
            session = await self.simulation_session_repository.find_by_session_id(session_id)
            if not session:
                raise ValueError(f"Sesión {session_id} is not found")
           
            scenario = await self.scenario_repository.find_by_id(session.scenario_id)
            if not scenario:
                raise ValueError(f"Escenario {session.scenario_id} is not found")

            
            steps = await self.simulation_step_repository.find_by_session_id(session_id)
            steps.sort(key=lambda x: x.step_number)
            
           
            session_info = SimulationSessionDTO(
                session_id=session.session_id,
                user_id=session.user_id,
                scenario_id=session.scenario_id,
                skill_type=session.skill_type,
                status=session.status.value,
                current_step=session.current_step,
                total_steps=session.total_steps,
                started_at=session.session_metadata.started_at,
                difficulty_level=session.session_metadata.difficulty_level
            )
            
            
            scenario_info = {
                "scenario_id": str(scenario.id),
                "title": scenario.title,
                "description": scenario.description,
                "skill_type": scenario.skill_type,
                "difficulty_level": scenario.difficulty_level,
                "estimated_duration": scenario.estimated_duration,
                "initial_situation": scenario.initial_situation
            }
            
            # 6. Procesar pasos completados
            steps_completed = []
            current_step_info = None
            
            for step in steps:
                step_data = {
                    "step_id": str(step.id),
                    "step_number": step.step_number,
                    "step_type": step.step_type.value,
                    "message_type": step.message_type.value,
                    "question": step.content.question,
                    "user_response": step.content.user_response,
                    "ai_feedback": step.content.ai_feedback,
                    "created_at": step.created_at.isoformat(),
                    "is_completed": step.content.user_response is not None
                }
                
                # Agregar evaluación si existe
                if step.evaluation:
                    step_data["evaluation"] = {
                        "score": step.evaluation.step_score,
                        "criteria_scores": step.evaluation.criteria_scores,
                        "strengths": step.evaluation.strengths,
                        "areas_for_improvement": step.evaluation.areas_for_improvement,
                        "feedback": step.evaluation.specific_feedback
                    }
                
                # Agregar tracking de interacción si existe
                if step.interaction_tracking:
                    step_data["interaction"] = {
                        "response_time_seconds": step.interaction_tracking.time_to_respond,
                        "response_length": step.interaction_tracking.response_length,
                        "help_requested": step.interaction_tracking.help_requested
                    }
                
                if step_data["is_completed"]:
                    steps_completed.append(step_data)
                else:
                    current_step_info = step_data
            
            # 7. Calcular resumen de progreso
            completed_steps = len(steps_completed)
            total_steps = session.total_steps
            progress_percentage = (completed_steps / total_steps) * 100 if total_steps > 0 else 0
            
            # Calcular puntuación promedio
            scores = [step.evaluation.step_score for step in steps if step.evaluation and step.evaluation.step_score]
            average_score = sum(scores) / len(scores) if scores else 0
            
            progress_summary = {
                "completed_steps": completed_steps,
                "total_steps": total_steps,
                "progress_percentage": round(progress_percentage, 1),
                "average_score": round(average_score, 1),
                "estimated_completion_time": self._calculate_estimated_completion(session, steps),
                "time_spent_minutes": self._calculate_time_spent(session, steps),
                "status_description": self._get_status_description(session.status.value, completed_steps, total_steps)
            }
            
            # 8. Determinar si la simulación está activa
            is_active = session.status.value in ["started", "pre_test", "simulation"]
            
            return GetSimulationStatusDTO(
                session_info=session_info,
                scenario_info=scenario_info,
                steps_completed=steps_completed,
                current_step=current_step_info,
                progress_summary=progress_summary,
                is_active=is_active
            )
            
        except Exception as e:
            raise Exception(f"Error fetching simulation status: {str(e)}")

    def _calculate_estimated_completion(self, session, steps) -> int:
        """Calcular tiempo estimado para completar (en minutos)"""
        completed_steps = len([s for s in steps if s.content.user_response])
        remaining_steps = session.total_steps - completed_steps
        
        # Estimar 5 minutos por paso restante
        return remaining_steps * 5
    
    def _calculate_time_spent(self, session, steps) -> int:
        """Calcular tiempo total gastado (en minutos)"""
        if not steps:
            return 0
        
        # Calcular desde el inicio hasta el último paso
        start_time = session.session_metadata.started_at
        last_step_time = max(step.created_at for step in steps) if steps else start_time
        
        time_diff = last_step_time - start_time
        return max(1, int(time_diff.total_seconds() / 60))
    
    def _get_status_description(self, status: str, completed: int, total: int) -> str:
        """Generate status description"""
        if status == "started":
            return "Simulation started - Waiting for initial test response"
        elif status == "pre_test":
            return "Completing initial test"
        elif status == "simulation":
            return f"In progress - Step {completed} of {total}"
        elif status == "completed":
            return "Simulation successfully completed"
        elif status == "abandoned":
            return "Simulation abandoned"
        else:
            return f"Status: {status}"
