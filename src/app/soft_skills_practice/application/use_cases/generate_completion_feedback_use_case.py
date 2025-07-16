from typing import List, Dict, Any
from datetime import datetime
from ..dtos.simulation_dtos import (
    CompletionFeedbackDTO, 
    PerformanceMetricsDTO, 
    SkillAssessmentDTO
)
from ...infrastructure.persistence.repositories.simulation_session_repository import SimulationSessionRepository
from ...infrastructure.persistence.repositories.simulation_step_repository import SimulationStepRepository
from ...infrastructure.persistence.repositories.scenario_repository import ScenarioRepository
from ..services.gemini_service import GeminiService


class GenerateCompletionFeedbackUseCase:
    def __init__(
        self,
        simulation_session_repository: SimulationSessionRepository,
        simulation_step_repository: SimulationStepRepository,
        scenario_repository: ScenarioRepository,
        gemini_service: GeminiService
    ):
        self.simulation_session_repository = simulation_session_repository
        self.simulation_step_repository = simulation_step_repository
        self.scenario_repository = scenario_repository
        self.gemini_service = gemini_service
    
    async def execute(self, session_id: str) -> CompletionFeedbackDTO:

        try:
          
            session = await self.simulation_session_repository.find_by_session_id(session_id)
            if not session:
                raise ValueError(f"Sesión {session_id} no encontrada")
            
            scenario = await self.scenario_repository.find_by_id(session.scenario_id)
            if not scenario:
                raise ValueError(f"Escenario {session.scenario_id} no encontrado")
            
            steps = await self.simulation_step_repository.find_by_session_id(session_id)
            steps.sort(key=lambda x: x.step_number)
            
            
            performance = self._calculate_performance_metrics(session, steps)
            
            
            skill_assessments = await self._generate_skill_assessments(session, steps, scenario)
            
            
            overall_feedback = await self._generate_overall_feedback(session, steps, scenario, performance)
            
            
            achievements = self._identify_key_achievements(steps, performance)
            learnings = self._extract_main_learnings(steps)
            
            
            recommendations = await self._generate_next_steps_recommendations(session, performance, skill_assessments)
            
            
            percentile = self._calculate_percentile_ranking(performance.overall_score)
            
            
            certificate_earned = performance.overall_score >= 80.0
            badge_unlocked = self._check_badge_unlock(performance, skill_assessments)
            
            return CompletionFeedbackDTO(
                session_id=session_id,
                user_id=session.user_id,
                scenario_title=scenario.title,
                skill_type=session.skill_type,
                completion_status="completed" if performance.completion_percentage >= 100 else "partially_completed",
                performance=performance,
                skill_assessments=skill_assessments,
                overall_feedback=overall_feedback,
                key_achievements=achievements,
                main_learnings=learnings,
                next_steps_recommendations=recommendations,
                percentile_ranking=percentile,
                completed_at=datetime.utcnow(),
                certificate_earned=certificate_earned,
                badge_unlocked=badge_unlocked
            )
            
        except Exception as e:
            raise Exception(f"Error al generar feedback de finalización: {str(e)}")
    
    def _calculate_performance_metrics(self, session, steps) -> PerformanceMetricsDTO:
        """Calcular métricas de rendimiento"""
        completed_steps = [s for s in steps if s.content.user_response]
        
        
        scores = [s.evaluation.step_score for s in steps if s.evaluation and s.evaluation.step_score]
        average_step_score = sum(scores) / len(scores) if scores else 0
        overall_score = min(100, average_step_score * 1.2)  # Boost por completar
        
        
        total_time = self._calculate_total_time_minutes(session, steps)
        response_times = [s.interaction_tracking.time_to_respond for s in steps 
                         if s.interaction_tracking and s.interaction_tracking.time_to_respond]
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        
        
        help_requests = len([s for s in steps if s.interaction_tracking and s.interaction_tracking.help_requested])
        
        
        completion_percentage = (len(completed_steps) / session.total_steps) * 100 if session.total_steps > 0 else 0
        
        
        confidence_level = self._calculate_confidence_level(steps, avg_response_time)
        
        return PerformanceMetricsDTO(
            overall_score=round(overall_score, 1),
            average_step_score=round(average_step_score, 1),
            total_time_minutes=total_time,
            average_response_time_seconds=round(avg_response_time, 1),
            help_requests_count=help_requests,
            completion_percentage=round(completion_percentage, 1),
            confidence_level=confidence_level
        )
    
    async def _generate_skill_assessments(self, session, steps, scenario) -> List[SkillAssessmentDTO]:
        """Generar evaluación detallada por habilidad"""
        skill_assessments = []
        
        
        skill_data = {}
        for step in steps:
            if step.evaluation and step.evaluation.criteria_scores:
                for skill, score in step.evaluation.criteria_scores.items():
                    if skill not in skill_data:
                        skill_data[skill] = {
                            'scores': [],
                            'strengths': [],
                            'improvements': [],
                            'feedback': []
                        }
                    
                    skill_data[skill]['scores'].append(score)
                    if step.evaluation.strengths:
                        skill_data[skill]['strengths'].extend(step.evaluation.strengths)
                    if step.evaluation.areas_for_improvement:
                        skill_data[skill]['improvements'].extend(step.evaluation.areas_for_improvement)
                    if step.evaluation.specific_feedback:
                        skill_data[skill]['feedback'].append(step.evaluation.specific_feedback)
        
        
        for skill_name, data in skill_data.items():
            avg_score = sum(data['scores']) / len(data['scores']) if data['scores'] else 0
            level = self._determine_skill_level(avg_score)
            
           
            unique_strengths = list(set(data['strengths']))[:3] 
            unique_improvements = list(set(data['improvements']))[:3]
            
            
            specific_feedback = await self._generate_skill_specific_feedback(
                skill_name, avg_score, unique_strengths, unique_improvements
            )
            
            skill_assessments.append(SkillAssessmentDTO(
                skill_name=skill_name,
                score=round(avg_score, 1),
                level=level,
                strengths=unique_strengths,
                areas_for_improvement=unique_improvements,
                specific_feedback=specific_feedback
            ))
        
        return skill_assessments
    
    async def _generate_overall_feedback(self, session, steps, scenario, performance) -> str:
        """Generar feedback general usando IA"""
        try:
        
            completed_steps = len([s for s in steps if s.content.user_response])
            user_responses = [s.content.user_response for s in steps if s.content.user_response]
            
            prompt = f"""
            Genera un feedback motivacional y constructivo para un usuario que completó una simulación de soft skills.

            CONTEXTO:
            - Habilidad practicada: {session.skill_type}
            - Escenario: {scenario.title}
            - Pasos completados: {completed_steps}/{session.total_steps}
            - Puntuación general: {performance.overall_score}/100
            - Tiempo total: {performance.total_time_minutes} minutos
            - Nivel de confianza: {performance.confidence_level}

            INSTRUCCIONES:
            1. Comienza reconociendo el esfuerzo y logros del usuario
            2. Destaca los aspectos más positivos de su desempeño
            3. Menciona áreas de crecimiento de manera constructiva
            4. Termina con motivación para continuar desarrollando la habilidad
            5. Usa un tono profesional pero cálido
            6. Máximo 200 palabras

            El feedback debe ser específico al contexto IT y soft skills profesionales.
            """
            
            feedback = await self.gemini_service.generate_content(prompt)
            return feedback[:500]  # Limitar longitud
            
        except Exception as e:
            # Fallback si falla la IA
            return self._generate_fallback_feedback(performance, session.skill_type)
    
    def _identify_key_achievements(self, steps, performance) -> List[str]:
        """Identificar logros clave basados en el desempeño"""
        achievements = []
        
        if performance.overall_score >= 90:
            achievements.append("🏆 Excelente desempeño - Puntuación superior al 90%")
        elif performance.overall_score >= 80:
            achievements.append("🎯 Muy buen desempeño - Puntuación superior al 80%")
        elif performance.overall_score >= 70:
            achievements.append("✅ Buen desempeño - Cumpliste los objetivos básicos")
        
        if performance.completion_percentage >= 100:
            achievements.append("🚀 Completaste toda la simulación exitosamente")
        
        if performance.help_requests_count == 0:
            achievements.append("💪 Resolviste todos los desafíos sin solicitar ayuda")
        
        if performance.average_response_time_seconds < 60:
            achievements.append("⚡ Respuestas rápidas y decisivas")
        
        if performance.confidence_level == "high":
            achievements.append("🎪 Demostraste alta confianza en tus respuestas")
        
        return achievements[:4]  
    
    def _extract_main_learnings(self, steps) -> List[str]:
        """Extraer aprendizajes principales de los feedbacks"""
        learnings = []
        
        
        for step in steps:
            if step.content.ai_feedback:
                
                feedback = step.content.ai_feedback.lower()
                if "importante" in feedback or "clave" in feedback:
                    
                    sentences = step.content.ai_feedback.split('.')
                    for sentence in sentences:
                        if "importante" in sentence.lower() or "clave" in sentence.lower():
                            learnings.append(sentence.strip())
                            break
        
        
        if len(learnings) < 2:
            learnings.extend([
                "La comunicación efectiva requiere claridad y empatía",
                "Tomar tiempo para reflexionar mejora la calidad de las decisiones"
            ])
        
        return learnings[:3]  
    
    async def _generate_next_steps_recommendations(self, session, performance, skill_assessments) -> List[str]:
        """Generar recomendaciones personalizadas"""
        recommendations = []
        
        
        if performance.overall_score < 70:
            recommendations.append(f"Practica más escenarios de {session.skill_type} para fortalecer las bases")
        elif performance.overall_score < 85:
            recommendations.append(f"Busca situaciones más complejas de {session.skill_type} para el siguiente nivel")
        else:
            recommendations.append(f"Considera convertirte en mentor en {session.skill_type}")
        
        
        for assessment in skill_assessments:
            if assessment.score < 70:
                recommendations.append(f"Enfócate en mejorar: {assessment.skill_name}")
        
        
        if performance.average_response_time_seconds > 120:
            recommendations.append("Practica tomar decisiones más rápidas en situaciones similares")
        
       
        if performance.help_requests_count > 2:
            recommendations.append("Construye más confianza practicando escenarios similares")
        
        return recommendations[:4]  
    
    
    def _calculate_total_time_minutes(self, session, steps) -> int:
        """Calcular tiempo total en minutos"""
        if not steps:
            return 0
        
        start_time = session.session_metadata.started_at
        end_time = max(step.created_at for step in steps)
        return max(1, int((end_time - start_time).total_seconds() / 60))
    
    def _calculate_confidence_level(self, steps, avg_response_time) -> str:
        """Calcular nivel de confianza basado en respuestas"""
        confidence_keywords = 0
        total_responses = 0
        
        for step in steps:
            if step.content.user_response:
                total_responses += 1
                response = step.content.user_response.lower()
                if any(word in response for word in ["seguro", "confío", "definitivamente", "claramente"]):
                    confidence_keywords += 1
        
        confidence_ratio = confidence_keywords / total_responses if total_responses > 0 else 0
        
        if confidence_ratio > 0.3 and avg_response_time < 90:
            return "high"
        elif confidence_ratio > 0.1 or avg_response_time < 120:
            return "medium"
        else:
            return "low"
    
    def _determine_skill_level(self, score: float) -> str:
        """Determinar nivel de habilidad basado en puntuación"""
        if score >= 85:
            return "advanced"
        elif score >= 70:
            return "intermediate"
        else:
            return "beginner"
    
    def _calculate_percentile_ranking(self, score: float) -> int:
        """Calcular percentil (simplificado)"""
       
        if score >= 90:
            return 95
        elif score >= 80:
            return 80
        elif score >= 70:
            return 65
        elif score >= 60:
            return 50
        else:
            return 30
    
    def _check_badge_unlock(self, performance, skill_assessments) -> str:
        """Verificar si se desbloqueó algún badge"""
        if performance.overall_score >= 95:
            return "Expert Communicator"
        elif performance.overall_score >= 85 and performance.help_requests_count == 0:
            return "Independent Problem Solver"
        elif performance.completion_percentage >= 100 and performance.average_response_time_seconds < 60:
            return "Quick Decision Maker"
        else:
            return None
    
    async def _generate_skill_specific_feedback(self, skill_name, score, strengths, improvements) -> str:
        """Generar feedback específico para una habilidad"""
        try:
            prompt = f"""
            Genera un feedback específico y constructivo para la habilidad de {skill_name}.

            DATOS:
            - Puntuación: {score}/100
            - Fortalezas: {', '.join(strengths) if strengths else 'No identificadas'}
            - Áreas de mejora: {', '.join(improvements) if improvements else 'No identificadas'}

            INSTRUCCIONES:
            1. Máximo 100 palabras
            2. Tono profesional y constructivo
            3. Enfoque en acciones específicas para mejorar
            4. Reconoce fortalezas identificadas
            """
            
            feedback = await self.gemini_service.generate_content(prompt)
            return feedback[:200]
            
        except Exception:
            return f"Tu desempeño en {skill_name} muestra potencial de crecimiento. Continúa practicando para mejorar tus habilidades."
    
    def _generate_fallback_feedback(self, performance, skill_type) -> str:
        """Feedback de respaldo si falla la IA"""
        score = performance.overall_score
        
        if score >= 80:
            return f"¡Excelente trabajo! Has demostrado un sólido dominio de {skill_type}. Tu puntuación de {score}/100 refleja tu capacidad para manejar situaciones profesionales complejas. Continúa desarrollando estas habilidades para alcanzar un nivel de expertise."
        elif score >= 60:
            return f"Buen progreso en {skill_type}. Has completado la simulación con una puntuación de {score}/100, lo que indica un entendimiento sólido de los conceptos clave. Hay oportunidades para mejorar y refinar tus habilidades con más práctica."
        else:
            return f"Has completado la simulación de {skill_type} con dedicación. Tu puntuación de {score}/100 muestra que estás en proceso de desarrollo. Te recomendamos revisar los conceptos fundamentales y practicar más escenarios similares."
