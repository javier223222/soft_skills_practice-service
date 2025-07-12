from typing import Optional
from datetime import datetime, timedelta
import math
from ..dtos.user_mobile_dtos import (
    UserLevelDTO, 
    UserAchievementDTO, 
    UserStatsDTO,
    TaskCompletionResponseDTO
)
from ...infrastructure.persistence.repositories.simulation_session_repository import SimulationSessionRepository


class UserMobileService:
    """Servicio para funcionalidades específicas de la aplicación móvil"""
    
    def __init__(self, simulation_session_repository: SimulationSessionRepository):
        self.simulation_session_repository = simulation_session_repository
    
    async def get_user_level_info(self, user_id: str) -> UserLevelDTO:
        """Obtener información del nivel del usuario"""
        try:
            # Obtener todas las sesiones del usuario
            user_sessions = await self.simulation_session_repository.find_by_user_id(user_id)
            
            # Calcular puntos totales basado en las puntuaciones
            total_points = 0
            completed_simulations = 0
            
            for session in user_sessions:
                if session.scores.final_score and session.scores.final_score > 0:
                    # Convertir puntuación (0-100) a puntos (0-10 por simulación)
                    points = int(session.scores.final_score / 10)
                    total_points += points
                    completed_simulations += 1
            
            # Calcular nivel actual (cada 100 puntos = 1 nivel)
            current_level = max(1, total_points // 100)
            
            # Puntos en el nivel actual
            points_in_current_level = total_points % 100
            
            # Puntos necesarios para el siguiente nivel
            points_to_next_level = 100 - points_in_current_level
            
            # Progreso porcentual en el nivel actual
            level_progress = (points_in_current_level / 100) * 100
            
            # Número de logros (simplificado)
            achievements_count = self._calculate_achievements_count(total_points, completed_simulations)
            
            return UserLevelDTO(
                user_id=user_id,
                current_level=current_level,
                current_points=points_in_current_level,
                points_to_next_level=points_to_next_level,
                total_points_earned=total_points,
                level_progress_percentage=round(level_progress, 1),
                achievements_unlocked=achievements_count,
                simulations_completed=completed_simulations
            )
            
        except Exception as e:
            # Valores por defecto para usuarios nuevos
            return UserLevelDTO(
                user_id=user_id,
                current_level=1,
                current_points=0,
                points_to_next_level=100,
                total_points_earned=0,
                level_progress_percentage=0.0,
                achievements_unlocked=0,
                simulations_completed=0
            )
    
    async def get_user_achievements(self, user_id: str) -> list[UserAchievementDTO]:
        """Obtener logros del usuario"""
        try:
            user_sessions = await self.simulation_session_repository.find_by_user_id(user_id)
            achievements = []
            
            completed_count = len([s for s in user_sessions if s.scores.final_score and s.scores.final_score > 0])
            total_score = sum([s.scores.final_score for s in user_sessions if s.scores.final_score])
            avg_score = total_score / completed_count if completed_count > 0 else 0
            
            # Logro por primera simulación
            if completed_count >= 1:
                achievements.append(UserAchievementDTO(
                    achievement_id="first_simulation",
                    title="First Steps",
                    description="Completed your first simulation",
                    icon="🎯",
                    unlocked_at=user_sessions[0].session_metadata.started_at,
                    rarity="common"
                ))
            
            # Logro por 5 simulaciones
            if completed_count >= 5:
                achievements.append(UserAchievementDTO(
                    achievement_id="simulation_master",
                    title="Simulation Master",
                    description="Completed 5 simulations",
                    icon="🏆",
                    unlocked_at=datetime.utcnow(),
                    rarity="rare"
                ))
            
            # Logro por alta puntuación
            if avg_score >= 85:
                achievements.append(UserAchievementDTO(
                    achievement_id="high_performer",
                    title="High Performer",
                    description="Maintained 85+ average score",
                    icon="⭐",
                    unlocked_at=datetime.utcnow(),
                    rarity="epic"
                ))
            
            # Logro por perfect score
            perfect_scores = [s for s in user_sessions if s.scores.final_score and s.scores.final_score >= 95]
            if perfect_scores:
                achievements.append(UserAchievementDTO(
                    achievement_id="perfectionist",
                    title="Perfectionist",
                    description="Achieved 95+ score in a simulation",
                    icon="💎",
                    unlocked_at=perfect_scores[0].session_metadata.started_at,
                    rarity="legendary"
                ))
            
            return achievements
            
        except Exception as e:
            return []
    
    async def calculate_task_completion_response(self, user_id: str, simulation_score: float) -> TaskCompletionResponseDTO:
        """Calcular respuesta de finalización de tarea para la app móvil"""
        try:
            # Obtener info actual del usuario
            current_level_info = await self.get_user_level_info(user_id)
            
            # Calcular puntos ganados en esta simulación
            points_earned = int(simulation_score / 10)  # Convertir score 0-100 a puntos 0-10
            
            # Calcular nuevos totales
            new_total_points = current_level_info.total_points_earned + points_earned
            new_level = max(1, new_total_points // 100)
            
            # Verificar si subió de nivel
            level_up = new_level > current_level_info.current_level
            
            # Calcular puntos para el siguiente nivel
            points_in_new_level = new_total_points % 100
            points_to_next_level = 100 - points_in_new_level
            
            # Verificar si desbloqueó un logro
            achievement_unlocked = await self._check_new_achievement(user_id, simulation_score)
            
            # Mensaje de celebración
            if level_up:
                celebration_message = f"🎉 Level up! You reached level {new_level}!"
            elif points_earned >= 8:
                celebration_message = "🌟 Excellent performance!"
            elif points_earned >= 6:
                celebration_message = "👍 Good job!"
            else:
                celebration_message = "Keep practicing!"
            
            return TaskCompletionResponseDTO(
                points_earned=points_earned,
                total_points=new_total_points,
                level_up=level_up,
                new_level=new_level if level_up else None,
                points_to_next_level=points_to_next_level,
                achievement_unlocked=achievement_unlocked,
                celebration_message=celebration_message
            )
            
        except Exception as e:
            # Respuesta por defecto
            return TaskCompletionResponseDTO(
                points_earned=int(simulation_score / 10),
                total_points=int(simulation_score / 10),
                level_up=False,
                points_to_next_level=100,
                celebration_message="Simulation completed!"
            )
    
    def _calculate_achievements_count(self, total_points: int, completed_simulations: int) -> int:
        """Calcular número de logros desbloqueados"""
        count = 0
        
        # Logros basados en simulaciones completadas
        if completed_simulations >= 1: count += 1
        if completed_simulations >= 5: count += 1
        if completed_simulations >= 10: count += 1
        if completed_simulations >= 25: count += 1
        
        # Logros basados en puntos
        if total_points >= 100: count += 1
        if total_points >= 500: count += 1
        if total_points >= 1000: count += 1
        
        return count
    
    async def _check_new_achievement(self, user_id: str, simulation_score: float) -> Optional[UserAchievementDTO]:
        """Verificar si se desbloqueó un nuevo logro con esta simulación"""
        try:
            # Por simplicidad, solo verificamos logro de alta puntuación
            if simulation_score >= 95:
                return UserAchievementDTO(
                    achievement_id="perfect_score",
                    title="Perfect Score!",
                    description="Achieved 95+ in a simulation",
                    icon="💎",
                    unlocked_at=datetime.utcnow(),
                    rarity="legendary"
                )
            elif simulation_score >= 85:
                return UserAchievementDTO(
                    achievement_id="excellent_performance",
                    title="Excellent Performance",
                    description="Achieved 85+ in a simulation",
                    icon="⭐",
                    unlocked_at=datetime.utcnow(),
                    rarity="rare"
                )
            
            return None
            
        except Exception:
            return None
