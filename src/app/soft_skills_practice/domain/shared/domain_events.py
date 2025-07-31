"""
Domain Events para comunicación entre bounded contexts
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List
from datetime import datetime
from pydantic import BaseModel, Field
from ..value_objects import UserId, SessionId, SkillType, Score


class DomainEvent(BaseModel, ABC):
    """Base class para todos los eventos de dominio"""
    event_id: str = Field(default_factory=lambda: str(__import__('uuid').uuid4()))
    occurred_at: datetime = Field(default_factory=datetime.utcnow)
    event_type: str
    aggregate_id: str
    user_id: str
    
    class Config:
        frozen = True


# ============= SKILL ASSESSMENT EVENTS =============

class AssessmentStartedEvent(DomainEvent):
    """Evento cuando se inicia una evaluación"""
    event_type: str = "assessment.started"
    assessment_id: str
    skill_types: List[str]
    total_questions: int


class AssessmentCompletedEvent(DomainEvent):
    """Evento cuando se completa una evaluación"""
    event_type: str = "assessment.completed"
    assessment_id: str
    overall_score: float
    skill_results: Dict[str, Any]
    proficiency_levels: Dict[str, str]
    completion_time_minutes: int


class SkillLevelDeterminedEvent(DomainEvent):
    """Evento cuando se determina el nivel de una habilidad"""
    event_type: str = "skill.level_determined"
    skill_type: str
    proficiency_level: str
    accuracy_percentage: float
    recommended_scenarios: List[str]


# ============= SIMULATION EVENTS =============

class SimulationStartedEvent(DomainEvent):
    """Evento cuando se inicia una simulación"""
    event_type: str = "simulation.started"
    session_id: str
    scenario_id: str
    skill_type: str
    difficulty_level: int


class SimulationStepCompletedEvent(DomainEvent):
    """Evento cuando se completa un paso de simulación"""
    event_type: str = "simulation.step_completed"
    session_id: str
    step_number: int
    step_score: float
    ai_feedback: str
    user_response_quality: str


class SimulationCompletedEvent(DomainEvent):
    """Evento cuando se completa una simulación"""
    event_type: str = "simulation.completed"
    session_id: str
    final_score: float
    skill_assessments: List[Dict[str, Any]]
    completion_time_minutes: int
    achievements_unlocked: List[str]


class SimulationAbandonedEvent(DomainEvent):
    """Evento cuando se abandona una simulación"""
    event_type: str = "simulation.abandoned"
    session_id: str
    progress_percentage: float
    time_spent_minutes: int
    abandon_reason: str


# ============= LEARNING PATH EVENTS =============

class LearningPathGeneratedEvent(DomainEvent):
    """Evento cuando se genera una ruta de aprendizaje"""
    event_type: str = "learning_path.generated"
    path_id: str
    recommended_skills: List[str]
    priority_skills: List[str]
    estimated_duration_weeks: int


class SkillProgressUpdatedEvent(DomainEvent):
    """Evento cuando se actualiza el progreso en una habilidad"""
    event_type: str = "skill.progress_updated"
    skill_type: str
    previous_level: str
    current_level: str
    progress_percentage: float
    sessions_completed: int


class MilestoneAchievedEvent(DomainEvent):
    """Evento cuando se alcanza un hito"""
    event_type: str = "milestone.achieved"
    milestone_type: str
    milestone_name: str
    points_earned: int
    badge_unlocked: str


# ============= USER PROGRESS EVENTS =============

class UserSkillImprovedEvent(DomainEvent):
    """Evento cuando un usuario mejora en una habilidad"""
    event_type: str = "user.skill_improved"
    skill_type: str
    improvement_percentage: float
    previous_score: float
    current_score: float
    sessions_count: int


class UserEngagementEvent(DomainEvent):
    """Evento de engagement del usuario"""
    event_type: str = "user.engagement"
    activity_type: str  # 'login', 'session_start', 'session_complete'
    duration_minutes: int
    interaction_quality: str  # 'high', 'medium', 'low'


class AchievementUnlockedEvent(DomainEvent):
    """Evento cuando se desbloquea un logro"""
    event_type: str = "achievement.unlocked"
    achievement_id: str
    achievement_type: str
    points_awarded: int
    rarity_level: str  # 'common', 'rare', 'epic', 'legendary'


# ============= CONTENT MANAGEMENT EVENTS =============

class ScenarioGeneratedEvent(DomainEvent):
    """Evento cuando se genera un nuevo escenario"""
    event_type: str = "scenario.generated"
    scenario_id: str
    skill_type: str
    difficulty_level: int
    generation_method: str  # 'ai', 'manual', 'template'


class ContentRecommendationEvent(DomainEvent):
    """Evento de recomendación de contenido"""
    event_type: str = "content.recommended"
    recommendation_type: str
    recommended_scenarios: List[str]
    recommendation_reason: str
    confidence_score: float


# ============= EVENT PUBLISHER INTERFACE =============

class DomainEventPublisher(ABC):
    """Interface para publicar eventos de dominio"""
    
    @abstractmethod
    async def publish(self, event: DomainEvent) -> None:
        """Publica un evento de dominio"""
        pass
    
    @abstractmethod
    async def publish_multiple(self, events: List[DomainEvent]) -> None:
        """Publica múltiples eventos de dominio"""
        pass


# ============= EVENT HANDLER INTERFACE =============

class DomainEventHandler(ABC):
    """Interface para manejar eventos de dominio"""
    
    @abstractmethod
    def can_handle(self, event: DomainEvent) -> bool:
        """Determina si puede manejar el evento"""
        pass
    
    @abstractmethod
    async def handle(self, event: DomainEvent) -> None:
        """Maneja el evento de dominio"""
        pass
