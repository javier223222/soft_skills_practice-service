#!/usr/bin/env python3
"""
Simple test for assessment use case
"""
import asyncio
import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from app.soft_skills_practice.infrastructure.persistence.database import DatabaseConnection
from app.soft_skills_practice.application.use_cases.start_initial_assessment_use_case import StartInitialAssessmentUseCase
from app.soft_skills_practice.infrastructure.persistence.repositories.assessment_repositories import (
    AssessmentQuestionRepository,
    InitialAssessmentRepository
)
from app.soft_skills_practice.application.dtos.initial_assessment_dtos import InitialAssessmentRequestDTO

async def test_use_case():
    """Test the start assessment use case"""
    try:
        # Connect to database
        db = DatabaseConnection()
        await db.connect()
        print("🔗 Connected to MongoDB")
        
        # Create repositories
        question_repo = AssessmentQuestionRepository()
        assessment_repo = InitialAssessmentRepository()
        
        # Create use case
        use_case = StartInitialAssessmentUseCase(question_repo, assessment_repo)
        
        # Create test request
        request = InitialAssessmentRequestDTO(
            user_id="test_user_12345",
            technical_specialization="Software Development",
            seniority_level="mid",
            preferred_language="english"
        )
        
        print("🚀 Testing start assessment use case...")
        
        # Execute use case
        result = await use_case.execute(request)
        
        print(f"✅ Assessment started successfully!")
        print(f"   Assessment ID: {result.assessment_id}")
        print(f"   Total questions: {result.total_questions}")
        print(f"   Estimated duration: {result.estimated_duration_minutes} minutes")
        print(f"   User ID: {result.user_id}")
        
        # Print sample questions
        if result.questions:
            print(f"\n📝 Sample questions:")
            for i, q in enumerate(result.questions[:2]):  # Show first 2 questions
                print(f"   {i+1}. Skill: {q.skill_type} ({q.skill_name})")
                print(f"      Question: {q.question_text[:60]}...")
                print(f"      Options: {len(q.options)}")
        
        print(f"\n✅ Test completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_use_case())
