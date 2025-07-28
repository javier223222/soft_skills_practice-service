from typing import List, Optional
from beanie import PydanticObjectId
from ..models.assessment_models import AssessmentQuestion, InitialAssessment
import random

class AssessmentQuestionRepository:
    """Repository for assessment questions"""
    
    async def find_by_skill_type(self, skill_type: str) -> List[AssessmentQuestion]:
        """Find questions by skill type"""
        return await AssessmentQuestion.find(
            AssessmentQuestion.skill_type == skill_type
        ).to_list()
    
    async def find_by_skill_types(self, skill_types: List[str]) -> List[AssessmentQuestion]:
        """Find questions for multiple skill types"""
        return await AssessmentQuestion.find(
            {"skill_type": {"$in": skill_types}}
        ).to_list()
    
    async def get_random_questions_by_skills(
        self, 
        skill_types: List[str], 
        questions_per_skill: int = 2
    ) -> List[AssessmentQuestion]:
        """Get random questions for each skill type"""
        all_questions = []
        
        for skill_type in skill_types:
            skill_questions = await self.find_by_skill_type(skill_type)
            if skill_questions:
                # Select random questions for this skill
                selected = random.sample(
                    skill_questions, 
                    min(questions_per_skill, len(skill_questions))
                )
                all_questions.extend(selected)
        
        # Shuffle the final list
        random.shuffle(all_questions)
        return all_questions
    
    async def find_by_id(self, question_id: str) -> Optional[AssessmentQuestion]:
        """Find question by ID"""
        return await AssessmentQuestion.find_one(
            AssessmentQuestion.question_id == question_id
        )
    
    async def create(self, question: AssessmentQuestion) -> AssessmentQuestion:
        """Create new assessment question"""
        return await question.insert()
    
    async def update_usage_stats(self, question_id: str, was_correct: bool):
        """Update question usage statistics"""
        question = await self.find_by_id(question_id)
        if question:
            question.usage_count += 1
            if question.usage_count == 1:
                question.success_rate = 100.0 if was_correct else 0.0
            else:
                # Update success rate using running average
                current_successes = (question.success_rate / 100.0) * (question.usage_count - 1)
                if was_correct:
                    current_successes += 1
                question.success_rate = (current_successes / question.usage_count) * 100.0
            
            await question.save()

class InitialAssessmentRepository:
    """Repository for initial assessments"""
    
    async def create(self, assessment: InitialAssessment) -> InitialAssessment:
        """Create new assessment"""
        return await assessment.insert()
    
    async def find_by_assessment_id(self, assessment_id: str) -> Optional[InitialAssessment]:
        """Find assessment by ID"""
        return await InitialAssessment.find_one(
            InitialAssessment.assessment_id == assessment_id
        )
    
    async def find_by_user_id(self, user_id: str) -> List[InitialAssessment]:
        """Find assessments by user ID"""
        return await InitialAssessment.find(
            InitialAssessment.user_id == user_id
        ).sort("-started_at").to_list()
    
    async def find_latest_by_user_id(self, user_id: str) -> Optional[InitialAssessment]:
        """Find latest assessment by user ID"""
        assessments = await self.find_by_user_id(user_id)
        return assessments[0] if assessments else None
    
    async def update(self, assessment: InitialAssessment) -> InitialAssessment:
        """Update assessment"""
        await assessment.save()
        return assessment
    
    async def find_completed_assessments(self) -> List[InitialAssessment]:
        """Find all completed assessments for analytics"""
        return await InitialAssessment.find(
            InitialAssessment.status == "completed"
        ).to_list()
    
    async def get_user_assessment_history(self, user_id: str, limit: int = 10) -> List[InitialAssessment]:
        """Get user's assessment history"""
        return await InitialAssessment.find(
            InitialAssessment.user_id == user_id
        ).sort("-started_at").limit(limit).to_list()
