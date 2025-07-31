"""
Entidades del bounded context Skill Assessment
"""
from typing import List, Dict, Optional, Any
from datetime import datetime
from enum import Enum

from ..shared.value_objects import (
    UserId, SkillType, ProficiencyLevel, Score, 
    Percentage, TimeSpent, ValueObject
)
from ..shared.exceptions import (
    AssessmentAlreadyCompletedException, 
    InvalidAssessmentAnswerException,
    AssessmentNotStartedException
)


class AssessmentQuestionId(ValueObject):
    """Value Object para ID de pregunta de evaluación"""
    value: str


class AssessmentId(ValueObject):
    """Value Object para ID de evaluación"""
    value: str


class OptionId(ValueObject):
    """Value Object para ID de opción de respuesta"""
    value: str


class QuestionDifficulty(ValueObject):
    """Value Object para dificultad de pregunta"""
    level: int
    
    def __post_init__(self):
        if not 1 <= self.level <= 5:
            raise ValueError("Question difficulty must be between 1 and 5")


class AssessmentQuestion:
    """Entidad para preguntas de evaluación"""
    
    def __init__(
        self,
        question_id: AssessmentQuestionId,
        skill_type: SkillType,
        question_text: str,
        scenario_context: str,
        options: Dict[str, str],
        correct_option_id: OptionId,
        difficulty: QuestionDifficulty,
        explanation: str,
        tags: List[str],
        created_at: datetime
    ):
        self._question_id = question_id
        self._skill_type = skill_type
        self._question_text = question_text
        self._scenario_context = scenario_context
        self._options = options.copy()  # Inmutable copy
        self._correct_option_id = correct_option_id
        self._difficulty = difficulty
        self._explanation = explanation
        self._tags = tags.copy()
        self._created_at = created_at
        self._usage_count = 0
        self._success_rate = 0.0
        
    @property
    def question_id(self) -> AssessmentQuestionId:
        return self._question_id
    
    @property
    def skill_type(self) -> SkillType:
        return self._skill_type
    
    @property
    def question_text(self) -> str:
        return self._question_text
    
    @property
    def scenario_context(self) -> str:
        return self._scenario_context
    
    @property
    def options(self) -> Dict[str, str]:
        return self._options.copy()
    
    @property
    def difficulty(self) -> QuestionDifficulty:
        return self._difficulty
    
    @property
    def tags(self) -> List[str]:
        return self._tags.copy()
    
    @property
    def usage_count(self) -> int:
        return self._usage_count
    
    @property
    def success_rate(self) -> float:
        return self._success_rate
    
    def is_correct_answer(self, option_id: OptionId) -> bool:
        """Verifica si la opción seleccionada es correcta"""
        return option_id.value == self._correct_option_id.value
    
    def get_explanation(self) -> str:
        """Retorna la explicación de la respuesta correcta"""
        return self._explanation
    
    def increment_usage(self) -> None:
        """Incrementa el contador de uso de la pregunta"""
        self._usage_count += 1
    
    def update_success_rate(self, new_rate: float) -> None:
        """Actualiza la tasa de éxito de la pregunta"""
        if 0 <= new_rate <= 100:
            self._success_rate = new_rate


class UserAnswer:
    """Value Object para respuesta de usuario"""
    
    def __init__(
        self,
        question_id: AssessmentQuestionId,
        selected_option_id: OptionId,
        time_taken_seconds: int,
        is_correct: bool
    ):
        if time_taken_seconds < 0:
            raise ValueError("Time taken cannot be negative")
        
        self._question_id = question_id
        self._selected_option_id = selected_option_id
        self._time_taken_seconds = time_taken_seconds
        self._is_correct = is_correct
        self._answered_at = datetime.utcnow()
    
    @property
    def question_id(self) -> AssessmentQuestionId:
        return self._question_id
    
    @property
    def selected_option_id(self) -> OptionId:
        return self._selected_option_id
    
    @property
    def time_taken_seconds(self) -> int:
        return self._time_taken_seconds
    
    @property
    def is_correct(self) -> bool:
        return self._is_correct
    
    @property
    def answered_at(self) -> datetime:
        return self._answered_at


