from typing import Dict, Any, List
from pydantic import BaseModel, validator
from datetime import datetime
from ..utils.validation_utils import ValidationMixins, SanitizationUtils

class UserLevelDTO(BaseModel, ValidationMixins):
    """DTO para información de nivel del usuario"""
    user_id: str
    current_level: int
    current_points: int
    points_to_next_level: int
    total_points_earned: int
    level_progress_percentage: float
    achievements_unlocked: int
    simulations_completed: int

class UserAchievementDTO(BaseModel, ValidationMixins):
    """DTO para logros del usuario"""
    achievement_id: str
    title: str
    description: str
    icon: str
    unlocked_at: datetime
    rarity: str 
    
    @validator('title', 'description')
    def validate_text_fields(cls, v):
        if v:
            return SanitizationUtils.sanitize_text_input(v)
        return v

class UserStatsDTO(BaseModel, ValidationMixins):
    """DTO para estadísticas del usuario"""
    user_id: str
    level_info: UserLevelDTO
    recent_achievements: List[UserAchievementDTO]
    favorite_skills: List[str]
    completion_streak: int
    average_score: float

class TaskCompletionResponseDTO(BaseModel, ValidationMixins):
    """DTO para respuesta de finalización de tarea móvil"""
    points_earned: int
    total_points: int
    level_up: bool
    new_level: int = None
    points_to_next_level: int
    achievement_unlocked: UserAchievementDTO = None
    celebration_message: str
    
    @validator('celebration_message')
    def validate_celebration_message(cls, v):
        if v:
            return SanitizationUtils.sanitize_text_input(v)
        return v
