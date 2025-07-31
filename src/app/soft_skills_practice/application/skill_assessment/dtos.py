"""
DTOs para el bounded context Skill Assessment
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class AssessmentQuestionDTO(BaseModel):
    """DTO para preguntas de evaluación"""
    question_id: str
    skill_type: str
    skill_name: str
    question_text: str
    scenario_context: str
    options: Dict[str, str]  # {option_id: option_text}
    difficulty_level: int
    tags: List[str]
    estimated_time_seconds: int = 60


class UserAnswerDTO(BaseModel):
    """DTO para respuestas de usuario"""
    question_id: str
    selected_option_id: str
    time_taken_seconds: int
    is_correct: bool
    answered_at: datetime


class SkillResultDTO(BaseModel):
    """DTO para resultados de habilidad"""
    skill_type: str
    skill_name: str
    questions_answered: int
    correct_answers: int
    accuracy_percentage: float
    proficiency_level: str  # beginner, intermediate, advanced, expert
    strengths: List[str]
    areas_for_improvement: List[str]
    recommended_scenarios: List[str]


class AssessmentProgressDTO(BaseModel):
    """DTO para progreso de evaluación"""
    assessment_id: str
    user_id: str
    total_questions: int
    answered_questions: int
    progress_percentage: float
    estimated_remaining_time_minutes: int
    current_skill_type: Optional[str] = None
    next_question: Optional[AssessmentQuestionDTO] = None


class AssessmentResultDTO(BaseModel):
    """DTO para resultados completos de evaluación"""
    assessment_id: str
    user_id: str
    overall_score: float
    completion_time_minutes: int
    skill_results: List[SkillResultDTO]
    weakest_skills: List[str]
    strongest_skills: List[str]
    recommended_learning_path: List[Dict[str, Any]]
    next_steps: List[str]
    completed_at: datetime
    performance_tier: str  # exceptional, above_average, average, below_average, needs_improvement


class AssessmentSummaryDTO(BaseModel):
    """DTO para resumen de evaluación"""
    assessment_id: str
    user_id: str
    status: str  # not_started, in_progress, completed, expired
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    total_questions: int
    answered_questions: int
    skill_types: List[str]


class StartAssessmentResponseDTO(BaseModel):
    """DTO para respuesta de inicio de evaluación"""
    assessment_id: str
    user_id: str
    total_questions: int
    questions_per_skill: int
    skill_types: List[str]
    estimated_duration_minutes: int
    first_question: AssessmentQuestionDTO
    instructions: str = "Answer all questions honestly. There are no right or wrong answers in the context of your experience."


class SubmitAnswerResponseDTO(BaseModel):
    """DTO para respuesta de envío de respuesta"""
    question_id: str
    is_correct: bool
    feedback: Optional[str] = None  # Solo para evaluaciones completadas
    next_question: Optional[AssessmentQuestionDTO] = None
    progress: AssessmentProgressDTO
    is_assessment_complete: bool = False


class AssessmentAnalyticsDTO(BaseModel):
    """DTO para analíticas de evaluación"""
    user_id: Optional[str] = None
    total_assessments: int
    completed_assessments: int
    average_score: float
    score_trend: List[float]  # Últimos scores para mostrar tendencia
    skill_performance: Dict[str, float]  # skill_type -> average_score
    time_spent_distribution: Dict[str, int]  # time_range -> count
    improvement_rate: float  # Porcentaje de mejora
    benchmark_comparison: Dict[str, Any]


class SkillProgressionDTO(BaseModel):
    """DTO para progresión de habilidades"""
    user_id: str
    skill_type: str
    progression_data: List[Dict[str, Any]]  # Datos históricos de progreso
    current_level: str
    previous_level: str
    improvement_percentage: float
    assessment_count: int
    latest_score: float
    best_score: float
    trend: str  # improving, stable, declining


class ComparisonAnalysisDTO(BaseModel):
    """DTO para análisis comparativo"""
    user_id: str
    user_score: float
    comparison_group_average: float
    percentile_ranking: int
    performance_tier: str
    skills_above_average: List[str]
    skills_below_average: List[str]
    recommended_focus_areas: List[str]
    peer_group_size: int


class LearningRecommendationDTO(BaseModel):
    """DTO para recomendaciones de aprendizaje"""
    user_id: str
    based_on_assessment_id: str
    priority_skills: List[str]
    recommended_scenarios: List[Dict[str, Any]]
    learning_path: List[Dict[str, Any]]
    estimated_improvement_timeline: str
    success_probability: float
    custom_recommendations: List[str]


class AssessmentReportDTO(BaseModel):
    """DTO para reporte completo de evaluación"""
    assessment_result: AssessmentResultDTO
    analytics: AssessmentAnalyticsDTO
    skill_progression: List[SkillProgressionDTO]
    comparison_analysis: ComparisonAnalysisDTO
    learning_recommendations: LearningRecommendationDTO
    generated_at: datetime
    report_version: str = "1.0"


class QuestionStatisticsDTO(BaseModel):
    """DTO para estadísticas de preguntas"""
    question_id: str
    skill_type: str
    difficulty_level: int
    usage_count: int
    success_rate: float
    average_time_seconds: float
    discrimination_index: float  # Qué tan bien discrimina entre usuarios de alto y bajo rendimiento
    tags: List[str]


class AssessmentMetricsDTO(BaseModel):
    """DTO para métricas globales de evaluaciones"""
    total_assessments_completed: int
    average_completion_time_minutes: float
    global_average_score: float
    skill_performance_ranking: List[Dict[str, Any]]  # Rankings por habilidad
    question_effectiveness: List[QuestionStatisticsDTO]
    user_engagement_metrics: Dict[str, Any]
    assessment_completion_rate: float


# DTOs de Error específicos para Assessment

class AssessmentErrorDTO(BaseModel):
    """DTO base para errores de evaluación"""
    error_code: str
    message: str
    details: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ValidationErrorDTO(AssessmentErrorDTO):
    """DTO para errores de validación"""
    field_errors: Dict[str, List[str]] = Field(default_factory=dict)


class BusinessRuleErrorDTO(AssessmentErrorDTO):
    """DTO para errores de reglas de negocio"""
    rule_name: str
    rule_description: str
