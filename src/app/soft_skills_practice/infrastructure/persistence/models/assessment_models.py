from beanie import Document
from pydantic import Field, BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
import uuid
from enum import Enum

class ProficiencyLevel(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate" 
    ADVANCED = "advanced"

class AssessmentStatus(str, Enum):
    STARTED = "started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ABANDONED = "abandoned"

class AssessmentQuestionOption(BaseModel):
    """Individual option for assessment question - This is a Pydantic model, not a Document"""
    option_id: str
    option_text: str
    is_correct: bool = False
    explanation: Optional[str] = None

class AssessmentQuestion(Document):
    """Assessment question with scenario and multiple choice options"""
    question_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    skill_type: str
    skill_name: str
    scenario_text: str
    question_text: str
    options: List[AssessmentQuestionOption]
    correct_answer_id: str
    difficulty_level: int = Field(ge=1, le=5)
    explanation: str
    tags: List[str] = []
    usage_count: int = 0
    success_rate: float = 0.0
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    class Settings:
        collection = "assessment_questions"

class UserAssessmentAnswer(BaseModel):
    """User's answer to an assessment question - Pydantic model"""
    question_id: str
    selected_option_id: str
    is_correct: bool
    time_taken_seconds: Optional[int] = None
    answered_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class SkillAssessmentResult(BaseModel):
    """Results for a specific skill in the assessment - Pydantic model"""
    skill_type: str
    skill_name: str
    questions_answered: int
    correct_answers: int
    accuracy_percentage: float
    proficiency_level: ProficiencyLevel
    areas_for_improvement: List[str] = []
    strengths: List[str] = []
    recommended_scenarios: List[str] = []

class InitialAssessment(Document):
    """Complete initial assessment session"""
    assessment_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    technical_specialization: str
    seniority_level: str
    status: AssessmentStatus = AssessmentStatus.STARTED
    
    # Questions and answers
    questions: List[str] = []  # question_ids
    answers: List[UserAssessmentAnswer] = []
    
    # Results
    overall_score: Optional[float] = None
    completion_time_minutes: Optional[int] = None
    skill_results: List[SkillAssessmentResult] = []
    
    # Analysis
    weakest_skills: List[str] = []
    strongest_skills: List[str] = []
    recommended_learning_path: List[Dict[str, Any]] = []
    next_steps: List[str] = []
    
    # Timestamps
    started_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = None
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    class Settings:
        collection = "initial_assessments"