class SkillResult:
    """Value Object para resultado de habilidad específica"""
    
    def __init__(
        self,
        skill_type: SkillType,
        questions_answered: int,
        correct_answers: int,
        proficiency_level: ProficiencyLevel,
        strengths: List[str],
        improvement_areas: List[str],
        recommended_scenarios: List[str]
    ):
        if questions_answered <= 0:
            raise ValueError("Questions answered must be positive")
        if correct_answers < 0 or correct_answers > questions_answered:
            raise ValueError("Correct answers must be between 0 and questions answered")
        
        self._skill_type = skill_type
        self._questions_answered = questions_answered
        self._correct_answers = correct_answers
        self._accuracy_percentage = Percentage(value=(correct_answers / questions_answered) * 100)
        self._proficiency_level = proficiency_level
        self._strengths = strengths.copy()
        self._improvement_areas = improvement_areas.copy()
        self._recommended_scenarios = recommended_scenarios.copy()
    
    @property
    def skill_type(self) -> SkillType:
        return self._skill_type
    
    @property
    def questions_answered(self) -> int:
        return self._questions_answered
    
    @property
    def correct_answers(self) -> int:
        return self._correct_answers
    
    @property
    def accuracy_percentage(self) -> Percentage:
        return self._accuracy_percentage
    
    @property
    def proficiency_level(self) -> ProficiencyLevel:
        return self._proficiency_level
    
    @property
    def strengths(self) -> List[str]:
        return self._strengths.copy()
    
    @property
    def improvement_areas(self) -> List[str]:
        return self._improvement_areas.copy()
    
    @property
    def recommended_scenarios(self) -> List[str]:
        return self._recommended_scenarios.copy()


class AssessmentStatus(str, Enum):
    """Estados posibles de una evaluación"""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress" 
    COMPLETED = "completed"
    EXPIRED = "expired"


