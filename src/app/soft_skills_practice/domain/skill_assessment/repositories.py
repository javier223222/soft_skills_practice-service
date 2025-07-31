"""
Interfaces de repositorios para el bounded context Skill Assessment
"""
from abc import ABC, abstractmethod
from typing import List, Optional

from .entities import (
    Assessment, AssessmentQuestion, AssessmentId, 
    AssessmentQuestionId, UserAnswer, SkillResult
)
from ..shared.value_objects import UserId, SkillType


class AssessmentQuestionRepository(ABC):
    """Interface para repositorio de preguntas de evaluación"""
    
    @abstractmethod
    async def find_by_id(self, question_id: AssessmentQuestionId) -> Optional[AssessmentQuestion]:
        """Busca una pregunta por ID"""
        pass
    
    @abstractmethod
    async def find_by_skill_type(self, skill_type: SkillType, limit: int = 10) -> List[AssessmentQuestion]:
        """Busca preguntas por tipo de habilidad"""
        pass
    
    @abstractmethod
    async def find_random_by_skill_type(self, skill_type: SkillType, count: int) -> List[AssessmentQuestion]:
        """Busca preguntas aleatorias por tipo de habilidad"""
        pass
    
    @abstractmethod
    async def save(self, question: AssessmentQuestion) -> None:
        """Guarda una pregunta de evaluación"""
        pass
    
    @abstractmethod
    async def update_usage_stats(self, question_id: AssessmentQuestionId, success_rate: float) -> None:
        """Actualiza estadísticas de uso de una pregunta"""
        pass
    
    @abstractmethod
    async def find_by_difficulty_range(
        self, 
        skill_type: SkillType, 
        min_difficulty: int, 
        max_difficulty: int
    ) -> List[AssessmentQuestion]:
        """Busca preguntas por rango de dificultad"""
        pass


class AssessmentRepository(ABC):
    """Interface para repositorio de evaluaciones"""
    
    @abstractmethod
    async def find_by_id(self, assessment_id: AssessmentId) -> Optional[Assessment]:
        """Busca una evaluación por ID"""
        pass
    
    @abstractmethod
    async def find_by_user_id(self, user_id: UserId) -> List[Assessment]:
        """Busca evaluaciones por usuario"""
        pass
    
    @abstractmethod
    async def find_latest_by_user_id(self, user_id: UserId) -> Optional[Assessment]:
        """Busca la evaluación más reciente de un usuario"""
        pass
    
    @abstractmethod
    async def find_completed_by_user_id(self, user_id: UserId) -> List[Assessment]:
        """Busca evaluaciones completadas por usuario"""
        pass
    
    @abstractmethod
    async def save(self, assessment: Assessment) -> None:
        """Guarda una evaluación"""
        pass
    
    @abstractmethod
    async def update(self, assessment: Assessment) -> None:
        """Actualiza una evaluación existente"""
        pass
    
    @abstractmethod
    async def delete(self, assessment_id: AssessmentId) -> None:
        """Elimina una evaluación"""
        pass
    
    @abstractmethod
    async def find_in_progress_by_user_id(self, user_id: UserId) -> Optional[Assessment]:
        """Busca evaluación en progreso de un usuario"""
        pass
    
    @abstractmethod
    async def count_by_user_id(self, user_id: UserId) -> int:
        """Cuenta evaluaciones por usuario"""
        pass


class SkillResultRepository(ABC):
    """Interface para repositorio de resultados de habilidades"""
    
    @abstractmethod
    async def save_results(self, assessment_id: AssessmentId, results: List[SkillResult]) -> None:
        """Guarda resultados de habilidades de una evaluación"""
        pass
    
    @abstractmethod
    async def find_by_assessment_id(self, assessment_id: AssessmentId) -> List[SkillResult]:
        """Busca resultados por ID de evaluación"""
        pass
    
    @abstractmethod
    async def find_by_user_and_skill(self, user_id: UserId, skill_type: SkillType) -> List[SkillResult]:
        """Busca resultados por usuario y habilidad"""
        pass
    
    @abstractmethod
    async def get_user_skill_progression(self, user_id: UserId, skill_type: SkillType) -> List[SkillResult]:
        """Obtiene la progresión de un usuario en una habilidad específica"""
        pass
    
    @abstractmethod
    async def get_user_latest_results(self, user_id: UserId) -> List[SkillResult]:
        """Obtiene los resultados más recientes de un usuario"""
        pass
    
    @abstractmethod
    async def calculate_skill_statistics(self, skill_type: SkillType) -> dict:
        """Calcula estadísticas globales de una habilidad"""
        pass
