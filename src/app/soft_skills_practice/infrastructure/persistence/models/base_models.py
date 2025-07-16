from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from beanie import Document
from enum import Enum

class SimulationStatus(str, Enum):
    STARTED = "started"
    PRE_TEST = "pre_test"
    SIMULATION = "simulation"
    COMPLETED = "completed"
    ABANDONED = "abandoned"

class MessageType(str, Enum):
    PRE_TEST_QUESTION = "pre_test_question"
    SIMULATION_PROMPT = "simulation_prompt"
    USER_RESPONSE = "user_response"
    AI_FEEDBACK = "ai_feedback"
    FINAL_SUMMARY = "final_summary"

class StepType(str, Enum):
    PRE_TEST = "pre_test"
    SIMULATION = "simulation"
    FEEDBACK = "feedback"


class ScoresData(BaseModel):
    pre_test_score: Optional[int] = None
    simulation_steps_scores: List[int] = Field(default_factory=list)
    final_score: Optional[int] = None
    max_possible_score: int = 100
class SessionMetadata(BaseModel):
    difficulty_level: int = 1  
    estimated_duration: int = 15 
    actual_duration: Optional[int] = None
    platform: str = "web" 
    started_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = None


class UserBehaviorTracking(BaseModel):
    session_duration: Optional[int] = None  
    completion_rate: float = 0.0           
    abandonment_point: Optional[int] = None 
    help_requested_count: int = 0           

class PreferenceIndicators(BaseModel):
    preferred_difficulty: Optional[int] = None
    learning_pace: str = "normal"    

class PerformanceTracking(BaseModel):
    improvement_rate: Optional[float] = None    
    consistency_score: Optional[float] = None  
    struggle_areas: List[str] = Field(default_factory=list)
    strength_areas: List[str] = Field(default_factory=list)


class InteractionTracking(BaseModel):
    time_to_respond: Optional[int] = None 
    response_length: int = 0               
    help_requested: bool = False           

class ResponseAnalysis(BaseModel):
    word_count: int = 0
    sentence_count: int = 0
    confidence_level: Optional[int] = None   


class EvaluationData(BaseModel):
    step_score: Optional[int] = None
    criteria_scores: Dict[str, int] = Field(default_factory=dict)
    strengths: List[str] = Field(default_factory=list)
    areas_for_improvement: List[str] = Field(default_factory=list)
    specific_feedback: Optional[str] = None


class StepContent(BaseModel):
    question: Optional[str] = None
    user_response: Optional[str] = None
    ai_feedback: Optional[str] = None
    context: Optional[str] = None


class RecommendationTracking(BaseModel):
    """Tracking específico para generar recomendaciones"""
    skills_practiced: List[str] = Field(default_factory=list) 
    last_skill_practiced: Optional[str] = None
    skill_performance: Dict[str, float] = Field(default_factory=dict) 
    neglected_skills: List[str] = Field(default_factory=list)  
    recommended_next_skills: List[str] = Field(default_factory=list) 
    recommendation_acceptance_rate: float = 0.0  
    last_recommendation_date: Optional[datetime] = None


class UserSkillProgress(BaseModel):
    """Progreso del usuario por skill - esencial para recomendaciones"""
    skill_name: str
    times_practiced: int = 0
    average_score: float = 0.0
    best_score: int = 0
    last_practiced: Optional[datetime] = None
    difficulty_level: int = 1 
    is_neglected: bool = False  
    natural_ability: Optional[int] = None  


class UsagePatterns(BaseModel):
    """Patrones de uso para recomendaciones"""
    favorite_skills: List[str] = Field(default_factory=list)
    avoided_skills: List[str] = Field(default_factory=list)
    typical_session_duration: int = 15  
    consistency_score: float = 0.0 
class SkillIconData(BaseModel):
    """Información de iconos para soft skills"""
    emoji: Optional[str] = None  
    icon_url: Optional[str] = None
    icon_name: Optional[str] = None  
    background_color: Optional[str] = None 
    icon_color: Optional[str] = None 
    category_icon: Optional[str] = None  

class SkillVisualData(BaseModel):
    """Datos visuales para soft skills"""
    primary_color: str = "#757575"  
    secondary_color: Optional[str] = None  
    gradient_start: Optional[str] = None  
    gradient_end: Optional[str] = None  
    icon_data: SkillIconData = Field(default_factory=SkillIconData)
    display_order: int = 0  
    is_featured: bool = False 
    is_new: bool = False  
class SkillMetadata(BaseModel):
    """Metadatos completos de una soft skill"""
    skill_name: str
    display_name: str
    description: str
    category: str
    tags: List[str] = Field(default_factory=list)
    difficulty_levels: List[int] = Field(default=[1, 2, 3, 4, 5])
    estimated_time_per_level: int = 15  # minutos
    visual_data: SkillVisualData = Field(default_factory=SkillVisualData)
    is_active: bool = True  
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
