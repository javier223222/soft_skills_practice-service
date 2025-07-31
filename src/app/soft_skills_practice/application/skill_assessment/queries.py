"""
Queries para el bounded context Skill Assessment
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, validator
from datetime import datetime, date


class GetAssessmentByIdQuery(BaseModel):
    """Query para obtener evaluación por ID"""
    assessment_id: str
    user_id: str  # Para verificar permisos
    
    @validator('assessment_id')
    def validate_assessment_id(cls, v):
        if not v or len(v.strip()) < 8:
            raise ValueError("Assessment ID must be at least 8 characters")
        return v.strip()


class GetAssessmentQuestionsQuery(BaseModel):
    """Query para obtener preguntas de evaluación"""
    assessment_id: str
    skill_type: Optional[str] = None  # Filtro opcional por habilidad
    include_answers: bool = False  # Solo para evaluaciones completadas
    
    @validator('assessment_id')
    def validate_assessment_id(cls, v):
        if not v or len(v.strip()) < 8:
            raise ValueError("Assessment ID must be at least 8 characters")
        return v.strip()


class GetUserAssessmentResultsQuery(BaseModel):
    """Query para obtener resultados de evaluación de usuario"""
    user_id: str
    assessment_id: Optional[str] = None
    skill_type: Optional[str] = None
    include_detailed_feedback: bool = True
    
    @validator('user_id')
    def validate_user_id(cls, v):
        if not v or len(v.strip()) < 10:
            raise ValueError("User ID must be at least 10 characters")
        return v.strip()


class GetSkillProgressionQuery(BaseModel):
    """Query para obtener progresión de habilidades"""
    user_id: str
    skill_type: Optional[str] = None
    from_date: Optional[date] = None
    to_date: Optional[date] = None
    limit: int = 50
    
    @validator('limit')
    def validate_limit(cls, v):
        if v < 1 or v > 100:
            raise ValueError("Limit must be between 1 and 100")
        return v
    
    @validator('from_date', 'to_date')
    def validate_dates(cls, v, values):
        if v and 'from_date' in values and values['from_date']:
            if v < values['from_date']:
                raise ValueError("To date must be after from date")
        return v


class GetAssessmentAnalyticsQuery(BaseModel):
    """Query para obtener analíticas de evaluaciones"""
    user_id: Optional[str] = None  # Para analíticas específicas de usuario
    skill_type: Optional[str] = None  # Para analíticas específicas de habilidad
    time_period: str = "last_30_days"  # last_7_days, last_30_days, last_90_days, all_time
    include_benchmark: bool = True
    
    @validator('time_period')
    def validate_time_period(cls, v):
        allowed_periods = ['last_7_days', 'last_30_days', 'last_90_days', 'all_time']
        if v not in allowed_periods:
            raise ValueError(f"Time period must be one of: {allowed_periods}")
        return v


class SearchAssessmentQuestionsQuery(BaseModel):
    """Query para buscar preguntas de evaluación"""
    skill_types: Optional[List[str]] = None
    difficulty_range: Optional[tuple] = None  # (min, max)
    search_text: Optional[str] = None
    tags: Optional[List[str]] = None
    limit: int = 20
    offset: int = 0
    sort_by: str = "created_at"  # created_at, difficulty, usage_count, success_rate
    sort_order: str = "desc"  # asc, desc
    
    @validator('limit')
    def validate_limit(cls, v):
        if v < 1 or v > 100:
            raise ValueError("Limit must be between 1 and 100")
        return v
    
    @validator('offset')
    def validate_offset(cls, v):
        if v < 0:
            raise ValueError("Offset must be non-negative")
        return v
    
    @validator('sort_by')
    def validate_sort_by(cls, v):
        allowed_sorts = ['created_at', 'difficulty', 'usage_count', 'success_rate']
        if v not in allowed_sorts:
            raise ValueError(f"Sort by must be one of: {allowed_sorts}")
        return v
    
    @validator('sort_order')
    def validate_sort_order(cls, v):
        if v.lower() not in ['asc', 'desc']:
            raise ValueError("Sort order must be 'asc' or 'desc'")
        return v.lower()


class GetComparisonAnalysisQuery(BaseModel):
    """Query para obtener análisis comparativo"""
    user_id: str
    comparison_type: str = "peer_group"  # peer_group, global_average, skill_specific
    skill_types: Optional[List[str]] = None
    time_frame: str = "last_assessment"  # last_assessment, last_30_days, last_90_days
    include_recommendations: bool = True
    
    @validator('comparison_type')
    def validate_comparison_type(cls, v):
        allowed_types = ['peer_group', 'global_average', 'skill_specific']
        if v not in allowed_types:
            raise ValueError(f"Comparison type must be one of: {allowed_types}")
        return v
    
    @validator('time_frame')
    def validate_time_frame(cls, v):
        allowed_frames = ['last_assessment', 'last_30_days', 'last_90_days']
        if v not in allowed_frames:
            raise ValueError(f"Time frame must be one of: {allowed_frames}")
        return v


class GetLearningRecommendationsQuery(BaseModel):
    """Query para obtener recomendaciones de aprendizaje"""
    user_id: str
    based_on_assessment_id: Optional[str] = None
    focus_areas: Optional[List[str]] = None  # Áreas específicas de enfoque
    max_recommendations: int = 10
    include_scenarios: bool = True
    include_learning_path: bool = True
    difficulty_preference: Optional[str] = None  # beginner, intermediate, advanced
    
    @validator('max_recommendations')
    def validate_max_recommendations(cls, v):
        if v < 1 or v > 20:
            raise ValueError("Max recommendations must be between 1 and 20")
        return v
    
    @validator('difficulty_preference')
    def validate_difficulty_preference(cls, v):
        if v is not None:
            allowed_difficulties = ['beginner', 'intermediate', 'advanced']
            if v.lower() not in allowed_difficulties:
                raise ValueError(f"Difficulty preference must be one of: {allowed_difficulties}")
        return v


class GetAssessmentStatisticsQuery(BaseModel):
    """Query para obtener estadísticas de evaluaciones"""
    scope: str = "global"  # global, user_specific, skill_specific
    user_id: Optional[str] = None
    skill_type: Optional[str] = None
    date_range: Optional[tuple] = None  # (start_date, end_date)
    aggregation_level: str = "daily"  # daily, weekly, monthly
    
    @validator('scope')
    def validate_scope(cls, v):
        allowed_scopes = ['global', 'user_specific', 'skill_specific']
        if v not in allowed_scopes:
            raise ValueError(f"Scope must be one of: {allowed_scopes}")
        return v
    
    @validator('aggregation_level')
    def validate_aggregation_level(cls, v):
        allowed_levels = ['daily', 'weekly', 'monthly']
        if v not in allowed_levels:
            raise ValueError(f"Aggregation level must be one of: {allowed_levels}")
        return v
