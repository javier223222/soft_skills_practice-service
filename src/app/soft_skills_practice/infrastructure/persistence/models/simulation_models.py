from beanie import Document, Indexed
from pydantic import Field
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
import uuid

from .base_models  import (
    SimulationStatus, MessageType, StepType, ScoresData, 
    SessionMetadata, UserBehaviorTracking, PreferenceIndicators,
    PerformanceTracking, InteractionTracking, ResponseAnalysis,
    EvaluationData, StepContent, RecommendationTracking,
    UserSkillProgress, UsagePatterns, 
    SkillMetadata
)

class SimulationSession(Document):
    session_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    skill_type: str
    scenario_id: Optional[str] = None
    scenario_title: Optional[str] = None
    status: SimulationStatus = SimulationStatus.STARTED
    current_step: int = 0
    total_steps: int = 5
    start_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    end_at: Optional[datetime] = None
    
    scores: ScoresData = Field(default_factory=ScoresData)
    
    
    session_metadata: SessionMetadata = Field(default_factory=SessionMetadata)
    
   
    user_behavior_tracking: UserBehaviorTracking = Field(default_factory=UserBehaviorTracking)
    preference_indicators: PreferenceIndicators = Field(default_factory=PreferenceIndicators)
    performance_tracking: PerformanceTracking = Field(default_factory=PerformanceTracking)
    
   
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    class Settings:
        name = "simulation_sessions"
        indexes = [
            [("user_id", 1), ("created_at", -1)],
            [("session_id", 1)],
            [("status", 1)],
        ]

class SimulationStep(Document):
    session_id: str
    step_number: int
    step_type: StepType
    message_type: MessageType
    
   
    content: StepContent = Field(default_factory=StepContent)
    
    
    evaluation: Optional[EvaluationData] = None
    
   
    interaction_tracking: InteractionTracking = Field(default_factory=InteractionTracking)
    response_analysis: Optional[ResponseAnalysis] = None
    
    
    context: Dict[str, Any] = Field(default_factory=dict)
    
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    class Settings:
        name = "simulation_steps"
        indexes = [
            [("session_id", 1), ("step_number", 1)],
            [("session_id", 1), ("created_at", 1)],
        ]

class UserRecommendations(Document):
    """Colección dedicada a tracking de recomendaciones"""
    user_id: str
    
    
    skills_analytics: Dict[str, UserSkillProgress] = Field(default_factory=dict)
    
    
    recommendation_data: RecommendationTracking = Field(default_factory=RecommendationTracking)
    
   
    usage_patterns: UsagePatterns = Field(default_factory=UsagePatterns)
    

    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    class Settings:
        name = "user_recommendations"
        indexes = [
            [("user_id", 1)],
            [("recommendation_data.last_recommendation_date", -1)],
        ]

class Scenario(Document):
    """Modelo para escenarios de simulación con información visual"""
    scenario_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    skill_type: str = Field(index=True)  
    title: str
    description: str
    difficulty_level: int = Field(index=True)
    estimated_duration: int  
    initial_situation: str
    
    
    scenario_icon: Optional[str] = None 
    scenario_image_url: Optional[str] = None 
    scenario_color: Optional[str] = None  
    
   
    skill_metadata: Optional[SkillMetadata] = None
    
    
    steps_configuration: Dict[str, Any] = Field(default_factory=dict)
    evaluation_criteria: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)
    steps: Optional[int] = 5  
    usage_count: int = 0
    is_popular: bool = False
    is_create_by_ai: bool = False  
    average_rating: float = 0.0
    
    
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    class Settings:
        name = "scenarios"
        indexes = [
            "skill_type",
            "difficulty_level",
            "is_popular",
            [("skill_type", 1), ("difficulty_level", 1)]
        ]


class SkillCatalog(Document):
    """Modelo para catálogo de soft skills con información completa"""
    
    skill_name: str = Field(default="", index=True)  
    display_name: str
    description: str
    category: str = Field(default="", index=True)
    tags: List[str] = Field(default_factory=list)
    difficulty_levels: List[int] = Field(default=[1, 2, 3, 4, 5])
    estimated_time_per_level: int = 15
    
    
    primary_color: str = "#757575"
    secondary_color: Optional[str] = None
    gradient_start: Optional[str] = None
    gradient_end: Optional[str] = None
    
    
    emoji: Optional[str] = None
    icon_url: Optional[str] = None
    icon_name: Optional[str] = None
    background_color: Optional[str] = None
    icon_color: Optional[str] = None
    
    
    display_order: int = 0
    is_featured: bool = False 
    is_new: bool = False
    is_active: bool = True  
    
    
    total_scenarios: int = 0
    popular_scenarios_count: int = 0
    total_users_practiced: int = 0
    average_user_score: float = 0.0
    
    
    difficulty_config: Dict[int, Dict[str, Any]] = Field(default_factory=dict)
    
    
    related_skills: List[str] = Field(default_factory=list)  
    prerequisite_skills: List[str] = Field(default_factory=list)  
    
    
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    class Settings:
        name = "skills_catalog"
        indexes = [
            "skill_name",
            "category",
            "is_active",
            "is_featured",
            [("category", 1), ("display_order", 1)],
            [("is_active", 1), ("is_featured", 1)]
        ]
