"""
Servicios de dominio para el bounded context Skill Assessment
"""
from typing import List, Dict, Any
from ..shared.value_objects import SkillType, ProficiencyLevel, Percentage
from .entities import UserAnswer, SkillResult, AssessmentQuestion, Assessment
from .repositories import AssessmentQuestionRepository, SkillResultRepository


class SkillEvaluationService:
    """Servicio de dominio para evaluación de habilidades"""
    
    def __init__(self, question_repository: AssessmentQuestionRepository):
        self._question_repository = question_repository
    
    async def evaluate_skill_performance(
        self, 
        skill_type: SkillType, 
        user_answers: List[UserAnswer]
    ) -> SkillResult:
        """Evalúa el rendimiento en una habilidad específica"""
        
        # Obtener preguntas para calcular contexto
        skill_questions = []
        for answer in user_answers:
            question = await self._question_repository.find_by_id(answer.question_id)
            if question and question.skill_type.value == skill_type.value:
                skill_questions.append(question)
        
        if not skill_questions:
            raise ValueError(f"No questions found for skill type: {skill_type.value}")
        
        # Filtrar respuestas para esta habilidad
        skill_answers = [
            answer for answer in user_answers 
            if any(q.question_id.value == answer.question_id.value for q in skill_questions)
        ]
        
        questions_answered = len(skill_answers)
        correct_answers = sum(1 for answer in skill_answers if answer.is_correct)
        
        if questions_answered == 0:
            raise ValueError(f"No answers found for skill type: {skill_type.value}")
        
        # Calcular nivel de competencia
        accuracy = (correct_answers / questions_answered) * 100
        proficiency_level = self._determine_proficiency_level(accuracy)
        
        # Generar fortalezas y áreas de mejora
        strengths = self._generate_strengths(skill_type, accuracy, skill_questions)
        improvement_areas = self._generate_improvement_areas(skill_type, accuracy, skill_questions)
        
        # Recomendar escenarios
        recommended_scenarios = self._recommend_scenarios(skill_type, proficiency_level)
        
        return SkillResult(
            skill_type=skill_type,
            questions_answered=questions_answered,
            correct_answers=correct_answers,
            proficiency_level=proficiency_level,
            strengths=strengths,
            improvement_areas=improvement_areas,
            recommended_scenarios=recommended_scenarios
        )
    
    def _determine_proficiency_level(self, accuracy: float) -> ProficiencyLevel:
        """Determina el nivel de competencia basado en precisión"""
        if accuracy >= 85:
            return ProficiencyLevel.EXPERT
        elif accuracy >= 75:
            return ProficiencyLevel.ADVANCED
        elif accuracy >= 60:
            return ProficiencyLevel.INTERMEDIATE
        else:
            return ProficiencyLevel.BEGINNER
    
    def _generate_strengths(
        self, 
        skill_type: SkillType, 
        accuracy: float, 
        questions: List[AssessmentQuestion]
    ) -> List[str]:
        """Genera lista de fortalezas basada en el rendimiento"""
        strengths = []
        
        if accuracy >= 80:
            strengths.append(f"Strong understanding of {skill_type.value} fundamentals")
        
        if accuracy >= 70:
            strengths.append(f"Good practical application of {skill_type.value} concepts")
        
        # Analizar por tags de preguntas si hay patrones
        if questions:
            high_performance_tags = []
            for question in questions:
                # En una implementación real, analizaríamos las respuestas específicas
                if accuracy >= 75:
                    high_performance_tags.extend(question.tags)
            
            # Agregar fortalezas específicas basadas en tags
            unique_tags = list(set(high_performance_tags))
            for tag in unique_tags[:2]:  # Máximo 2 fortalezas específicas
                strengths.append(f"Excellent performance in {tag} scenarios")
        
        return strengths[:3]  # Máximo 3 fortalezas
    
    def _generate_improvement_areas(
        self, 
        skill_type: SkillType, 
        accuracy: float, 
        questions: List[AssessmentQuestion]
    ) -> List[str]:
        """Genera áreas de mejora basada en el rendimiento"""
        improvements = []
        
        if accuracy < 60:
            improvements.append(f"Focus on building {skill_type.value} foundation")
        
        if accuracy < 75:
            improvements.append(f"Practice applying {skill_type.value} in complex situations")
        
        if accuracy < 85:
            improvements.append(f"Refine advanced {skill_type.value} techniques")
        
        return improvements[:3]  # Máximo 3 áreas de mejora
    
    def _recommend_scenarios(self, skill_type: SkillType, proficiency_level: ProficiencyLevel) -> List[str]:
        """Recomienda escenarios basados en el nivel de competencia"""
        skill_scenarios = {
            'communication': {
                ProficiencyLevel.BEGINNER: [
                    'basic_presentation_scenario',
                    'simple_team_meeting_scenario'
                ],
                ProficiencyLevel.INTERMEDIATE: [
                    'difficult_conversation_scenario',
                    'cross_functional_collaboration_scenario'
                ],
                ProficiencyLevel.ADVANCED: [
                    'crisis_communication_scenario',
                    'executive_presentation_scenario'
                ],
                ProficiencyLevel.EXPERT: [
                    'stakeholder_negotiation_scenario',
                    'public_speaking_scenario'
                ]
            },
            'leadership': {
                ProficiencyLevel.BEGINNER: [
                    'team_motivation_scenario',
                    'basic_delegation_scenario'
                ],
                ProficiencyLevel.INTERMEDIATE: [
                    'conflict_resolution_scenario',
                    'performance_management_scenario'
                ],
                ProficiencyLevel.ADVANCED: [
                    'strategic_decision_scenario',
                    'change_management_scenario'
                ],
                ProficiencyLevel.EXPERT: [
                    'organizational_transformation_scenario',
                    'crisis_leadership_scenario'
                ]
            }
        }
        
        # Obtener escenarios para la habilidad y nivel específico
        skill_type_scenarios = skill_scenarios.get(skill_type.value, {})
        return skill_type_scenarios.get(proficiency_level, [f'{skill_type.value}_practice_scenario'])


