from typing import Dict, Any, List
from pydantic import BaseModel
from datetime import datetime


class UserLevelDTO(BaseModel):
    """DTO para información de nivel del usuario"""
    user_id: str
    current_level: int
    current_points: int
    points_to_next_level: int
    total_points_earned: int
    level_progress_percentage: float
    achievements_unlocked: int
    simulations_completed: int


class UserAchievementDTO(BaseModel):
    """DTO para logros del usuario"""
    achievement_id: str
    title: str
    description: str
    icon: str
    unlocked_at: datetime
    rarity: str  # "common", "rare", "epic", "legendary"


class UserStatsDTO(BaseModel):
    """DTO para estadísticas del usuario"""
    user_id: str
    level_info: UserLevelDTO
    recent_achievements: List[UserAchievementDTO]
    favorite_skills: List[str]
    completion_streak: int
    average_score: float


class TaskCompletionResponseDTO(BaseModel):
    """DTO para respuesta de finalización de tarea móvil"""
    points_earned: int
    total_points: int
    level_up: bool
    new_level: int = None
    points_to_next_level: int
    achievement_unlocked: UserAchievementDTO = None
    celebration_message: str
