"""
Implementación concreta del repositorio de evaluaciones usando MongoDB
"""
from typing import List, Optional
import uuid
from datetime import datetime

from motor.motor_asyncio import AsyncIOMotorDatabase
from beanie import Document, Indexed
from pydantic import Field

from ...domain.skill_assessment.entities import (
    Assessment, AssessmentId, AssessmentStatus, UserAnswer, 
    SkillResult, AssessmentQuestionId, OptionId
)
from ...domain.skill_assessment.repositories import AssessmentRepository
from ...domain.shared.value_objects import UserId, SkillType, ProficiencyLevel, Score, TimeSpent


# Modelos de persistencia (Infraestructura)
class UserAnswerModel(Document):
    """Modelo de persistencia para respuestas de usuario"""
    question_id: str
    selected_option_id: str
    time_taken_seconds: int
    is_correct: bool
    answered_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "user_answers"


class SkillResultModel(Document):
    """Modelo de persistencia para resultados de habilidades"""
    skill_type: str
    questions_answered: int
    correct_answers: int
    accuracy_percentage: float
    proficiency_level: str
    strengths: List[str] = Field(default_factory=list)
    improvement_areas: List[str] = Field(default_factory=list)
    recommended_scenarios: List[str] = Field(default_factory=list)
    
    class Settings:
        name = "skill_results"


class AssessmentModel(Document):
    """Modelo de persistencia para evaluaciones"""
    assessment_id: Indexed(str, unique=True)
    user_id: Indexed(str)
    skill_types: List[str]
    questions_per_skill: int = 2
    status: str = AssessmentStatus.NOT_STARTED.value
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    user_answers: List[dict] = Field(default_factory=list)
    skill_results: List[dict] = Field(default_factory=list)
    overall_score: Optional[float] = None
    completion_time_minutes: Optional[int] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "assessments"