class ProficiencyLevelCalculator:
    """Servicio para calcular niveles de competencia"""
    
    def calculate_overall_proficiency(self, skill_results: List[SkillResult]) -> ProficiencyLevel:
        """Calcula el nivel de competencia general"""
        if not skill_results:
            return ProficiencyLevel.BEGINNER
        
        # Calcular promedio ponderado de precisión
        total_questions = sum(sr.questions_answered for sr in skill_results)
        if total_questions == 0:
            return ProficiencyLevel.BEGINNER
        
        weighted_accuracy = sum(
            sr.accuracy_percentage.value * sr.questions_answered 
            for sr in skill_results
        ) / total_questions
        
        # Determinar nivel basado en promedio
        if weighted_accuracy >= 85:
            return ProficiencyLevel.EXPERT
        elif weighted_accuracy >= 75:
            return ProficiencyLevel.ADVANCED
        elif weighted_accuracy >= 60:
            return ProficiencyLevel.INTERMEDIATE
        else:
            return ProficiencyLevel.BEGINNER
    
    def identify_skill_gaps(self, skill_results: List[SkillResult]) -> List[SkillType]:
        """Identifica habilidades con gaps significativos"""
        gaps = []
        
        for result in skill_results:
            if result.proficiency_level in [ProficiencyLevel.BEGINNER, ProficiencyLevel.INTERMEDIATE]:
                gaps.append(result.skill_type)
        
        # Ordenar por menor precisión
        gaps.sort(key=lambda skill: next(
            sr.accuracy_percentage.value for sr in skill_results 
            if sr.skill_type.value == skill.value
        ))
        
        return gaps
    
    def calculate_improvement_potential(self, skill_results: List[SkillResult]) -> Dict[str, float]:
        """Calcula el potencial de mejora por habilidad"""
        potential = {}
        
        for result in skill_results:
            current_accuracy = result.accuracy_percentage.value
            max_potential = 100.0
            improvement_potential = max_potential - current_accuracy
            potential[result.skill_type.value] = improvement_potential
        
        return potential


