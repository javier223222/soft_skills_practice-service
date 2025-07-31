"""
Controller para el bounded context Skill Assessment usando arquitectura DDD
"""
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.responses import JSONResponse

from ...application.skill_assessment.commands import (
    StartAssessmentCommand, SubmitAnswerCommand, CompleteAssessmentCommand
)
from ...application.skill_assessment.queries import (
    GetAssessmentByIdQuery, GetUserAssessmentResultsQuery
)
from ...application.skill_assessment.handlers import (
    StartAssessmentCommandHandler, SubmitAnswerCommandHandler, 
    CompleteAssessmentCommandHandler
)
from ...application.skill_assessment.dtos import (
    StartAssessmentResponseDTO, SubmitAnswerResponseDTO, AssessmentResultDTO,
    AssessmentErrorDTO, ValidationErrorDTO
)
from ...domain.shared.exceptions import (
    AssessmentException, AssessmentNotStartedException,
    AssessmentAlreadyCompletedException, InvalidAssessmentAnswerException
)
from ...infrastructure.persistence.skill_assessment.mongo_assessment_repository import MongoAssessmentRepository
from ...infrastructure.persistence.skill_assessment.mongo_question_repository import MongoAssessmentQuestionRepository
from ...domain.skill_assessment.domain_services import SkillEvaluationService, AssessmentAnalyticsService
from ...infrastructure.messaging.domain_event_publisher_impl import DomainEventPublisherImpl

# Router para endpoints de evaluación
router = APIRouter(prefix="/api/v1/assessment", tags=["skill_assessment"])


# Dependency injection (en una implementación real, usarías un container DI)
async def get_assessment_repository() -> MongoAssessmentRepository:
    return MongoAssessmentRepository()

async def get_question_repository() -> MongoAssessmentQuestionRepository:
    return MongoAssessmentQuestionRepository()

async def get_skill_evaluation_service(
    question_repo: MongoAssessmentQuestionRepository = Depends(get_question_repository)
) -> SkillEvaluationService:
    return SkillEvaluationService(question_repo)

async def get_analytics_service() -> AssessmentAnalyticsService:
    skill_result_repo = None  # Implementar según sea necesario
    return AssessmentAnalyticsService(skill_result_repo)

async def get_domain_event_publisher() -> DomainEventPublisherImpl:
    return DomainEventPublisherImpl()

async def get_start_assessment_handler(
    assessment_repo: MongoAssessmentRepository = Depends(get_assessment_repository),
    question_repo: MongoAssessmentQuestionRepository = Depends(get_question_repository),
    event_publisher: DomainEventPublisherImpl = Depends(get_domain_event_publisher)
) -> StartAssessmentCommandHandler:
    return StartAssessmentCommandHandler(assessment_repo, question_repo, event_publisher)

async def get_submit_answer_handler(
    assessment_repo: MongoAssessmentRepository = Depends(get_assessment_repository),
    question_repo: MongoAssessmentQuestionRepository = Depends(get_question_repository)
) -> SubmitAnswerCommandHandler:
    return SubmitAnswerCommandHandler(assessment_repo, question_repo)

async def get_complete_assessment_handler(
    assessment_repo: MongoAssessmentRepository = Depends(get_assessment_repository),
    question_repo: MongoAssessmentQuestionRepository = Depends(get_question_repository),
    skill_evaluation_service: SkillEvaluationService = Depends(get_skill_evaluation_service),
    analytics_service: AssessmentAnalyticsService = Depends(get_analytics_service),
    event_publisher: DomainEventPublisherImpl = Depends(get_domain_event_publisher)
) -> CompleteAssessmentCommandHandler:
    return CompleteAssessmentCommandHandler(
        assessment_repo, question_repo, skill_evaluation_service, 
        analytics_service, event_publisher
    )


