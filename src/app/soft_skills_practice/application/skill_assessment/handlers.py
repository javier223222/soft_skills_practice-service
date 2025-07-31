"""
Command Handlers para el bounded context Skill Assessment
"""
from typing import List, Optional
import uuid
from datetime import datetime

from .commands import (
    StartAssessmentCommand, SubmitAnswerCommand, CompleteAssessmentCommand,
    RetakeAssessmentCommand, GetAssessmentProgressCommand
)
from .dtos import (
    StartAssessmentResponseDTO, SubmitAnswerResponseDTO, AssessmentResultDTO,
    AssessmentProgressDTO, AssessmentQuestionDTO, SkillResultDTO
)
from ...domain.skill_assessment.entities import (
    Assessment, AssessmentId, UserAnswer, AssessmentQuestionId, OptionId
)
from ...domain.skill_assessment.repositories import (
    AssessmentRepository, AssessmentQuestionRepository, SkillResultRepository
)
from ...domain.skill_assessment.domain_services import (
    SkillEvaluationService, AssessmentAnalyticsService
)
from ...domain.shared.value_objects import UserId, SkillType
from ...domain.shared.exceptions import (
    AssessmentNotStartedException, AssessmentAlreadyCompletedException,
    InsufficientQuestionsException
)
from ...domain.shared.domain_events import DomainEventPublisher


class StartAssessmentCommandHandler:
    """Handler para comando de inicio de evaluación"""
    
    def __init__(
        self,
        assessment_repository: AssessmentRepository,
        question_repository: AssessmentQuestionRepository,
        domain_event_publisher: DomainEventPublisher
    ):
        self._assessment_repository = assessment_repository
        self._question_repository = question_repository
        self._domain_event_publisher = domain_event_publisher
    
    async def handle(self, command: StartAssessmentCommand) -> StartAssessmentResponseDTO:
        """Maneja el comando de inicio de evaluación"""
        
        # Verificar si el usuario ya tiene una evaluación en progreso
        user_id = UserId(value=command.user_id)
        existing_assessment = await self._assessment_repository.find_in_progress_by_user_id(user_id)
        
        if existing_assessment:
            raise AssessmentAlreadyCompletedException(
                f"User {command.user_id} already has an assessment in progress"
            )
        
        # Definir habilidades a evaluar
        skill_types = self._determine_skill_types(command.skill_types)
        
        # Verificar que hay suficientes preguntas
        await self._validate_sufficient_questions(skill_types, command.questions_per_skill)
        
        # Crear nueva evaluación
        assessment_id = AssessmentId(value=str(uuid.uuid4()))
        assessment = Assessment(
            assessment_id=assessment_id,
            user_id=user_id,
            skill_types=skill_types,
            questions_per_skill=command.questions_per_skill
        )
        
        # Iniciar evaluación
        assessment.start_assessment()
        
        # Guardar evaluación
        await self._assessment_repository.save(assessment)
        
        # Publicar eventos de dominio
        for event in assessment.domain_events:
            await self._domain_event_publisher.publish(event)
        
        # Obtener primera pregunta
        first_question = await self._get_first_question(skill_types[0])
        
        return StartAssessmentResponseDTO(
            assessment_id=assessment_id.value,
            user_id=command.user_id,
            total_questions=len(skill_types) * command.questions_per_skill,
            questions_per_skill=command.questions_per_skill,
            skill_types=[st.value for st in skill_types],
            estimated_duration_minutes=self._calculate_estimated_duration(len(skill_types) * command.questions_per_skill),
            first_question=self._map_question_to_dto(first_question)
        )
    
    def _determine_skill_types(self, requested_skills: Optional[List[str]]) -> List[SkillType]:
        """Determina las habilidades a evaluar"""
        if requested_skills:
            return [SkillType(value=skill) for skill in requested_skills]
        
        # Habilidades por defecto
        default_skills = [
            'communication', 'leadership', 'teamwork', 'problem_solving',
            'time_management', 'emotional_intelligence', 'adaptability',
            'conflict_resolution', 'decision_making', 'critical_thinking'
        ]
        return [SkillType(value=skill) for skill in default_skills]
    
    async def _validate_sufficient_questions(self, skill_types: List[SkillType], questions_per_skill: int):
        """Valida que hay suficientes preguntas para cada habilidad"""
        for skill_type in skill_types:
            available_questions = await self._question_repository.find_by_skill_type(skill_type)
            if len(available_questions) < questions_per_skill:
                raise InsufficientQuestionsException(
                    skill_type.value, 
                    questions_per_skill, 
                    len(available_questions)
                )
    
    async def _get_first_question(self, skill_type: SkillType) -> 'AssessmentQuestion':
        """Obtiene la primera pregunta para la evaluación"""
        questions = await self._question_repository.find_random_by_skill_type(skill_type, 1)
        if not questions:
            raise InsufficientQuestionsException(skill_type.value, 1, 0)
        return questions[0]
    
    def _calculate_estimated_duration(self, total_questions: int) -> int:
        """Calcula la duración estimada en minutos"""
        return max(10, total_questions * 1)  # Mínimo 10 minutos, 1 minuto por pregunta
    
    def _map_question_to_dto(self, question: 'AssessmentQuestion') -> AssessmentQuestionDTO:
        """Mapea una pregunta de dominio a DTO"""
        return AssessmentQuestionDTO(
            question_id=question.question_id.value,
            skill_type=question.skill_type.value,
            skill_name=self._get_skill_display_name(question.skill_type.value),
            question_text=question.question_text,
            scenario_context=question.scenario_context,
            options=question.options,
            difficulty_level=question.difficulty.level,
            tags=question.tags
        )
    
    def _get_skill_display_name(self, skill_type: str) -> str:
        """Convierte el tipo de habilidad a nombre de display"""
        skill_names = {
            'communication': 'Communication Skills',
            'leadership': 'Leadership',
            'teamwork': 'Teamwork & Collaboration',
            'problem_solving': 'Problem Solving',
            'time_management': 'Time Management',
            'emotional_intelligence': 'Emotional Intelligence',
            'adaptability': 'Adaptability',
            'conflict_resolution': 'Conflict Resolution',
            'decision_making': 'Decision Making',
            'critical_thinking': 'Critical Thinking'
        }
        return skill_names.get(skill_type, skill_type.title())