class Assessment:
    """Agregado raíz para evaluaciones de habilidades"""
    
    def __init__(
        self,
        assessment_id: AssessmentId,
        user_id: UserId,
        skill_types: List[SkillType],
        questions_per_skill: int = 2
    ):
        if questions_per_skill < 1:
            raise ValueError("Questions per skill must be at least 1")
        if not skill_types:
            raise ValueError("At least one skill type is required")
        
        self._assessment_id = assessment_id
        self._user_id = user_id
        self._skill_types = skill_types.copy()
        self._questions_per_skill = questions_per_skill
        self._status = AssessmentStatus.NOT_STARTED
        self._started_at: Optional[datetime] = None
        self._completed_at: Optional[datetime] = None
        self._user_answers: List[UserAnswer] = []
        self._skill_results: List[SkillResult] = []
        self._overall_score: Optional[Score] = None
        self._completion_time: Optional[TimeSpent] = None
        
        # Domain events
        self._domain_events: List[Any] = []
    
    @property
    def assessment_id(self) -> AssessmentId:
        return self._assessment_id
    
    @property
    def user_id(self) -> UserId:
        return self._user_id
    
    @property
    def skill_types(self) -> List[SkillType]:
        return self._skill_types.copy()
    
    @property
    def status(self) -> AssessmentStatus:
        return self._status
    
    @property
    def user_answers(self) -> List[UserAnswer]:
        return self._user_answers.copy()
    
    @property
    def skill_results(self) -> List[SkillResult]:
        return self._skill_results.copy()
    
    @property
    def overall_score(self) -> Optional[Score]:
        return self._overall_score
    
    @property
    def completion_time(self) -> Optional[TimeSpent]:
        return self._completion_time
    
    @property
    def domain_events(self) -> List[Any]:
        events = self._domain_events.copy()
        self._domain_events.clear()  # Clear after reading
        return events
    
    def start_assessment(self) -> None:
        """Inicia la evaluación"""
        if self._status != AssessmentStatus.NOT_STARTED:
            raise AssessmentAlreadyCompletedException(self._assessment_id.value)
        
        self._status = AssessmentStatus.IN_PROGRESS
        self._started_at = datetime.utcnow()
        
        # Add domain event
        from ..shared.domain_events import AssessmentStartedEvent
        event = AssessmentStartedEvent(
            aggregate_id=self._assessment_id.value,
            user_id=self._user_id.value,
            assessment_id=self._assessment_id.value,
            skill_types=[st.value for st in self._skill_types],
            total_questions=len(self._skill_types) * self._questions_per_skill
        )
        self._domain_events.append(event)
    
    def submit_answer(self, answer: UserAnswer) -> None:
        """Envía una respuesta de usuario"""
        if self._status != AssessmentStatus.IN_PROGRESS:
            raise AssessmentNotStartedException(self._assessment_id.value)
        
        # Verificar que no se responda la misma pregunta dos veces
        existing_answer = next(
            (ua for ua in self._user_answers if ua.question_id.value == answer.question_id.value),
            None
        )
        if existing_answer:
            raise InvalidAssessmentAnswerException(
                answer.question_id.value, 
                "Question already answered"
            )
        
        self._user_answers.append(answer)
    
    def complete_assessment(self, skill_results: List[SkillResult]) -> None:
        """Completa la evaluación con los resultados"""
        if self._status != AssessmentStatus.IN_PROGRESS:
            raise AssessmentNotStartedException(self._assessment_id.value)
        
        if not skill_results:
            raise ValueError("Skill results are required to complete assessment")
        
        self._skill_results = skill_results.copy()
        self._status = AssessmentStatus.COMPLETED
        self._completed_at = datetime.utcnow()
        
        # Calcular tiempo de completación
        if self._started_at:
            time_diff = self._completed_at - self._started_at
            self._completion_time = TimeSpent(minutes=int(time_diff.total_seconds() / 60))
        
        # Calcular puntaje general
        if skill_results:
            avg_accuracy = sum(sr.accuracy_percentage.value for sr in skill_results) / len(skill_results)
            self._overall_score = Score(value=avg_accuracy)
        
        # Add domain event
        from ..shared.domain_events import AssessmentCompletedEvent
        event = AssessmentCompletedEvent(
            aggregate_id=self._assessment_id.value,
            user_id=self._user_id.value,
            assessment_id=self._assessment_id.value,
            overall_score=self._overall_score.value if self._overall_score else 0.0,
            skill_results={sr.skill_type.value: sr.accuracy_percentage.value for sr in skill_results},
            proficiency_levels={sr.skill_type.value: sr.proficiency_level.value for sr in skill_results},
            completion_time_minutes=self._completion_time.minutes if self._completion_time else 0
        )
        self._domain_events.append(event)
    
    def get_progress_percentage(self) -> Percentage:
        """Calcula el porcentaje de progreso"""
        total_questions = len(self._skill_types) * self._questions_per_skill
        answered_questions = len(self._user_answers)
        
        if total_questions == 0:
            return Percentage(value=0.0)
        
        return Percentage(value=(answered_questions / total_questions) * 100)
    
    def is_complete(self) -> bool:
        """Verifica si la evaluación está completa"""
        return self._status == AssessmentStatus.COMPLETED
    
    def get_answers_for_skill(self, skill_type: SkillType) -> List[UserAnswer]:
        """Obtiene las respuestas para una habilidad específica"""
        # Esta implementación requeriría acceso a las preguntas para filtrar por skill_type
        # En una implementación real, se consultaría el repositorio de preguntas
        return [answer for answer in self._user_answers 
                if self._is_answer_for_skill(answer, skill_type)]
    
    def _is_answer_for_skill(self, answer: UserAnswer, skill_type: SkillType) -> bool:
        """Helper method para determinar si una respuesta pertenece a una habilidad"""
        # En una implementación real, esto requeriría consultar las preguntas
        # Por ahora retornamos True como placeholder
        return True
