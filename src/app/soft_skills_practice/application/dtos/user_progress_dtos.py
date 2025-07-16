from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime

class UserSkillProgressDto(BaseModel):
    """DTO para progreso de usuario en una skill específica"""
    skill_name: str
    display_name: str
    category: str
    times_practiced: int = 0
    average_score: float = 0.0
    best_score: int = 0
    current_difficulty_level: int = 1
    last_practiced: Optional[datetime] = None
    is_neglected: bool = False
    natural_ability: Optional[int] = None
    improvement_rate: float = 0.0
    next_recommended_level: int = 1
    completion_percentage: float = 0.0 
    
    total_time_spent: int = 0  
    sessions_completed: int = 0
    sessions_abandoned: int = 0
    help_requests_count: int = 0

class UserSkillSummaryDto(BaseModel):
    """DTO para resumen de progreso por categoría"""
    category: str
    display_name: str
    skills_in_category: int
    skills_practiced: int
    skills_mastered: int  
    skills_neglected: int
    average_score: float
    total_time_spent: int
    completion_percentage: float

class UserOverallProgressDto(BaseModel):
    """DTO para progreso general del usuario"""
    user_id: str
    user_name: Optional[str] = None
    
    
    total_skills_available: int
    total_skills_practiced: int
    total_skills_mastered: int
    total_skills_neglected: int
    overall_completion_percentage: float
    
    
    categories_progress: List[UserSkillSummaryDto]
    
   
    skills_progress: List[UserSkillProgressDto]
    
    
    strongest_skills: List[str] = Field(default_factory=list)
    weakest_skills: List[str] = Field(default_factory=list)
    recommended_next_skills: List[str] = Field(default_factory=list)
    neglected_skills: List[str] = Field(default_factory=list)
    
   
    total_sessions: int = 0
    total_time_spent: int = 0 
    average_session_duration: float = 0.0
    last_activity: Optional[datetime] = None
    consistency_score: float = 0.0  
    

    improvement_trend: str = "stable" 
    learning_pace: str = "normal"  
    engagement_level: str = "medium" 
    
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class UserProgressResponseDto(BaseModel):
    """DTO para respuesta completa de progreso de usuario"""
    success: bool = True
    message: str = "User progress retrieved successfully"
    data: UserOverallProgressDto
    recommendations_count: int = 0
    last_updated: datetime = Field(default_factory=datetime.utcnow)