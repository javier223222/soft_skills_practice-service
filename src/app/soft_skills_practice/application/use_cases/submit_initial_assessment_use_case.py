from typing import List, Dict, Any
from datetime import datetime, timezone
from ..dtos.initial_assessment_dtos import (
    InitialAssessmentSubmissionDTO,
    InitialAssessmentResultDTO,
    SkillAssessmentResultDTO
)
from ...infrastructure.persistence.repositories.assessment_repositories import (
    AssessmentQuestionRepository,
    InitialAssessmentRepository
)
from ...infrastructure.persistence.models.assessment_models import (
    AssessmentStatus,
    ProficiencyLevel,
    UserAssessmentAnswer,
    SkillAssessmentResult
)
from ..utils.validation_utils import ValidationUtils

class SubmitInitialAssessmentUseCase:
    """Use case for submitting and evaluating initial assessment"""
    
    def __init__(
        self,
        assessment_question_repository: AssessmentQuestionRepository,
        initial_assessment_repository: InitialAssessmentRepository
    ):
        self.assessment_question_repository = assessment_question_repository
        self.initial_assessment_repository = initial_assessment_repository
    
    async def execute(self, submission: InitialAssessmentSubmissionDTO) -> InitialAssessmentResultDTO:
        """Process assessment submission and generate results"""
        try:
            # Find the assessment
            assessment = await self.initial_assessment_repository.find_by_assessment_id(
                submission.assessment_id
            )
            
            if not assessment:
                raise ValueError("Assessment not found")
            
            if assessment.status == AssessmentStatus.COMPLETED:
                raise ValueError("Assessment already completed")
            
            # Process answers and calculate results
            processed_answers = await self._process_answers(assessment, submission.answers)
            skill_results = await self._calculate_skill_results(processed_answers)
            overall_score = self._calculate_overall_score(skill_results)
            
            # Analyze strengths and weaknesses
            analysis = self._analyze_results(skill_results)
            
            # Update assessment with results
            assessment.answers = processed_answers
            assessment.skill_results = skill_results
            assessment.overall_score = overall_score
            assessment.completion_time_minutes = submission.total_time_minutes
            assessment.weakest_skills = analysis["weakest_skills"]
            assessment.strongest_skills = analysis["strongest_skills"]
            assessment.recommended_learning_path = analysis["learning_path"]
            assessment.next_steps = analysis["next_steps"]
            assessment.status = AssessmentStatus.COMPLETED
            assessment.completed_at = datetime.now(timezone.utc)
            assessment.updated_at = datetime.now(timezone.utc)
            
            await self.initial_assessment_repository.update(assessment)
            
            # Convert to response DTO
            return InitialAssessmentResultDTO(
                assessment_id=assessment.assessment_id,
                user_id=assessment.user_id,
                overall_score=overall_score,
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
                    for sr in skill_results
                ],
                weakest_skills=assessment.weakest_skills,
                strongest_skills=assessment.strongest_skills,
                recommended_learning_path=assessment.recommended_learning_path,
                next_steps=assessment.next_steps,
                completed_at=assessment.completed_at
            )
            
        except Exception as e:
            raise Exception(f"Error submitting assessment: {str(e)}")
    
    async def _process_answers(self, assessment, answers) -> List[UserAssessmentAnswer]:
        """Process user answers and determine correctness"""
        processed_answers = []
        
        for answer in answers:
            # Find the question
            question = await self.assessment_question_repository.find_by_id(answer.question_id)
            if not question:
                continue
            
            # Check if answer is correct
            is_correct = answer.selected_option_id == question.correct_answer_id
            
            processed_answer = UserAssessmentAnswer(
                question_id=answer.question_id,
                selected_option_id=answer.selected_option_id,
                is_correct=is_correct,
                time_taken_seconds=answer.time_taken_seconds
            )
            
            processed_answers.append(processed_answer)
            
            # Update question statistics
            await self.assessment_question_repository.update_usage_stats(
                answer.question_id, is_correct
            )
        
        return processed_answers
    
    async def _calculate_skill_results(self, answers: List[UserAssessmentAnswer]) -> List[SkillAssessmentResult]:
        """Calculate results for each skill"""
        skill_results = {}
        
        for answer in answers:
            question = await self.assessment_question_repository.find_by_id(answer.question_id)
            if not question:
                continue
            
            skill_type = question.skill_type
            if skill_type not in skill_results:
                skill_results[skill_type] = {
                    "skill_name": self._get_skill_display_name(skill_type),
                    "questions": [],
                    "correct": 0,
                    "total": 0
                }
            
            skill_results[skill_type]["questions"].append(answer)
            skill_results[skill_type]["total"] += 1
            if answer.is_correct:
                skill_results[skill_type]["correct"] += 1
        
        # Convert to SkillAssessmentResult objects
        results = []
        for skill_type, data in skill_results.items():
            accuracy = (data["correct"] / data["total"]) * 100 if data["total"] > 0 else 0
            proficiency = self._determine_proficiency_level(accuracy)
            
            result = SkillAssessmentResult(
                skill_type=skill_type,
                skill_name=data["skill_name"],
                questions_answered=data["total"],
                correct_answers=data["correct"],
                accuracy_percentage=accuracy,
                proficiency_level=proficiency,
                areas_for_improvement=self._get_improvement_areas(skill_type, accuracy),
                strengths=self._get_strengths(skill_type, accuracy),
                recommended_scenarios=self._get_recommended_scenarios(skill_type, proficiency)
            )
            
            results.append(result)
        
        return results
    
    def _calculate_overall_score(self, skill_results: List[SkillAssessmentResult]) -> float:
        """Calculate overall assessment score"""
        if not skill_results:
            return 0.0
        
        total_score = sum(sr.accuracy_percentage for sr in skill_results)
        return round(total_score / len(skill_results), 1)
    
    def _analyze_results(self, skill_results: List[SkillAssessmentResult]) -> Dict[str, Any]:
        """Analyze results to identify strengths, weaknesses, and recommendations"""
        # Sort by accuracy
        sorted_skills = sorted(skill_results, key=lambda x: x.accuracy_percentage)
        
        # Identify weakest (bottom 30%) and strongest (top 30%) skills
        total_skills = len(sorted_skills)
        weak_count = max(1, total_skills // 3)
        strong_count = max(1, total_skills // 3)
        
        weakest_skills = [skill.skill_type for skill in sorted_skills[:weak_count]]
        strongest_skills = [skill.skill_type for skill in sorted_skills[-strong_count:]]
        
        # Generate learning path
        learning_path = self._generate_learning_path(weakest_skills, strongest_skills)
        
        # Generate next steps
        next_steps = self._generate_next_steps(weakest_skills, strongest_skills)
        
        return {
            "weakest_skills": weakest_skills,
            "strongest_skills": strongest_skills,
            "learning_path": learning_path,
            "next_steps": next_steps
        }
    
    def _determine_proficiency_level(self, accuracy: float) -> ProficiencyLevel:
        """Determine proficiency level based on accuracy"""
        if accuracy >= 80:
            return ProficiencyLevel.ADVANCED
        elif accuracy >= 60:
            return ProficiencyLevel.INTERMEDIATE
        else:
            return ProficiencyLevel.BEGINNER
    
    def _get_skill_display_name(self, skill_type: str) -> str:
        """Get display name for skill type"""
        skill_names = {
            "communication": "Communication Skills",
            "leadership": "Leadership",
            "teamwork": "Teamwork & Collaboration",
            "problem_solving": "Problem Solving",
            "time_management": "Time Management",
            "emotional_intelligence": "Emotional Intelligence",
            "adaptability": "Adaptability",
            "conflict_resolution": "Conflict Resolution",
            "decision_making": "Decision Making",
            "critical_thinking": "Critical Thinking"
        }
        return skill_names.get(skill_type, skill_type.replace("_", " ").title())
    
    def _get_improvement_areas(self, skill_type: str, accuracy: float) -> List[str]:
        """Get areas for improvement based on skill and performance"""
        improvement_areas = {
            "communication": [
                "Active listening techniques",
                "Clear and concise messaging",
                "Non-verbal communication awareness",
                "Feedback delivery skills"
            ],
            "leadership": [
                "Team motivation strategies",
                "Decision-making confidence",
                "Delegation skills",
                "Vision communication"
            ],
            "teamwork": [
                "Collaborative planning",
                "Role clarity understanding",
                "Conflict management in teams",
                "Supporting team members"
            ],
            "problem_solving": [
                "Structured problem analysis",
                "Creative solution generation",
                "Risk assessment",
                "Implementation planning"
            ],
            "time_management": [
                "Priority setting techniques",
                "Task scheduling methods",
                "Deadline management",
                "Productivity optimization"
            ]
        }
        
        areas = improvement_areas.get(skill_type, ["General skill development"])
        # Return fewer areas if performance is good
        if accuracy >= 70:
            return areas[:2]
        else:
            return areas[:3]
    
    def _get_strengths(self, skill_type: str, accuracy: float) -> List[str]:
        """Get strengths based on skill and performance"""
        if accuracy < 50:
            return ["Shows willingness to learn", "Demonstrates self-awareness"]
        
        strengths = {
            "communication": [
                "Clear expression of ideas",
                "Understanding of communication principles",
                "Awareness of audience needs"
            ],
            "leadership": [
                "Leadership awareness",
                "Understanding of team dynamics",
                "Decision-making capabilities"
            ],
            "teamwork": [
                "Collaborative mindset",
                "Team-oriented thinking",
                "Supportive approach"
            ]
        }
        
        return strengths.get(skill_type, ["Good foundational understanding"])
    
    def _get_recommended_scenarios(self, skill_type: str, proficiency: ProficiencyLevel) -> List[str]:
        """Get recommended scenarios based on skill and proficiency"""
        scenarios = {
            "communication": ["team_presentation", "difficult_conversation", "feedback_session"],
            "leadership": ["team_crisis", "project_leadership", "performance_review"],
            "teamwork": ["cross_functional_project", "team_conflict", "remote_collaboration"]
        }
        
        skill_scenarios = scenarios.get(skill_type, [f"{skill_type}_basic", f"{skill_type}_intermediate"])
        
        # Adjust based on proficiency
        if proficiency == ProficiencyLevel.BEGINNER:
            return skill_scenarios[:1]  # Start with basics
        elif proficiency == ProficiencyLevel.INTERMEDIATE:
            return skill_scenarios[:2]  # Intermediate scenarios
        else:
            return skill_scenarios  # All scenarios
    
    def _generate_learning_path(self, weakest_skills: List[str], strongest_skills: List[str]) -> List[Dict[str, Any]]:
        """Generate recommended learning path"""
        path = []
        
        # Start with weakest skills
        for i, skill in enumerate(weakest_skills[:3], 1):
            path.append({
                "step": i,
                "skill_type": skill,
                "skill_name": self._get_skill_display_name(skill),
                "action": "Practice scenarios",
                "estimated_duration": "2-3 sessions",
                "priority": "high"
            })
        
        # Add intermediate skills
        for i, skill in enumerate(strongest_skills[-2:], len(path) + 1):
            if skill not in weakest_skills:  # Avoid duplicates
                path.append({
                    "step": i,
                    "skill_type": skill,
                    "skill_name": self._get_skill_display_name(skill),
                    "action": "Advanced practice",
                    "estimated_duration": "1-2 sessions",
                    "priority": "medium"
                })
        
        return path
    
    def _generate_next_steps(self, weakest_skills: List[str], strongest_skills: List[str]) -> List[str]:
        """Generate immediate next steps for the user"""
        steps = []
        
        if weakest_skills:
            primary_skill = self._get_skill_display_name(weakest_skills[0])
            steps.append(f"Start with {primary_skill} practice scenarios to build foundational skills")
        
        steps.extend([
            "Complete 2-3 practice sessions per week for optimal learning",
            "Focus on one skill at a time for deeper understanding",
            "Apply learned concepts in real workplace situations",
            "Track your progress and celebrate improvements"
        ])
        
        if strongest_skills:
            strong_skill = self._get_skill_display_name(strongest_skills[-1])
            steps.append(f"Leverage your {strong_skill} strength to support team members")
        
        return steps
