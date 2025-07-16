from typing import List,Optional,Dict,Any
from datetime import datetime,timedelta
from ..models.simulation_models import SimulationSession
from ..models.base_models import SimulationStatus
from .base_repository import BaseRepository

class SimulationSessionRepository(BaseRepository[SimulationSession]):
    def __init__(self):
        super().__init__(SimulationSession)
    
    async def find_by_session_id(self, session_id: str) -> Optional[SimulationSession]:
        
        
        return await SimulationSession.find_one(
            SimulationSession.session_id == session_id
        )
    
    async def find_by_user_id(self, user_id: str, limit: int = 20) -> List[SimulationSession]:
        """Buscar todas las sesiones de un usuario"""
        return await SimulationSession.find(
            SimulationSession.user_id == user_id
        ).sort(-SimulationSession.created_at).limit(limit).to_list()
    
    async def find_by_user_and_skill(self, user_id: str, skill_type: str) -> List[SimulationSession]:
        """Buscar sesiones de un usuario para una habilidad específica"""
        return await SimulationSession.find(
            SimulationSession.user_id == user_id,
            SimulationSession.skill_type == skill_type
        ).sort(-SimulationSession.created_at).to_list()
    
    async def find_active_sessions(self, user_id: str) -> List[SimulationSession]:
        """Buscar sesiones activas (no completadas) de un usuario"""
        return await SimulationSession.find(
            SimulationSession.user_id == user_id,
            SimulationSession.status.in_([
                SimulationStatus.STARTED,
                SimulationStatus.PRE_TEST,
                SimulationStatus.SIMULATION
            ])
        ).to_list()
    
    async def find_completed_sessions(self, user_id: str, limit: int = 10) -> List[SimulationSession]:
        """Buscar sesiones completadas de un usuario"""
        return await SimulationSession.find(
            SimulationSession.user_id == user_id,
            SimulationSession.status == SimulationStatus.COMPLETED
        ).sort(-SimulationSession.created_at).limit(limit).to_list()
    
    async def find_by_skill_type(self, skill_type: str, limit: int = 50) -> List[SimulationSession]:
        """Buscar sesiones por tipo de habilidad"""
        return await SimulationSession.find(
            SimulationSession.skill_type == skill_type
        ).sort(-SimulationSession.created_at).limit(limit).to_list()
    
    async def find_recent_sessions(self, days: int = 7) -> List[SimulationSession]:
        """Buscar sesiones recientes"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        return await SimulationSession.find(
            SimulationSession.created_at >= cutoff_date
        ).sort(-SimulationSession.created_at).to_list()
    
    async def update_session_status(self, session_id: str, status: SimulationStatus) -> bool:
        """Actualizar estado de una sesión"""
        session = await self.find_by_session_id(session_id)
        if session:
            session.status = status
            session.updated_at = datetime.utcnow()
            await session.save()
            return True
        return False
    
    async def update_current_step(self, session_id: str, step_number: int) -> bool:
        """Actualizar paso actual de una sesión"""
        session = await self.find_by_session_id(session_id)
        if session:
            session.current_step = step_number
            session.updated_at = datetime.utcnow()
            await session.save()
            return True
        return False
    
    async def get_user_stats(self, user_id: str) -> Dict[str, Any]:
        """Obtener estadísticas de un usuario"""
        total_sessions = await SimulationSession.find(
            SimulationSession.user_id == user_id
        ).count()
        
        completed_sessions = await SimulationSession.find(
            SimulationSession.user_id == user_id,
            SimulationSession.status == SimulationStatus.COMPLETED
        ).count()
        
        skills_practiced = await SimulationSession.find(
            SimulationSession.user_id == user_id
        ).distinct("skill_type")
        
        return {
            "total_sessions": total_sessions,
            "completed_sessions": completed_sessions,
            "completion_rate": (completed_sessions / total_sessions * 100) if total_sessions > 0 else 0,
            "skills_practiced": skills_practiced,
            "unique_skills_count": len(skills_practiced)
        }
    
    async def get_skill_performance(self, user_id: str, skill_type: str) -> Dict[str, Any]:
        """Obtener rendimiento de un usuario en una habilidad específica"""
        sessions = await self.find_by_user_and_skill(user_id, skill_type)
        
        if not sessions:
            return {
                "skill_type": skill_type,
                "sessions_count": 0,
                "average_score": 0,
                "best_score": 0,
                "improvement_trend": 0
            }
        
        completed_sessions = [s for s in sessions if s.status == SimulationStatus.COMPLETED]
        scores = [s.scores.final_score for s in completed_sessions if s.scores.final_score is not None]
        
        if not scores:
            return {
                "skill_type": skill_type,
                "sessions_count": len(sessions),
                "average_score": 0,
                "best_score": 0,
                "improvement_trend": 0
            }
        
        return {
            "skill_type": skill_type,
            "sessions_count": len(sessions),
            "average_score": sum(scores) / len(scores),
            "best_score": max(scores),
            "improvement_trend": scores[-1] - scores[0] if len(scores) > 1 else 0
        }   