class MongoAssessmentRepository(AssessmentRepository):
    """Implementación concreta del repositorio de evaluaciones con MongoDB"""
    
    async def find_by_id(self, assessment_id: AssessmentId) -> Optional[Assessment]:
        """Busca una evaluación por ID"""
        model = await AssessmentModel.find_one(
            AssessmentModel.assessment_id == assessment_id.value
        )
        
        if not model:
            return None
        
        return self._map_to_domain_entity(model)
    
    async def find_by_user_id(self, user_id: UserId) -> List[Assessment]:
        """Busca evaluaciones por usuario"""
        models = await AssessmentModel.find(
            AssessmentModel.user_id == user_id.value
        ).sort(-AssessmentModel.created_at).to_list()
        
        return [self._map_to_domain_entity(model) for model in models]
    
    async def find_latest_by_user_id(self, user_id: UserId) -> Optional[Assessment]:
        """Busca la evaluación más reciente de un usuario"""
        model = await AssessmentModel.find_one(
            AssessmentModel.user_id == user_id.value,
            sort=[("created_at", -1)]
        )
        
        if not model:
            return None
        
        return self._map_to_domain_entity(model)
    
    async def find_completed_by_user_id(self, user_id: UserId) -> List[Assessment]:
        """Busca evaluaciones completadas por usuario"""
        models = await AssessmentModel.find(
            AssessmentModel.user_id == user_id.value,
            AssessmentModel.status == AssessmentStatus.COMPLETED.value
        ).sort(-AssessmentModel.completed_at).to_list()
        
        return [self._map_to_domain_entity(model) for model in models]
    
    async def find_in_progress_by_user_id(self, user_id: UserId) -> Optional[Assessment]:
        """Busca evaluación en progreso de un usuario"""
        model = await AssessmentModel.find_one(
            AssessmentModel.user_id == user_id.value,
            AssessmentModel.status == AssessmentStatus.IN_PROGRESS.value
        )
        
        if not model:
            return None
        
        return self._map_to_domain_entity(model)
    
    async def save(self, assessment: Assessment) -> None:
        """Guarda una evaluación nueva"""
        model = self._map_to_persistence_model(assessment)
        await model.insert()
    
    async def update(self, assessment: Assessment) -> None:
        """Actualiza una evaluación existente"""
        model = await AssessmentModel.find_one(
            AssessmentModel.assessment_id == assessment.assessment_id.value
        )
        
        if not model:
            raise ValueError(f"Assessment {assessment.assessment_id.value} not found")
        
        # Actualizar campos
        model.status = assessment.status.value
        model.user_answers = [self._map_user_answer_to_dict(ua) for ua in assessment.user_answers]
        model.skill_results = [self._map_skill_result_to_dict(sr) for sr in assessment.skill_results]
        
        if assessment.overall_score:
            model.overall_score = assessment.overall_score.value
        if assessment.completion_time:
            model.completion_time_minutes = assessment.completion_time.minutes
        if assessment.status == AssessmentStatus.COMPLETED:
            model.completed_at = datetime.utcnow()
        
        model.updated_at = datetime.utcnow()
        
        await model.save()
    
    async def delete(self, assessment_id: AssessmentId) -> None:
        """Elimina una evaluación"""
        await AssessmentModel.find_one(
            AssessmentModel.assessment_id == assessment_id.value
        ).delete()
    
    async def count_by_user_id(self, user_id: UserId) -> int:
        """Cuenta evaluaciones por usuario"""
        return await AssessmentModel.find(
            AssessmentModel.user_id == user_id.value
        ).count()
    
    def _map_to_domain_entity(self, model: AssessmentModel) -> Assessment:
        """Mapea modelo de persistencia a entidad de dominio"""
        
        # Crear entidad base
        assessment = Assessment(
            assessment_id=AssessmentId(value=model.assessment_id),
            user_id=UserId(value=model.user_id),
            skill_types=[SkillType(value=st) for st in model.skill_types],
            questions_per_skill=model.questions_per_skill
        )
        
        # Restaurar estado
        assessment._status = AssessmentStatus(model.status)
        assessment._started_at = model.started_at
        assessment._completed_at = model.completed_at
        
        # Restaurar respuestas
        assessment._user_answers = [
            self._map_dict_to_user_answer(ua_dict) for ua_dict in model.user_answers
        ]
        
        # Restaurar resultados de habilidades
        assessment._skill_results = [
            self._map_dict_to_skill_result(sr_dict) for sr_dict in model.skill_results
        ]
        
        # Restaurar métricas
        if model.overall_score is not None:
            assessment._overall_score = Score(value=model.overall_score)
        if model.completion_time_minutes is not None:
            assessment._completion_time = TimeSpent(minutes=model.completion_time_minutes)
        
        return assessment
    
    def _map_to_persistence_model(self, assessment: Assessment) -> AssessmentModel:
        """Mapea entidad de dominio a modelo de persistencia"""
        return AssessmentModel(
            assessment_id=assessment.assessment_id.value,
            user_id=assessment.user_id.value,
            skill_types=[st.value for st in assessment.skill_types],
            questions_per_skill=assessment._questions_per_skill,
            status=assessment.status.value,
            started_at=assessment._started_at,
            completed_at=assessment._completed_at,
            user_answers=[self._map_user_answer_to_dict(ua) for ua in assessment.user_answers],
            skill_results=[self._map_skill_result_to_dict(sr) for sr in assessment.skill_results],
            overall_score=assessment.overall_score.value if assessment.overall_score else None,
            completion_time_minutes=assessment.completion_time.minutes if assessment.completion_time else None
        )
    
    def _map_user_answer_to_dict(self, user_answer: UserAnswer) -> dict:
        """Mapea UserAnswer a diccionario"""
        return {
            "question_id": user_answer.question_id.value,
            "selected_option_id": user_answer.selected_option_id.value,
            "time_taken_seconds": user_answer.time_taken_seconds,
            "is_correct": user_answer.is_correct,
            "answered_at": user_answer.answered_at
        }
    
    def _map_dict_to_user_answer(self, ua_dict: dict) -> UserAnswer:
        """Mapea diccionario a UserAnswer"""
        return UserAnswer(
            question_id=AssessmentQuestionId(value=ua_dict["question_id"]),
            selected_option_id=OptionId(value=ua_dict["selected_option_id"]),
            time_taken_seconds=ua_dict["time_taken_seconds"],
            is_correct=ua_dict["is_correct"]
        )
    
    def _map_skill_result_to_dict(self, skill_result: SkillResult) -> dict:
        """Mapea SkillResult a diccionario"""
        return {
            "skill_type": skill_result.skill_type.value,
            "questions_answered": skill_result.questions_answered,
            "correct_answers": skill_result.correct_answers,
            "accuracy_percentage": skill_result.accuracy_percentage.value,
            "proficiency_level": skill_result.proficiency_level.value,
            "strengths": skill_result.strengths,
            "improvement_areas": skill_result.improvement_areas,
            "recommended_scenarios": skill_result.recommended_scenarios
        }
    
    def _map_dict_to_skill_result(self, sr_dict: dict) -> SkillResult:
        """Mapea diccionario a SkillResult"""
        return SkillResult(
            skill_type=SkillType(value=sr_dict["skill_type"]),
            questions_answered=sr_dict["questions_answered"],
            correct_answers=sr_dict["correct_answers"],
            proficiency_level=ProficiencyLevel(sr_dict["proficiency_level"]),
            strengths=sr_dict["strengths"],
            improvement_areas=sr_dict["improvement_areas"],
            recommended_scenarios=sr_dict["recommended_scenarios"]
        )
