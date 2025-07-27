from pydantic import BaseModel, validator
from typing import Optional, Dict, Any, List

from datetime import datetime
from ..utils.validation_utils import ValidationMixins, SanitizationUtils, ValidationUtils

class StartSimulationRequestBaseModel(BaseModel, ValidationMixins):
    user_id: str
    tecnical_specialization: str 
    seniority_level: str
    difficulty_preference: Optional[int] = None
    
    @validator('tecnical_specialization')
    def validate_technical_specialization(cls, v):
        if v:
            sanitized = SanitizationUtils.sanitize_text_input(v)
            if len(sanitized.strip()) < 3:
                raise ValueError('Technical specialization must be at least 3 characters')
            return sanitized[:100]  # Limit length
        return v
    
    @validator('seniority_level')
    def validate_seniority_level(cls, v):
        if v:
            sanitized = SanitizationUtils.sanitize_text_input(v)
            allowed_levels = {'junior', 'mid', 'senior', 'lead', 'principal', 'architect'}
            if sanitized.lower() not in allowed_levels:
                # Don't raise error to maintain compatibility, just sanitize
                pass
            return sanitized[:50]  # Limit length
        return v

class StartSimulationRequestBySoftSkillDTO(StartSimulationRequestBaseModel):
    skill_type: str  

class StartSimulationRequestDTO(StartSimulationRequestBaseModel):
    scenario_id: str
    
    @validator('scenario_id')
    def validate_scenario_id(cls, v):
        if v and not ValidationUtils.validate_session_id(v):
            # Don't raise error to maintain compatibility, just sanitize
            return SanitizationUtils.sanitize_alphanumeric(v)
        return v

class RespondSimulationRequestDTO(BaseModel, ValidationMixins):
    user_response: str
    response_time_seconds: Optional[int] = None
    help_requested: bool = False
    
    @validator('response_time_seconds')
    def validate_response_time(cls, v):
        if v is not None and (v < 0 or v > 3600):  # Max 1 hour
            return None  # Reset to None if invalid, don't break the flow
        return v


class SimulationResponseDTO(BaseModel, ValidationMixins):
    session_id: str
    step_number: int
    user_response: str
    ai_feedback: Optional[str] = None
    evaluation: Optional[Dict[str, Any]] = None
    next_step: Optional[Dict[str, Any]] = None
    is_completed: bool = False
    message: str
    
    @validator('ai_feedback')
    def validate_ai_feedback(cls, v):
        if v:
            # Sanitize AI feedback to ensure it's safe
            return SanitizationUtils.sanitize_text_input(v)
        return v
    
    @validator('message')
    def validate_message(cls, v):
        if v:
            return SanitizationUtils.sanitize_text_input(v)
        return v


class SimulationStepDTO(BaseModel):
    
    step_id: str
    step_number: int
    step_type: str  
    message_type: str  
    content: Dict[str, Any]
    created_at: datetime


class SimulationSessionDTO(BaseModel):
    
    session_id: str
    user_id: str
    scenario_id: str
    skill_type: str
    status: str  
    current_step: int
    total_steps: int
    started_at: datetime
    difficulty_level: int
    

class PerformanceMetricsDTO(BaseModel):
    
    overall_score: float
    average_step_score: float
    total_time_minutes: int
    average_response_time_seconds: float
    help_requests_count: int
    completion_percentage: float
    confidence_level: str 


class SkillAssessmentDTO(BaseModel):
   
    skill_name: str
    score: float  
    level: str 
    strengths: List[str]
    areas_for_improvement: List[str]
    specific_feedback: str


class CompletionFeedbackDTO(BaseModel, ValidationMixins):
    session_id: str
    user_id: str
    scenario_title: str
    skill_type: str
    completion_status: str  
    performance: PerformanceMetricsDTO
    skill_assessments: List[SkillAssessmentDTO]
    overall_feedback: str
    key_achievements: List[str]
    main_learnings: List[str]
    next_steps_recommendations: List[str]
    percentile_ranking: Optional[int] = None 
    completed_at: datetime
    certificate_earned: bool = False
    badge_unlocked: Optional[str] = None
    notification_status: Optional[Dict[str, Any]] = None  
    certificate_earned: bool = False
    badge_unlocked: Optional[str] = None
    
    @validator('overall_feedback')
    def validate_overall_feedback(cls, v):
        if v:
            return SanitizationUtils.sanitize_text_input(v)
        return v
    
    @validator('scenario_title')
    def validate_scenario_title(cls, v):
        if v:
            return SanitizationUtils.sanitize_text_input(v)
        return v


class StartSimulationResponseDTO(BaseModel):
    """DTO para la respuesta de iniciar simulación - coherente con vistas móviles"""
    session_id: str
    user_id: str
    scenario_id: str
    scenario: Dict[str, Any]
    initial_situation: str  
    first_test: Dict[str, Any]  
    session_info: SimulationSessionDTO
    message: str
    
    estimated_duration_minutes: int = 15
    skill_focus: List[str] = []  
    scenario_metadata: Dict[str, Any] = {}


class FirstTestDTO(BaseModel):
    """DTO para el primer test/pregunta"""
    test_content: str
    test_type: str 
    response_options: Optional[List[Dict[str, str]]] = None  
    instructions: str
    expected_response_time_seconds: int = 120
    

class InitialTestDTO(BaseModel):
    """DTO para el test inicial"""
    test_id: str
    question: str
    context: str
    expected_skills: List[str]
    instructions: str


class SimulationCompletedResponseDTO(BaseModel):
    """DTO para respuesta cuando la simulación se completa"""
    session_id: str
    is_completed: bool
    completion_feedback: CompletionFeedbackDTO
    message: str


class SimulationStatusDTO(BaseModel):
    """DTO para estado de simulación - coherente con vistas móviles"""
    session_id: str
    current_step_number: int
    total_steps_completed: int
    total_steps_planned: int = 3  
    
   
    session_metadata: Dict[str, Any] = {}
    
    
    scores: Dict[str, Any] = {}
    
    
    status: str 
    is_completed: bool = False
    
    
    scenario_info: Dict[str, Any] = {}
    
    
    completed_steps: List[Dict[str, Any]] = []
    
    
    progress_analytics: Dict[str, Any] = {}
