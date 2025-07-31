"""
Commands para el bounded context Skill Assessment
"""
from typing import List, Optional
from pydantic import BaseModel, validator
from datetime import datetime

from ...domain.shared.value_objects import UserId, SkillType, TechnicalSpecialization, SeniorityLevel
from ...domain.skill_assessment.entities import AssessmentId, AssessmentQuestionId, OptionId


class StartAssessmentCommand(BaseModel):
    """Command para iniciar una evaluación"""
    user_id: str
    technical_specialization: str
    seniority_level: str
    preferred_language: str = "english"
    skill_types: Optional[List[str]] = None  # Si no se especifica, usa todas las habilidades
    questions_per_skill: int = 2
    
    @validator('user_id')
    def validate_user_id(cls, v):
        if not v or len(v.strip()) < 10:
            raise ValueError("User ID must be at least 10 characters")
        return v.strip()
    
    @validator('questions_per_skill')
    def validate_questions_per_skill(cls, v):
        if v < 1 or v > 5:
            raise ValueError("Questions per skill must be between 1 and 5")
        return v
    
    @validator('skill_types')
    def validate_skill_types(cls, v):
        if v is not None:
            allowed_skills = {
                'communication', 'leadership', 'teamwork', 'problem_solving',
                'time_management', 'emotional_intelligence', 'adaptability',
                'conflict_resolution', 'decision_making', 'critical_thinking',
                'active_listening', 'negotiation', 'stress_management'
            }
            invalid_skills = [skill for skill in v if skill.lower() not in allowed_skills]
            if invalid_skills:
                raise ValueError(f"Invalid skill types: {invalid_skills}")
        return v


class SubmitAnswerCommand(BaseModel):
    """Command para enviar una respuesta"""
    assessment_id: str
    question_id: str
    selected_option_id: str
    time_taken_seconds: int
    
    @validator('time_taken_seconds')
    def validate_time_taken(cls, v):
        if v < 0 or v > 3600:  # Máximo 1 hora por pregunta
            raise ValueError("Time taken must be between 0 and 3600 seconds")
        return v


class CompleteAssessmentCommand(BaseModel):
    """Command para completar una evaluación"""
    assessment_id: str
    answers: List[SubmitAnswerCommand]
    total_time_minutes: int
    
    @validator('total_time_minutes')
    def validate_total_time(cls, v):
        if v < 0 or v > 180:  # Máximo 3 horas total
            raise ValueError("Total time must be between 0 and 180 minutes")
        return v
    
    @validator('answers')
    def validate_answers(cls, v):
        if not v:
            raise ValueError("At least one answer is required")
        return v


class RetakeAssessmentCommand(BaseModel):
    """Command para repetir una evaluación"""
    user_id: str
    previous_assessment_id: str
    focus_skills: Optional[List[str]] = None  # Habilidades específicas para enfocar
    
    @validator('user_id')
    def validate_user_id(cls, v):
        if not v or len(v.strip()) < 10:
            raise ValueError("User ID must be at least 10 characters")
        return v.strip()


class GetAssessmentProgressCommand(BaseModel):
    """Command para obtener progreso de evaluación"""
    assessment_id: str
    user_id: str
    
    @validator('assessment_id')
    def validate_assessment_id(cls, v):
        if not v or len(v.strip()) < 8:
            raise ValueError("Assessment ID must be at least 8 characters")
        return v.strip()


class GetUserAssessmentHistoryCommand(BaseModel):
    """Command para obtener historial de evaluaciones"""
    user_id: str
    limit: int = 10
    include_incomplete: bool = False
    
    @validator('limit')
    def validate_limit(cls, v):
        if v < 1 or v > 100:
            raise ValueError("Limit must be between 1 and 100")
        return v


class GenerateAssessmentReportCommand(BaseModel):
    """Command para generar reporte de evaluación"""
    assessment_id: str
    user_id: str
    include_detailed_analysis: bool = True
    include_benchmark_comparison: bool = True
    report_format: str = "json"
    
    @validator('report_format')
    def validate_report_format(cls, v):
        allowed_formats = ['json', 'pdf', 'html']
        if v.lower() not in allowed_formats:
            raise ValueError(f"Report format must be one of: {allowed_formats}")
        return v.lower()
