from typing import List
from ..dtos.simple_skill_dtos import SimpleUserSkillProgressDTO, SimpleUserProgressResponseDTO
from ...infrastructure.persistence.repositories.simulation_session_repository import SimulationSessionRepository
from ...infrastructure.persistence.models.base_models import SimulationStatus


class GetUserProgressUseCase:
    def __init__(self, simulation_session_repository: SimulationSessionRepository):
        self.simulation_session_repository = simulation_session_repository
    
    async def execute(self, user_id: str, auto_register: bool = True) -> SimpleUserProgressResponseDTO:
        """Obtener el progreso del usuario en todas las soft skills"""
        try:
           
            if not user_id or user_id.strip() == "":
                raise ValueError("El user_id no puede estar vacío")
            
           
            user_sessions = await self.simulation_session_repository.find_by_user_id(user_id)
            
            
            
            if not user_sessions and auto_register:
                
                return SimpleUserProgressResponseDTO(
                    user_id=user_id,
                    total_skills_practiced=0,
                    skills_progress=[]
                )
            
            
            
            skills_progress = {}
            
            for session in user_sessions:
                skill_id = session.skill_type  
                
                if skill_id not in skills_progress:
                    skills_progress[skill_id] = {
                        'total_sessions': 0,
                        'completed_sessions': 0,
                        'total_score': 0.0,
                        'session_count': 0
                    }
                
                skills_progress[skill_id]['total_sessions'] += 1
                
                if session.status == SimulationStatus.COMPLETED:
                    skills_progress[skill_id]['completed_sessions'] += 1
                    if session.scores.final_score is not None:
                        skills_progress[skill_id]['total_score'] += session.scores.final_score
                        skills_progress[skill_id]['session_count'] += 1
            
            
            progress_dtos = []
            for skill_id, progress in skills_progress.items():
                
                completion_rate = progress['completed_sessions'] / progress['total_sessions'] if progress['total_sessions'] > 0 else 0
                avg_score = progress['total_score'] / progress['session_count'] if progress['session_count'] > 0 else 0
                
                
                progress_percentage = (completion_rate * 0.7 + (avg_score / 100) * 0.3) * 100
                progress_percentage = min(100.0, max(0.0, progress_percentage))
                
                progress_dto = SimpleUserSkillProgressDTO(
                    skill_id=skill_id,
                    progress_percentage=round(progress_percentage, 2),
                    total_sessions=progress['total_sessions'],
                    completed_sessions=progress['completed_sessions'],
                    average_score=round(avg_score, 2) if avg_score > 0 else None
                )
                progress_dtos.append(progress_dto)
            
            return SimpleUserProgressResponseDTO(
                user_id=user_id,
                total_skills_practiced=len(progress_dtos),
                skills_progress=progress_dtos
            )
            
        except Exception as e:
            raise Exception(f"Error al obtener progreso del usuario: {str(e)}")