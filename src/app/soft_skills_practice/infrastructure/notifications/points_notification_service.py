"""
Servicio para notificaciones de puntos y actualizaciones de perfil
Maneja la lógica de negocio para enviar notificaciones cuando se completan simulaciones
"""

from typing import Dict, Any, Optional
from datetime import datetime
import logging
from ..messaging.message_queue_service import message_queue_service
from ...application.dtos.simulation_dtos import CompletionFeedbackDTO
from ...application.services.user_mobile_service import UserMobileService

logger = logging.getLogger(__name__)

class PointsNotificationService:
    """Servicio para enviar notificaciones de puntos al microservicio de perfil"""
    
    def __init__(self, user_mobile_service: UserMobileService):
        self.user_mobile_service = user_mobile_service
        self.message_queue = message_queue_service
    
    async def notify_simulation_completed(
        self,
        user_id: str,
        completion_feedback: CompletionFeedbackDTO,
        session_id: str
    ) -> Dict[str, bool]:
        """
        Notificar al microservicio de perfil sobre la completación de una simulación
        
        Args:
            user_id: ID del usuario
            completion_feedback: Feedback de completación de la simulación
            session_id: ID de la sesión
            
        Returns:
            Dict con el estado de cada notificación enviada
        """
        try:
            # Calcular puntos ganados basado en el score
            points_earned = self._calculate_points_from_score(
                completion_feedback.performance.overall_score
            )
            
            # Obtener información del nivel anterior
            previous_level_info = await self.user_mobile_service.get_user_level_info(user_id)
            previous_level = previous_level_info.current_level
            previous_total_points = previous_level_info.total_points_earned
            
            # Preparar datos de la simulación
            simulation_data = {
                "session_id": session_id,
                "skill_type": completion_feedback.skill_type,
                "scenario_title": completion_feedback.scenario_title,
                "final_score": completion_feedback.performance.overall_score,
                "completion_percentage": completion_feedback.performance.completion_percentage,
                "time_spent_minutes": completion_feedback.performance.total_time_minutes,
                "difficulty_level": 3,  # Por defecto, podríamos obtener esto del escenario
                "skill_assessments": [
                    {
                        "skill_name": assessment.skill_name,
                        "score": assessment.score,
                        "level": assessment.level
                    }
                    for assessment in completion_feedback.skill_assessments
                ]
            }
            
            results = {}
            
            # 1. Enviar notificación de puntos ganados
            points_sent = await self.message_queue.publish_points_update(
                user_id=user_id,
                points_earned=points_earned,
                simulation_data=simulation_data
            )
            results["points_notification"] = points_sent
            
            # 2. Calcular nuevo nivel después de agregar puntos
            new_total_points = previous_total_points + points_earned
            new_level = max(1, new_total_points // 100 + 1)
            
            # 3. Verificar si hubo level up
            if new_level > previous_level:
                level_up_data = {
                    "previous_level": previous_level,
                    "new_level": new_level,
                    "total_points": new_total_points,
                    "points_in_new_level": new_total_points % 100
                }
                
                level_up_sent = await self.message_queue.publish_level_up(
                    user_id=user_id,
                    level_data=level_up_data
                )
                results["level_up_notification"] = level_up_sent
            
            # 4. Verificar si se desbloqueó algún logro
            achievement_unlocked = await self._check_and_notify_achievements(
                user_id=user_id,
                completion_feedback=completion_feedback,
                new_total_points=new_total_points,
                new_level=new_level
            )
            results["achievement_notification"] = achievement_unlocked
            
            # 5. Enviar actualización de progreso de skill
            skill_progress_sent = await self._notify_skill_progress_update(
                user_id=user_id,
                completion_feedback=completion_feedback
            )
            results["skill_progress_notification"] = skill_progress_sent
            
            logger.info(f"🎯 Notificaciones enviadas para {user_id}: {results}")
            return results
            
        except Exception as e:
            logger.error(f"❌ Error enviando notificaciones para {user_id}: {e}")
            return {"error": True, "message": str(e)}
    
    def _calculate_points_from_score(self, overall_score: float) -> int:
        """
        Calcular puntos ganados basado en la puntuación de la simulación
        
        Args:
            overall_score: Puntuación general (0-100)
            
        Returns:
            Puntos ganados (0-10)
        """
        # Convertir score de 0-100 a puntos de 0-10
        base_points = int(overall_score / 10)
        
        # Bonificaciones por excelencia
        if overall_score >= 95:
            return base_points + 2  # Bonus por excelencia
        elif overall_score >= 85:
            return base_points + 1  # Bonus por buen desempeño
        else:
            return max(1, base_points)  # Mínimo 1 punto por participar
    
    async def _check_and_notify_achievements(
        self,
        user_id: str,
        completion_feedback: CompletionFeedbackDTO,
        new_total_points: int,
        new_level: int
    ) -> bool:
        """Verificar y notificar logros desbloqueados"""
        try:
            achievements_unlocked = []
            
            # Logro por primera simulación
            if new_total_points >= 1 and new_total_points <= 10:
                achievements_unlocked.append({
                    "achievement_id": "first_simulation",
                    "title": "Primera Simulación",
                    "description": "Completaste tu primera simulación de soft skills",
                    "icon": "🎯",
                    "rarity": "common",
                    "points_value": 5
                })
            
            # Logro por puntuación alta
            if completion_feedback.performance.overall_score >= 90:
                achievements_unlocked.append({
                    "achievement_id": "high_scorer",
                    "title": "Alto Desempeño",
                    "description": "Obtuviste una puntuación de 90+ en una simulación",
                    "icon": "⭐",
                    "rarity": "rare",
                    "points_value": 10
                })
            
            # Logro por puntuación perfecta
            if completion_feedback.performance.overall_score >= 95:
                achievements_unlocked.append({
                    "achievement_id": "perfectionist",
                    "title": "Perfeccionista",
                    "description": "Obtuviste una puntuación de 95+ en una simulación",
                    "icon": "💎",
                    "rarity": "epic",
                    "points_value": 20
                })
            
            # Logro por llegar a nivel 5
            if new_level == 5:
                achievements_unlocked.append({
                    "achievement_id": "level_5_master",
                    "title": "Maestro Nivel 5",
                    "description": "Alcanzaste el nivel 5 en soft skills",
                    "icon": "🏆",
                    "rarity": "epic",
                    "points_value": 25
                })
            
            # Enviar notificaciones de logros
            all_sent = True
            for achievement in achievements_unlocked:
                sent = await self.message_queue.publish_achievement_unlock(
                    user_id=user_id,
                    achievement_data=achievement
                )
                if not sent:
                    all_sent = False
            
            return all_sent
            
        except Exception as e:
            logger.error(f"❌ Error verificando logros para {user_id}: {e}")
            return False
    
    async def _notify_skill_progress_update(
        self,
        user_id: str,
        completion_feedback: CompletionFeedbackDTO
    ) -> bool:
        """Notificar actualización de progreso en habilidad específica"""
        try:
            # Calcular progreso basado en skill assessments
            average_skill_score = sum(
                assessment.score for assessment in completion_feedback.skill_assessments
            ) / len(completion_feedback.skill_assessments) if completion_feedback.skill_assessments else 0
            
            # Extraer áreas de mejora
            improvement_areas = []
            for assessment in completion_feedback.skill_assessments:
                improvement_areas.extend(assessment.areas_for_improvement)
            
            skill_progress_data = {
                "skill_type": completion_feedback.skill_type,
                "skill_name": completion_feedback.skill_type.replace("_", " ").title(),
                "previous_progress": 0,  # Se calcularía basado en historial
                "new_progress": average_skill_score,
                "sessions_completed": 1,  # Incremento por esta sesión
                "average_score": average_skill_score,
                "improvement_areas": list(set(improvement_areas))  # Remover duplicados
            }
            
            return await self.message_queue.publish_skill_progress_update(
                user_id=user_id,
                skill_progress_data=skill_progress_data
            )
            
        except Exception as e:
            logger.error(f"❌ Error notificando progreso de skill para {user_id}: {e}")
            return False
    
    async def notify_manual_points_adjustment(
        self,
        user_id: str,
        points_adjustment: int,
        reason: str,
        admin_user_id: str
    ) -> bool:
        """
        Notificar ajuste manual de puntos (para casos especiales)
        
        Args:
            user_id: ID del usuario
            points_adjustment: Puntos a ajustar (puede ser negativo)
            reason: Razón del ajuste
            admin_user_id: ID del administrador que hace el ajuste
        """
        try:
            simulation_data = {
                "session_id": f"manual_adjustment_{int(datetime.utcnow().timestamp())}",
                "skill_type": "manual_adjustment",
                "scenario_title": "Ajuste Manual de Puntos",
                "final_score": 100 if points_adjustment > 0 else 0,
                "completion_percentage": 100,
                "time_spent_minutes": 0,
                "difficulty_level": 0,
                "adjustment_reason": reason,
                "admin_user_id": admin_user_id
            }
            
            return await self.message_queue.publish_points_update(
                user_id=user_id,
                points_earned=points_adjustment,
                simulation_data=simulation_data
            )
            
        except Exception as e:
            logger.error(f"❌ Error enviando ajuste manual de puntos para {user_id}: {e}")
            return False