class AssessmentAnalyticsService:
    """Servicio para análisis y métricas de evaluaciones"""
    
    def __init__(self, skill_result_repository: SkillResultRepository):
        self._skill_result_repository = skill_result_repository
    
    async def generate_performance_insights(self, assessment: Assessment) -> Dict[str, Any]:
        """Genera insights de rendimiento de una evaluación"""
        if not assessment.is_complete():
            raise ValueError("Assessment must be completed to generate insights")
        
        skill_results = assessment.skill_results
        
        # Calcular métricas básicas
        total_questions = sum(sr.questions_answered for sr in skill_results)
        total_correct = sum(sr.correct_answers for sr in skill_results)
        overall_accuracy = (total_correct / total_questions * 100) if total_questions > 0 else 0
        
        # Identificar fortalezas y debilidades
        strongest_skills = sorted(
            skill_results, 
            key=lambda sr: sr.accuracy_percentage.value, 
            reverse=True
        )[:3]
        
        weakest_skills = sorted(
            skill_results, 
            key=lambda sr: sr.accuracy_percentage.value
        )[:3]
        
        # Calcular tiempo promedio por pregunta
        avg_time_per_question = 0
        if assessment.completion_time and total_questions > 0:
            avg_time_per_question = (assessment.completion_time.minutes * 60) / total_questions
        
        return {
            'overall_accuracy': overall_accuracy,
            'total_questions': total_questions,
            'total_correct': total_correct,
            'strongest_skills': [sr.skill_type.value for sr in strongest_skills],
            'weakest_skills': [sr.skill_type.value for sr in weakest_skills],
            'completion_time_minutes': assessment.completion_time.minutes if assessment.completion_time else 0,
            'average_time_per_question_seconds': avg_time_per_question,
            'proficiency_distribution': self._calculate_proficiency_distribution(skill_results),
            'recommended_focus_areas': [sr.skill_type.value for sr in weakest_skills[:2]]
        }
    
    def _calculate_proficiency_distribution(self, skill_results: List[SkillResult]) -> Dict[str, int]:
        """Calcula la distribución de niveles de competencia"""
        distribution = {
            ProficiencyLevel.BEGINNER.value: 0,
            ProficiencyLevel.INTERMEDIATE.value: 0,
            ProficiencyLevel.ADVANCED.value: 0,
            ProficiencyLevel.EXPERT.value: 0
        }
        
        for result in skill_results:
            distribution[result.proficiency_level.value] += 1
        
        return distribution
    
    async def calculate_benchmark_comparison(
        self, 
        assessment: Assessment
    ) -> Dict[str, Any]:
        """Compara el rendimiento con benchmarks globales"""
        # En una implementación real, esto consultaría estadísticas globales
        # Por ahora retornamos datos simulados
        
        overall_score = assessment.overall_score.value if assessment.overall_score else 0
        
        # Simular percentiles
        percentile = min(95, max(5, int(overall_score * 1.2)))  # Rough approximation
        
        return {
            'user_score': overall_score,
            'global_average': 72.5,
            'percentile_ranking': percentile,
            'performance_tier': self._determine_performance_tier(percentile),
            'users_outperformed_percentage': percentile
        }
    
    def _determine_performance_tier(self, percentile: int) -> str:
        """Determina el tier de rendimiento basado en percentil"""
        if percentile >= 90:
            return 'exceptional'
        elif percentile >= 75:
            return 'above_average'
        elif percentile >= 50:
            return 'average'
        elif percentile >= 25:
            return 'below_average'
        else:
            return 'needs_improvement'
