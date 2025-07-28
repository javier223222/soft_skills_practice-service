#!/usr/bin/env python3
"""
Simple test for DTOs
"""
import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_dtos():
    """Test creating DTOs"""
    try:
        from app.soft_skills_practice.application.dtos.initial_assessment_dtos import (
            InitialAssessmentRequestDTO,
            InitialAssessmentQuestionDTO
        )
        
        print("🔗 Testing DTO imports...")
        
        # Test request DTO
        request = InitialAssessmentRequestDTO(
            user_id="test_user_12345",
            technical_specialization="Software Development",
            seniority_level="mid",
            preferred_language="english"
        )
        print(f"✅ Request DTO created: {request.user_id}")
        
        # Test question DTO
        question = InitialAssessmentQuestionDTO(
            question_id="test_q_123",
            skill_type="active_listening",
            skill_name="Active Listening",
            scenario_text="Test scenario",
            question_text="Test question?",
            options=[
                {"id": "A", "text": "Option A"},
                {"id": "B", "text": "Option B"}
            ],
            correct_answer_id="",
            difficulty_level=3,
            explanation=""
        )
        print(f"✅ Question DTO created: {question.skill_type}")
        
        print("✅ DTO test completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during DTO test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_dtos()
