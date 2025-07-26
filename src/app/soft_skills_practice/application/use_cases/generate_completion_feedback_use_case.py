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
                raise ValueError(f"Session {session_id} not found")
            
            scenario = await self.scenario_repository.find_by_id(session.scenario_id)
            if not scenario:
                raise ValueError(f"Scenario {session.scenario_id} not found")
            
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
            raise Exception(f"Error generating completion feedback: {str(e)}")
    
    def _calculate_performance_metrics(self, session, steps) -> PerformanceMetricsDTO:
        """Calculate performance metrics"""
        completed_steps = [s for s in steps if s.content.user_response]
        
        
        scores = [s.evaluation.step_score for s in steps if s.evaluation and s.evaluation.step_score]
        average_step_score = sum(scores) / len(scores) if scores else 0
        overall_score = min(100, average_step_score * 1.2)  
        
        
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
        """Generate detailed evaluation by skill"""
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
        """Generate general feedback using AI"""
        try:
        
            completed_steps = len([s for s in steps if s.content.user_response])
            user_responses = [s.content.user_response for s in steps if s.content.user_response]
            
            prompt = f"""
            Generate motivational and constructive feedback for a user who completed a soft skills simulation.

            CONTEXT:
            - Practiced skill: {session.skill_type}
            - Scenario: {scenario.title}
            - Steps completed: {completed_steps}/{session.total_steps}
            - Overall score: {performance.overall_score}/100
            - Total time: {performance.total_time_minutes} minutes
            - Confidence level: {performance.confidence_level}

            INSTRUCTIONS:
            1. Start by recognizing the user's effort and achievements
            2. Highlight the most positive aspects of their performance
            3. Mention areas for growth in a constructive way
            4. End with motivation to continue developing the skill
            5. Use a professional yet warm tone
            6. Maximum 200 words

            The feedback should be specific to the IT context and professional soft skills.
            """
            
            feedback = await self.gemini_service.generate_content(prompt)
            return feedback[:500]  # Limit length
            
        except Exception as e:
            raise Exception(f"Error generating general feedback: {str(e)}")
    
    def _identify_key_achievements(self, steps, performance) -> List[str]:
        """Identify key achievements based on performance"""
        achievements = []
        
        if performance.overall_score >= 90:
            achievements.append("Excellent performance - Score above 90%")
        elif performance.overall_score >= 80:
            achievements.append("Very good performance - Score above 80%")
        elif performance.overall_score >= 70:
            achievements.append("Good performance - You met the basic objectives")
        
        if performance.completion_percentage >= 100:
            achievements.append("You successfully completed the entire simulation")
        
        if performance.help_requests_count == 0:
            achievements.append("You solved all challenges without requesting help")
        
        if performance.average_response_time_seconds < 60:
            achievements.append("Quick and decisive responses")
        
        if performance.confidence_level == "high":
            achievements.append("You demonstrated high confidence in your answers")
        
        return achievements[:4]  
    def _extract_main_learnings(self, steps) -> List[str]:
        
        learnings = []
        
        # Extract key learnings
        for step in steps:
            if step.content.ai_feedback:
                # Look for important insights in feedback
                feedback = step.content.ai_feedback.lower()
                if "important" in feedback or "key" in feedback:
                    # Extract the sentence containing the learning
                    sentences = step.content.ai_feedback.split('.')
                    for sentence in sentences:
                        if "important" in sentence.lower() or "key" in sentence.lower():
                            learnings.append(sentence.strip())
                            break
        
        # Default learnings if none found
        if len(learnings) < 2:
            learnings.extend([
                "Effective communication requires clarity and empathy",
                "Taking time to reflect improves decision quality"
            ])
        
        return learnings[:3]  
    
    async def _generate_next_steps_recommendations(self, session, performance, skill_assessments) -> List[str]:
        """Generate personalized recommendations"""
        recommendations = []
        
        # Score-based recommendations
        if performance.overall_score < 70:
            recommendations.append(f"Practice more {session.skill_type} scenarios to strengthen fundamentals")
        elif performance.overall_score < 85:
            recommendations.append(f"Seek more complex {session.skill_type} situations for the next level")
        else:
            recommendations.append(f"Consider becoming a mentor in {session.skill_type}")
        
        # Skill-specific recommendations
        for assessment in skill_assessments:
            if assessment.score < 70:
                recommendations.append(f"Focus on improving: {assessment.skill_name}")
        
        # Response time recommendations
        if performance.average_response_time_seconds > 120:
            recommendations.append("Practice making faster decisions in similar situations")
        
        # Help request recommendations
        if performance.help_requests_count > 2:
            recommendations.append("Build more confidence by practicing similar scenarios")
        
        return recommendations[:4]  
    
    
    def _calculate_total_time_minutes(self, session, steps) -> int:
        """Calculate total time in minutes"""
        if not steps:
            return 0
        
        start_time = session.session_metadata.started_at
        end_time = max(step.created_at for step in steps)
        return max(1, int((end_time - start_time).total_seconds() / 60))
    
    def _calculate_confidence_level(self, steps, avg_response_time) -> str:
        """Calculate confidence level based on responses"""
        confidence_keywords = 0
        total_responses = 0
        
        for step in steps:
            if step.content.user_response:
                total_responses += 1
                response = step.content.user_response.lower()
                if any(word in response for word in ["sure", "confident", "definitely", "clearly"]):
                    confidence_keywords += 1
        
        confidence_ratio = confidence_keywords / total_responses if total_responses > 0 else 0
        
        if confidence_ratio > 0.3 and avg_response_time < 90:
            return "high"
        elif confidence_ratio > 0.1 or avg_response_time < 120:
            return "medium"
        else:
            return "low"
    
    def _determine_skill_level(self, score: float) -> str:
        """Determine skill level based on score"""
        if score >= 85:
            return "advanced"
        elif score >= 70:
            return "intermediate"
        else:
            return "beginner"
    
    def _calculate_percentile_ranking(self, score: float) -> int:
        """Calculate percentile (simplified)"""
        # Simplified percentile calculation based on score
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
        """Check if any badge was unlocked"""
        if performance.overall_score >= 95:
            return "Expert Communicator"
        elif performance.overall_score >= 85 and performance.help_requests_count == 0:
            return "Independent Problem Solver"
        elif performance.completion_percentage >= 100 and performance.average_response_time_seconds < 60:
            return "Quick Decision Maker"
        else:
            return None
    
    async def _generate_skill_specific_feedback(self, skill_name, score, strengths, improvements) -> str:
        """Generate specific feedback for a skill"""
        try:
            prompt = f"""
            Generate specific and constructive feedback for the skill of {skill_name}.

            DATA:
            - Score: {score}/100
            - Strengths: {', '.join(strengths) if strengths else 'None identified'}
            - Areas for improvement: {', '.join(improvements) if improvements else 'None identified'}

            INSTRUCTIONS:
            1. Maximum 100 words
            2. Professional and constructive tone
            3. Focus on specific actions to improve
            4. Acknowledge identified strengths
            """
            
            feedback = await self.gemini_service.generate_content(prompt)
            return feedback[:200]
            
        except Exception:
            return f"Your performance in {skill_name} shows growth potential. Continue practicing to improve your skills."
    
    def _generate_fallback_feedback(self, performance, skill_type) -> str:
        """Fallback feedback if AI fails"""
        score = performance.overall_score
        
        if score >= 80:
            return f"Excellent work! You have demonstrated solid mastery of {skill_type}. Your score of {score}/100 reflects your ability to handle complex professional situations. Continue developing these skills to reach expert level."
        elif score >= 60:
            return f"Good progress in {skill_type}. You completed the simulation with a score of {score}/100, indicating solid understanding of key concepts. There are opportunities to improve and refine your skills with more practice."
        else:
            return f"You completed the {skill_type} simulation with dedication. Your score of {score}/100 shows you are in development process. We recommend reviewing fundamental concepts and practicing more similar scenarios."