@router.post("/start", response_model=StartAssessmentResponseDTO, status_code=status.HTTP_201_CREATED)
async def start_assessment(
    command: StartAssessmentCommand,
    handler: StartAssessmentCommandHandler = Depends(get_start_assessment_handler)
):
    """
    🎯 Inicia una nueva evaluación de habilidades blandas
    
    **Parámetros:**
    - **user_id**: ID único del usuario (24-36 caracteres)
    - **technical_specialization**: Especialización técnica del usuario
    - **seniority_level**: Nivel de seniority (junior, mid, senior, lead, principal, architect)
    - **preferred_language**: Idioma preferido (default: english)
    - **skill_types**: Lista de habilidades a evaluar (opcional, usa todas por defecto)
    - **questions_per_skill**: Número de preguntas por habilidad (1-5, default: 2)
    
    **Respuesta:**
    - Información de la evaluación iniciada
    - Primera pregunta para responder
    - Progreso y estimación de tiempo
    """
    try:
        result = await handler.handle(command)
        return result
    
    except AssessmentAlreadyCompletedException as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=AssessmentErrorDTO(
                error_code=e.error_code,
                message=e.message,
                details=e.details
            ).dict()
        )
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=ValidationErrorDTO(
                error_code="VALIDATION_ERROR",
                message=str(e),
                field_errors={"general": [str(e)]}
            ).dict()
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=AssessmentErrorDTO(
                error_code="INTERNAL_ERROR",
                message="Failed to start assessment",
                details={"original_error": str(e)}
            ).dict()
        )


@router.post("/{assessment_id}/submit-answer", response_model=SubmitAnswerResponseDTO)
async def submit_answer(
    assessment_id: str,
    command: SubmitAnswerCommand,
    handler: SubmitAnswerCommandHandler = Depends(get_submit_answer_handler)
):
    """
    📝 Envía una respuesta para una pregunta de evaluación
    
    **Parámetros:**
    - **assessment_id**: ID de la evaluación en progreso
    - **question_id**: ID de la pregunta siendo respondida
    - **selected_option_id**: ID de la opción seleccionada (A, B, C, D)
    - **time_taken_seconds**: Tiempo tomado para responder (0-3600 segundos)
    
    **Respuesta:**
    - Confirmación de respuesta enviada
    - Siguiente pregunta (si está disponible)
    - Progreso actual de la evaluación
    """
    try:
        # Asegurar que el assessment_id del path coincida con el del comando
        command.assessment_id = assessment_id
        
        result = await handler.handle(command)
        return result
    
    except AssessmentNotStartedException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=AssessmentErrorDTO(
                error_code=e.error_code,
                message=e.message,
                details=e.details
            ).dict()
        )
    
    except InvalidAssessmentAnswerException as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=AssessmentErrorDTO(
                error_code=e.error_code,
                message=e.message,
                details=e.details
            ).dict()
        )
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=ValidationErrorDTO(
                error_code="VALIDATION_ERROR",
                message=str(e),
                field_errors={"general": [str(e)]}
            ).dict()
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=AssessmentErrorDTO(
                error_code="INTERNAL_ERROR",
                message="Failed to submit answer",
                details={"original_error": str(e)}
            ).dict()
        )


@router.post("/{assessment_id}/complete", response_model=AssessmentResultDTO)
async def complete_assessment(
    assessment_id: str,
    command: CompleteAssessmentCommand,
    handler: CompleteAssessmentCommandHandler = Depends(get_complete_assessment_handler)
):
    """
    ✅ Completa una evaluación y obtiene resultados detallados
    
    **Parámetros:**
    - **assessment_id**: ID de la evaluación a completar
    - **answers**: Lista de respuestas finales (si las hay)
    - **total_time_minutes**: Tiempo total empleado en la evaluación
    
    **Respuesta:**
    - Resultados completos de la evaluación
    - Puntuación general y por habilidad
    - Niveles de competencia determinados
    - Fortalezas y áreas de mejora identificadas
    - Recomendaciones de escenarios de práctica
    - Ruta de aprendizaje sugerida
    """
    try:
        # Asegurar que el assessment_id del path coincida con el del comando
        command.assessment_id = assessment_id
        
        result = await handler.handle(command)
        return result
    
    except AssessmentNotStartedException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=AssessmentErrorDTO(
                error_code=e.error_code,
                message=e.message,
                details=e.details
            ).dict()
        )
    
    except AssessmentAlreadyCompletedException as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=AssessmentErrorDTO(
                error_code=e.error_code,
                message=e.message,
                details=e.details
            ).dict()
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=AssessmentErrorDTO(
                error_code="INTERNAL_ERROR",
                message="Failed to complete assessment",
                details={"original_error": str(e)}
            ).dict()
        )