class SubmitAnswerCommandHandler:
    """Handler para comando de envío de respuesta"""
    
    def __init__(
        self,
        assessment_repository: AssessmentRepository,
        question_repository: AssessmentQuestionRepository
    ):
        self._assessment_repository = assessment_repository
        self._question_repository = question_repository
    
    async def handle(self, command: SubmitAnswerCommand) -> SubmitAnswerResponseDTO:
        """Maneja el comando de envío de respuesta"""
        
        # Obtener evaluación
        assessment_id = AssessmentId(value=command.assessment_id)
        assessment = await self._assessment_repository.find_by_id(assessment_id)
        
        if not assessment:
            raise AssessmentNotStartedException(command.assessment_id)
        
        # Obtener pregunta
        question_id = AssessmentQuestionId(value=command.question_id)
        question = await self._question_repository.find_by_id(question_id)
        
        if not question:
            raise ValueError(f"Question {command.question_id} not found")
        
        # Verificar respuesta
        option_id = OptionId(value=command.selected_option_id)
        is_correct = question.is_correct_answer(option_id)
        
        # Crear respuesta de usuario
        user_answer = UserAnswer(
            question_id=question_id,
            selected_option_id=option_id,
            time_taken_seconds=command.time_taken_seconds,
            is_correct=is_correct
        )
        
        # Enviar respuesta a la evaluación
        assessment.submit_answer(user_answer)
        
        # Actualizar evaluación
        await self._assessment_repository.update(assessment)
        
        # Obtener progreso actual
        progress = self._calculate_progress(assessment)
        
        # Determinar siguiente pregunta
        next_question = await self._get_next_question(assessment)
        
        return SubmitAnswerResponseDTO(
            question_id=command.question_id,
            is_correct=is_correct,
            next_question=next_question,
            progress=progress,
            is_assessment_complete=assessment.is_complete()
        )
    
    def _calculate_progress(self, assessment: Assessment) -> AssessmentProgressDTO:
        """Calcula el progreso de la evaluación"""
        total_questions = len(assessment.skill_types) * 2  # Asumiendo 2 preguntas por habilidad
        answered_questions = len(assessment.user_answers)
        progress_percentage = assessment.get_progress_percentage().value
        
        return AssessmentProgressDTO(
            assessment_id=assessment.assessment_id.value,
            user_id=assessment.user_id.value,
            total_questions=total_questions,
            answered_questions=answered_questions,
            progress_percentage=progress_percentage,
            estimated_remaining_time_minutes=max(0, (total_questions - answered_questions) * 1)
        )
    
    async def _get_next_question(self, assessment: Assessment) -> Optional[AssessmentQuestionDTO]:
        """Obtiene la siguiente pregunta si está disponible"""
        if assessment.is_complete():
            return None
        
        # Lógica simplificada: obtener una pregunta aleatoria del siguiente skill type
        # En una implementación real, esto sería más sofisticado
        remaining_skills = assessment.skill_types  # Simplificado
        if remaining_skills:
            questions = await self._question_repository.find_random_by_skill_type(remaining_skills[0], 1)
            if questions:
                question = questions[0]
                return AssessmentQuestionDTO(
                    question_id=question.question_id.value,
                    skill_type=question.skill_type.value,
                    skill_name=self._get_skill_display_name(question.skill_type.value),
                    question_text=question.question_text,
                    scenario_context=question.scenario_context,
                    options=question.options,
                    difficulty_level=question.difficulty.level,
                    tags=question.tags
                )
        return None
    
    def _get_skill_display_name(self, skill_type: str) -> str:
        """Convierte el tipo de habilidad a nombre de display"""
        skill_names = {
            'communication': 'Communication Skills',
            'leadership': 'Leadership',
            'teamwork': 'Teamwork & Collaboration',
            'problem_solving': 'Problem Solving',
            'time_management': 'Time Management',
            'emotional_intelligence': 'Emotional Intelligence',
            'adaptability': 'Adaptability',
            'conflict_resolution': 'Conflict Resolution',
            'decision_making': 'Decision Making',
            'critical_thinking': 'Critical Thinking'
        }
        return skill_names.get(skill_type, skill_type.title())


