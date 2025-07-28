from typing import List, Dict, Any
from datetime import datetime, timezone
from ..dtos.initial_assessment_dtos import (
    InitialAssessmentRequestDTO,
    InitialAssessmentResponseDTO,
    InitialAssessmentQuestionDTO
)
from ...infrastructure.persistence.repositories.assessment_repositories import (
    AssessmentQuestionRepository,
    InitialAssessmentRepository
)
from ...infrastructure.persistence.models.assessment_models import (
    InitialAssessment,
    AssessmentStatus
)
from ..utils.validation_utils import ValidationUtils, SanitizationUtils

class StartInitialAssessmentUseCase:
    """Use case for starting an initial soft skills assessment"""
    
    def __init__(
        self,
        assessment_question_repository: AssessmentQuestionRepository,
        initial_assessment_repository: InitialAssessmentRepository
    ):
        self.assessment_question_repository = assessment_question_repository
        self.initial_assessment_repository = initial_assessment_repository
    
    async def execute(self, request: InitialAssessmentRequestDTO) -> InitialAssessmentResponseDTO:
        """Start a new initial assessment for the user"""
        try:
            # Validate user ID
            if not ValidationUtils.validate_user_id(request.user_id):
                raise ValueError("Invalid user ID format")
            
            # Get available soft skills to assess
            available_skills = self._get_available_soft_skills()
            
            # Get random questions for each skill (2-3 questions per skill)
            questions = await self.assessment_question_repository.get_random_questions_by_skills(
                skill_types=available_skills,
                questions_per_skill=2
            )
            
            if not questions:
                raise ValueError("No assessment questions available")
            
            # Create new assessment session
            assessment = InitialAssessment(
                user_id=request.user_id,
                technical_specialization=SanitizationUtils.sanitize_text_input(request.technical_specialization),
                seniority_level=SanitizationUtils.sanitize_text_input(request.seniority_level),
                questions=[q.question_id for q in questions],
                status=AssessmentStatus.STARTED
            )
            
            saved_assessment = await self.initial_assessment_repository.create(assessment)
            
            # Convert questions to DTOs
            question_dtos = []
            for q in questions:
                try:
                    question_dto = InitialAssessmentQuestionDTO(
                        question_id=getattr(q, 'question_id', str(q.id) if hasattr(q, 'id') else ''),
                        skill_type=getattr(q, 'skill_type', ''),
                        skill_name=getattr(q, 'skill_name', ''),
                        scenario_text=getattr(q, 'scenario_text', ''),
                        question_text=getattr(q, 'question_text', ''),
                        options=[
                            {"id": opt.option_id, "text": opt.option_text}
                            for opt in getattr(q, 'options', [])
                        ],
                        correct_answer_id="",  # Don't send correct answer to client
                        difficulty_level=getattr(q, 'difficulty_level', 1),
                        explanation=""  # Don't send explanation until completion
                    )
                    question_dtos.append(question_dto)
                except Exception as e:
                    raise Exception(f"Error converting question to DTO: {e}. Question data: {q}")
            
            if not question_dtos:
                raise ValueError("No valid questions could be converted to DTOs")
            
            return InitialAssessmentResponseDTO(
                assessment_id=saved_assessment.assessment_id,
                user_id=saved_assessment.user_id,
                questions=question_dtos,
                total_questions=len(question_dtos),
                estimated_duration_minutes=len(question_dtos) * 2,  # 2 minutes per question
                instructions=self._get_assessment_instructions(),
                started_at=saved_assessment.started_at
            )
            
        except Exception as e:
            raise Exception(f"Error starting initial assessment: {str(e)}")
    
    def _get_available_soft_skills(self) -> List[str]:
        """Get list of available soft skills for assessment - matching your database skills"""
        return [
            "active_listening",           # Communication
            "public_speaking",           # Communication  
            "written_communication",     # Communication
            "nonverbal_communication",   # Communication
            "team_motivation",           # Leadership
            "decision_making",           # Leadership
            "delegation",                # Leadership
            "conflict_resolution",       # Leadership
            "collaboration",             # Teamwork
            "adaptability",              # Teamwork
            "cultural_awareness",        # Teamwork
            "empathy",                   # Emotional Intelligence
            "self_awareness",            # Emotional Intelligence
            "stress_management",         # Emotional Intelligence
            "critical_thinking",         # Problem Solving
            "creativity",                # Problem Solving
            "analytical_thinking"        # Problem Solving
        ]
    
    def _get_assessment_instructions(self) -> str:
        """Get assessment instructions for the user"""
        return """
Welcome to your Soft Skills Initial Assessment!

INSTRUCTIONS:
• This assessment contains scenario-based questions to evaluate your soft skills
• Each question presents a workplace situation with multiple choice answers
• Choose the option that best represents how you would handle the situation
• There are no right or wrong answers - be honest about your approach
• Take your time to read each scenario carefully
• The assessment takes approximately 15-20 minutes to complete

Your results will help us:
• Identify your strongest soft skills
• Highlight areas for improvement
• Recommend personalized learning scenarios
• Create a customized development path

Ready to begin? Click 'Start Assessment' when you're ready!
""".strip()
