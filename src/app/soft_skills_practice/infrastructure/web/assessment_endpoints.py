"""
Assessment endpoints for initial soft skills evaluation.
These endpoints are new and don't affect existing simulation endpoints.
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
import logging

from ...application.dtos.initial_assessment_dtos import (
    InitialAssessmentRequestDTO,
    InitialAssessmentResponseDTO,
    InitialAssessmentSubmissionDTO,
    InitialAssessmentResultDTO
)
from ...application.use_cases.start_initial_assessment_use_case import StartInitialAssessmentUseCase
from ...application.use_cases.submit_initial_assessment_use_case import SubmitInitialAssessmentUseCase
from ...infrastructure.persistence.repositories.assessment_repositories import (
    AssessmentQuestionRepository,
    InitialAssessmentRepository
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create router for assessment endpoints
assessment_router = APIRouter(
    prefix="/api/v1/assessment",
    tags=["Assessment"],
    responses={
        404: {"description": "Not found"},
        422: {"description": "Validation error"},
        500: {"description": "Internal server error"}
    }
)

# Dependency injection for repositories
async def get_assessment_question_repository() -> AssessmentQuestionRepository:
    """Get assessment question repository instance"""
    return AssessmentQuestionRepository()

async def get_initial_assessment_repository() -> InitialAssessmentRepository:
    """Get initial assessment repository instance"""
    return InitialAssessmentRepository()

async def get_start_assessment_use_case(
    question_repo: AssessmentQuestionRepository = Depends(get_assessment_question_repository),
    assessment_repo: InitialAssessmentRepository = Depends(get_initial_assessment_repository)
) -> StartInitialAssessmentUseCase:
    """Get start assessment use case instance"""
    return StartInitialAssessmentUseCase(question_repo, assessment_repo)

async def get_submit_assessment_use_case(
    question_repo: AssessmentQuestionRepository = Depends(get_assessment_question_repository),
    assessment_repo: InitialAssessmentRepository = Depends(get_initial_assessment_repository)
) -> SubmitInitialAssessmentUseCase:
    """Get submit assessment use case instance"""
    return SubmitInitialAssessmentUseCase(question_repo, assessment_repo)

@assessment_router.post(
    "/start",
    response_model=InitialAssessmentResponseDTO,
    summary="Start Initial Soft Skills Assessment",
    description="""
    Start a new initial assessment to evaluate user's soft skills strengths and areas for improvement.
    
    This endpoint:
    - Creates a new assessment session
    - Generates scenario-based multiple choice questions
    - Covers key soft skills: communication, leadership, teamwork, etc.
    - Returns questions in English for workplace scenarios
    
    The assessment helps identify:
    - Current skill proficiency levels
    - Areas needing improvement
    - Recommended learning paths
    - Personalized scenario suggestions
    """
)
async def start_initial_assessment(
    request: InitialAssessmentRequestDTO,
    use_case: StartInitialAssessmentUseCase = Depends(get_start_assessment_use_case)
) -> InitialAssessmentResponseDTO:
    """
    Start initial soft skills assessment
    
    - **user_id**: Unique identifier for the user
    - **technical_specialization**: User's technical background  
    - **seniority_level**: Professional experience level
    - **preferred_language**: Language preference (default: english)
    
    Returns assessment questions with scenarios and multiple choice options.
    """
    try:
        logger.info(f"Starting initial assessment for user: {request.user_id}")
        
        result = await use_case.execute(request)
        
        logger.info(f"Successfully started assessment {result.assessment_id} with {result.total_questions} questions")
        return result
        
    except ValueError as e:
        logger.error(f"Validation error starting assessment: {e}")
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.error(f"Error starting initial assessment: {e}")
        # Return the actual error for debugging
        raise HTTPException(status_code=500, detail=f"Failed to start assessment: {str(e)}")

@assessment_router.post(
    "/submit",
    response_model=InitialAssessmentResultDTO,
    summary="Submit Initial Assessment Answers",
    description="""
    Submit completed assessment answers and receive detailed results.
    
    This endpoint:
    - Evaluates user responses against correct answers
    - Calculates skill-specific scores and overall performance
    - Identifies strongest and weakest soft skills
    - Generates personalized learning recommendations
    - Provides detailed feedback and next steps
    
    Results include:
    - Individual skill assessments with proficiency levels
    - Areas for improvement and strengths for each skill
    - Recommended scenarios for practice
    - Personalized learning path suggestions
    """
)
async def submit_initial_assessment(
    submission: InitialAssessmentSubmissionDTO,
    use_case: SubmitInitialAssessmentUseCase = Depends(get_submit_assessment_use_case)
) -> InitialAssessmentResultDTO:
    """
    Submit assessment answers and get results
    
    - **assessment_id**: ID of the assessment session
    - **answers**: List of user's selected answers
    - **total_time_minutes**: Time taken to complete assessment
    
    Returns comprehensive results with skill analysis and recommendations.
    """
    try:
        logger.info(f"Processing assessment submission: {submission.assessment_id}")
        
        result = await use_case.execute(submission)
        
        logger.info(f"Successfully processed assessment {submission.assessment_id}, overall score: {result.overall_score}")
        return result
        
    except ValueError as e:
        logger.error(f"Validation error submitting assessment: {e}")
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.error(f"Error submitting assessment: {e}")
        raise HTTPException(status_code=500, detail="Failed to process assessment submission")

@assessment_router.get(
    "/user/{user_id}/latest",
    response_model=Optional[InitialAssessmentResultDTO],
    summary="Get User's Latest Assessment Results",
    description="""
    Retrieve the most recent assessment results for a user.
    
    Useful for:
    - Displaying previous assessment results
    - Tracking skill development progress
    - Showing current proficiency levels
    - Accessing personalized recommendations
    
    Returns null if user has no completed assessments.
    """
)
async def get_latest_assessment_results(
    user_id: str,
    assessment_repo: InitialAssessmentRepository = Depends(get_initial_assessment_repository)
) -> Optional[InitialAssessmentResultDTO]:
    """
    Get user's latest completed assessment results
    
    - **user_id**: User's unique identifier
    
    Returns the most recent assessment results or null if none exist.
    """
    try:
        logger.info(f"Fetching latest assessment for user: {user_id}")
        
        assessment = await assessment_repo.find_latest_by_user_id(user_id)
        
        if not assessment or assessment.status != "completed":
            logger.info(f"No completed assessment found for user: {user_id}")
            return None
        
        # Convert to result DTO
        from ...application.dtos.initial_assessment_dtos import SkillAssessmentResultDTO
        
        result = InitialAssessmentResultDTO(
            assessment_id=assessment.assessment_id,
            user_id=assessment.user_id,
            overall_score=assessment.overall_score or 0.0,
            completion_time_minutes=assessment.completion_time_minutes or 0,
            skill_results=[
                SkillAssessmentResultDTO(
                    skill_type=sr.skill_type,
                    skill_name=sr.skill_name,
                    questions_answered=sr.questions_answered,
                    correct_answers=sr.correct_answers,
                    accuracy_percentage=sr.accuracy_percentage,
                    proficiency_level=sr.proficiency_level.value,
                    areas_for_improvement=sr.areas_for_improvement,
                    strengths=sr.strengths,
                    recommended_scenarios=sr.recommended_scenarios
                )
                for sr in assessment.skill_results
            ],
            weakest_skills=assessment.weakest_skills,
            strongest_skills=assessment.strongest_skills,
            recommended_learning_path=assessment.recommended_learning_path,
            next_steps=assessment.next_steps,
            completed_at=assessment.completed_at
        )
        
        logger.info(f"Successfully retrieved assessment results for user: {user_id}")
        return result
        
    except Exception as e:
        logger.error(f"Error fetching latest assessment: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve assessment results")

@assessment_router.get(
    "/health",
    summary="Assessment Service Health Check",
    description="Check if the assessment service is running and database is accessible"
)
async def assessment_health_check():
    """Health check for assessment endpoints"""
    try:
        # Test database connectivity
        repo = AssessmentQuestionRepository()
        # This is a simple test - you might want to add more comprehensive checks
        
        return {
            "status": "healthy",
            "service": "assessment",
            "timestamp": "2025-07-28T12:00:00Z",
            "message": "Assessment service is running normally"
        }
    except Exception as e:
        logger.error(f"Assessment health check failed: {e}")
        raise HTTPException(status_code=503, detail="Assessment service unavailable")