class CompleteAssessmentCommandHandler:
    """Handler para comando de completar evaluación"""
    
    def __init__(
        self,
        assessment_repository: AssessmentRepository,
        question_repository: AssessmentQuestionRepository,
        skill_evaluation_service: SkillEvaluationService,
        analytics_service: AssessmentAnalyticsService,
        domain_event_publisher: DomainEventPublisher
    ):
        self._assessment_repository = assessment_repository
        self._question_repository = question_repository
        self._skill_evaluation_service = skill_evaluation_service
        self._analytics_service = analytics_service
        self._domain_event_publisher = domain_event_publisher
    
    async def handle(self, command: CompleteAssessmentCommand) -> AssessmentResultDTO:
        """Maneja el comando de completar evaluación"""
        
        # Obtener evaluación
        assessment_id = AssessmentId(value=command.assessment_id)
        assessment = await self._assessment_repository.find_by_id(assessment_id)
        
        if not assessment:
            raise AssessmentNotStartedException(command.assessment_id)
        
        if assessment.is_complete():
            raise AssessmentAlreadyCompletedException(command.assessment_id)
        
        # Procesar respuestas restantes si las hay
        await self._process_remaining_answers(assessment, command.answers)
        
        # Evaluar resultados por habilidad
        skill_results = []
        for skill_type in assessment.skill_types:
            skill_result = await self._skill_evaluation_service.evaluate_skill_performance(
                skill_type, assessment.user_answers
            )
            skill_results.append(skill_result)
        
        # Completar evaluación
        assessment.complete_assessment(skill_results)
        
        # Actualizar evaluación
        await self._assessment_repository.update(assessment)
        
        # Publicar eventos de dominio
        for event in assessment.domain_events:
            await self._domain_event_publisher.publish(event)
        
        # Generar insights de rendimiento
        insights = await self._analytics_service.generate_performance_insights(assessment)
        
        # Mapear a DTO de respuesta
        return self._map_to_result_dto(assessment, insights)
    
    async def _process_remaining_answers(self, assessment: Assessment, answers: List[SubmitAnswerCommand]):
        """Procesa respuestas restantes"""
        for answer_cmd in answers:
            question_id = AssessmentQuestionId(value=answer_cmd.question_id)
            question = await self._question_repository.find_by_id(question_id)
            
            if question:
                option_id = OptionId(value=answer_cmd.selected_option_id)
                is_correct = question.is_correct_answer(option_id)
                
                user_answer = UserAnswer(
                    question_id=question_id,
                    selected_option_id=option_id,
                    time_taken_seconds=answer_cmd.time_taken_seconds,
                    is_correct=is_correct
                )
                
                assessment.submit_answer(user_answer)
    
    def _map_to_result_dto(self, assessment: Assessment, insights: dict) -> AssessmentResultDTO:
        """Mapea evaluación y insights a DTO de resultado"""
        skill_result_dtos = []
        for skill_result in assessment.skill_results:
            skill_result_dtos.append(SkillResultDTO(
                skill_type=skill_result.skill_type.value,
                skill_name=self._get_skill_display_name(skill_result.skill_type.value),
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
            weakest_skills=insights.get('weakest_skills', []),
            strongest_skills=insights.get('strongest_skills', []),
            recommended_learning_path=insights.get('recommended_learning_path', []),
            next_steps=insights.get('recommended_focus_areas', []),
            completed_at=datetime.utcnow(),
            performance_tier=insights.get('performance_tier', 'average')
        )
    
    def _get_skill_display_name(self, skill_type: str) -> str:
        """Convierte el tipo de habilidad a nombre de display"""
        skill_names = {
            'communication': 'Communication Skills',
            'leadership': 'Leadership',
            'teamwork': 'Teamwork & Collaboration',
            'problem_solving': 'Problem Solving',
            'time_management': 'Time Management',
            'emotional_intelligence': 'Emotional Intelligence',
            'adaptability': 'Adaptability',
            'conflict_resolution': 'Conflict Resolution',
            'decision_making': 'Decision Making',
            'critical_thinking': 'Critical Thinking'
        }
        return skill_names.get(skill_type, skill_type.title())