@router.get("/{assessment_id}", response_model=AssessmentResultDTO)
async def get_assessment_results(
    assessment_id: str,
    user_id: str,
    assessment_repo: MongoAssessmentRepository = Depends(get_assessment_repository)
):
    """
    📊 Obtiene los resultados de una evaluación completada
    
    **Parámetros:**
    - **assessment_id**: ID de la evaluación
    - **user_id**: ID del usuario (para verificar permisos)
    
    **Respuesta:**
    - Resultados completos si la evaluación está completada
    - Error 404 si no se encuentra o no está completada
    """
    try:
        from ...domain.skill_assessment.entities import AssessmentId
        from ...domain.shared.value_objects import UserId
        
        assessment = await assessment_repo.find_by_id(AssessmentId(value=assessment_id))
        
        if not assessment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Assessment not found"
            )
        
        if assessment.user_id.value != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this assessment"
            )
        
        if not assessment.is_complete():
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Assessment is not completed yet"
            )
        
        # Mapear a DTO (implementación simplificada)
        skill_result_dtos = []
        for skill_result in assessment.skill_results:
            from ...application.skill_assessment.dtos import SkillResultDTO
            skill_result_dtos.append(SkillResultDTO(
                skill_type=skill_result.skill_type.value,
                skill_name=skill_result.skill_type.value.title(),
                questions_answered=skill_result.questions_answered,
                correct_answers=skill_result.correct_answers,
                accuracy_percentage=skill_result.accuracy_percentage.value,
                proficiency_level=skill_result.proficiency_level.value,
                strengths=skill_result.strengths,
                areas_for_improvement=skill_result.improvement_areas,
                recommended_scenarios=skill_result.recommended_scenarios
            ))
        
        return AssessmentResultDTO(
            assessment_id=assessment.assessment_id.value,
            user_id=assessment.user_id.value,
            overall_score=assessment.overall_score.value if assessment.overall_score else 0.0,
            completion_time_minutes=assessment.completion_time.minutes if assessment.completion_time else 0,
            skill_results=skill_result_dtos,
            weakest_skills=[],  # Calcular desde skill_results
            strongest_skills=[],  # Calcular desde skill_results
            recommended_learning_path=[],
            next_steps=[],
            completed_at=assessment._completed_at,
            performance_tier="average"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=AssessmentErrorDTO(
                error_code="INTERNAL_ERROR",
                message="Failed to retrieve assessment results",
                details={"original_error": str(e)}
            ).dict()
        )


@router.get("/user/{user_id}/history")
async def get_user_assessment_history(
    user_id: str,
    limit: int = 10,
    include_incomplete: bool = False,
    assessment_repo: MongoAssessmentRepository = Depends(get_assessment_repository)
):
    """
    📚 Obtiene el historial de evaluaciones de un usuario
    
    **Parámetros:**
    - **user_id**: ID del usuario
    - **limit**: Número máximo de evaluaciones a retornar (default: 10)
    - **include_incomplete**: Incluir evaluaciones incompletas (default: false)
    
    **Respuesta:**
    - Lista de evaluaciones del usuario ordenadas por fecha
    """
    try:
        from ...domain.shared.value_objects import UserId
        
        if include_incomplete:
            assessments = await assessment_repo.find_by_user_id(UserId(value=user_id))
        else:
            assessments = await assessment_repo.find_completed_by_user_id(UserId(value=user_id))
        
        # Limitar resultados
        assessments = assessments[:limit]
        
        # Mapear a DTOs simplificados
        from ...application.skill_assessment.dtos import AssessmentSummaryDTO
        summaries = []
        for assessment in assessments:
            summaries.append(AssessmentSummaryDTO(
                assessment_id=assessment.assessment_id.value,
                user_id=assessment.user_id.value,
                status=assessment.status.value,
                started_at=assessment._started_at,
                completed_at=assessment._completed_at,
                total_questions=len(assessment.skill_types) * assessment._questions_per_skill,
                answered_questions=len(assessment.user_answers),
                skill_types=[st.value for st in assessment.skill_types]
            ))
        
        return {
            "user_id": user_id,
            "total_assessments": len(summaries),
            "assessments": summaries
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=AssessmentErrorDTO(
                error_code="INTERNAL_ERROR",
                message="Failed to retrieve assessment history",
                details={"original_error": str(e)}
            ).dict()
        )
