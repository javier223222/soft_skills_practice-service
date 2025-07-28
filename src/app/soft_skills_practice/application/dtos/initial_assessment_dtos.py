from pydantic import BaseModel, validator
from typing import List, Dict, Any, Optional
from datetime import datetime
from ..utils.validation_utils import ValidationMixins, SanitizationUtils

class InitialAssessmentQuestionDTO(BaseModel, ValidationMixins):
    """DTO for initial assessment questions with multiple choice scenarios"""
    question_id: str
    skill_type: str
    skill_name: str
    scenario_text: str
    question_text: str
    options: List[Dict[str, str]]  # [{"id": "A", "text": "Option text"}, ...]
    correct_answer_id: str
    difficulty_level: int
    explanation: str
    
    @validator('scenario_text', 'question_text', 'explanation')
    def validate_text_fields(cls, v):
        if v:
            return SanitizationUtils.sanitize_text_input(v)
        return v

class InitialAssessmentAnswerDTO(BaseModel, ValidationMixins):
    """DTO for user's answer to assessment question"""
    question_id: str
    selected_option_id: str
    time_taken_seconds: Optional[int] = None
    
    @validator('selected_option_id')
    def validate_option_id(cls, v):
        if v and v not in ['A', 'B', 'C', 'D']:
            raise ValueError('Invalid option ID. Must be A, B, C, or D')
        return v

class InitialAssessmentRequestDTO(BaseModel, ValidationMixins):
    """DTO for starting initial assessment"""
    user_id: str
    technical_specialization: str
    seniority_level: str
    preferred_language: str = "english"

class InitialAssessmentSubmissionDTO(BaseModel, ValidationMixins):
    """DTO for submitting all assessment answers"""
    assessment_id: str
    answers: List[InitialAssessmentAnswerDTO]
    total_time_minutes: Optional[int] = None

class SkillAssessmentResultDTO(BaseModel, ValidationMixins):
    """DTO for individual skill assessment result"""
    skill_type: str
    skill_name: str
    questions_answered: int
    correct_answers: int
    accuracy_percentage: float
    proficiency_level: str  # "beginner", "intermediate", "advanced"
    areas_for_improvement: List[str]
    strengths: List[str]
    recommended_scenarios: List[str]

class InitialAssessmentResultDTO(BaseModel, ValidationMixins):
    """DTO for complete initial assessment results"""
    assessment_id: str
    user_id: str
    overall_score: float
    completion_time_minutes: int
    skill_results: List[SkillAssessmentResultDTO]
    weakest_skills: List[str]
    strongest_skills: List[str]
    recommended_learning_path: List[Dict[str, Any]]
    next_steps: List[str]
    completed_at: datetime

class InitialAssessmentResponseDTO(BaseModel, ValidationMixins):
    """DTO for assessment start response"""
    assessment_id: str
    user_id: str
    questions: List[InitialAssessmentQuestionDTO]
    total_questions: int
    estimated_duration_minutes: int
    instructions: str
    started_at: datetime
