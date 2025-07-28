#!/usr/bin/env python3
"""
Test script to debug assessment questions
"""
import asyncio
import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from app.soft_skills_practice.infrastructure.persistence.models.assessment_models import AssessmentQuestion
from app.soft_skills_practice.infrastructure.persistence.repositories.assessment_repositories import AssessmentQuestionRepository
from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient

async def test_questions():
    """Test loading questions from database"""
    try:
        # Connect to MongoDB
        client = AsyncIOMotorClient("mongodb://admin:ELTopn4590@3.217.49.154/soft_skills_practice?authSource=admin")
        
        # Initialize Beanie
        await init_beanie(
            database=client.soft_skills_practice,
            document_models=[AssessmentQuestion]
        )
        
        print("🔗 Connected to MongoDB")
        
        # Test repository
        repo = AssessmentQuestionRepository()
        
        # Get all questions
        all_questions = await AssessmentQuestion.find().to_list()
        print(f"📊 Total questions in database: {len(all_questions)}")
        
        if all_questions:
            sample_question = all_questions[0]
            print(f"\n📝 Sample question structure:")
            print(f"  question_id: {getattr(sample_question, 'question_id', 'MISSING')}")
            print(f"  skill_type: {getattr(sample_question, 'skill_type', 'MISSING')}")
            print(f"  skill_name: {getattr(sample_question, 'skill_name', 'MISSING')}")
            print(f"  scenario_text: {getattr(sample_question, 'scenario_text', 'MISSING')[:50]}...")
            print(f"  options count: {len(getattr(sample_question, 'options', []))}")
            
            # Test get_random_questions_by_skills method
            skill_types = ["active_listening", "public_speaking"]
            random_questions = await repo.get_random_questions_by_skills(skill_types, 2)
            print(f"\n🎲 Random questions for {skill_types}: {len(random_questions)}")
            
            for q in random_questions:
                print(f"  - {q.skill_type}: {q.question_text[:50]}...")
        
        print("\n✅ Test completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_questions())
