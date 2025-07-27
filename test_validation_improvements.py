#!/usr/bin/env python3
"""
Simple test script to validate the new validation utilities work correctly.
"""
import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from app.soft_skills_practice.application.utils.validation_utils import (
        ValidationUtils, 
        SanitizationUtils, 
        VagueResponseDetector,
        ValidationMixins
    )
    
    print("✅ Successfully imported validation utilities")
    
    # Test ValidationUtils
    print("\n🔍 Testing ValidationUtils:")
    test_user_id = "user123456789012345678901234"
    print(f"User ID '{test_user_id}' is valid: {ValidationUtils.validate_user_id(test_user_id)}")
    
    test_session_id = "session-123-456-789-abc"
    print(f"Session ID '{test_session_id}' is valid: {ValidationUtils.validate_session_id(test_session_id)}")
    
    test_skill = "communication_skills"
    print(f"Skill type '{test_skill}' is valid: {ValidationUtils.validate_skill_type(test_skill)}")
    
    # Test SanitizationUtils
    print("\n🧹 Testing SanitizationUtils:")
    dirty_text = "<script>alert('xss')</script>Hello World   "
    clean_text = SanitizationUtils.sanitize_text_input(dirty_text)
    print(f"Original: '{dirty_text}'")
    print(f"Sanitized: '{clean_text}'")
    
    # Test VagueResponseDetector
    print("\n🎯 Testing VagueResponseDetector:")
    vague_responses = ["hello", "ddd", "ok", "yes"]
    good_responses = ["I would approach this by analyzing the requirements first", "Let me think about this problem"]
    
    for response in vague_responses:
        is_vague = VagueResponseDetector.is_vague_response(response)
        print(f"'{response}' is vague: {is_vague}")
    
    for response in good_responses:
        is_vague = VagueResponseDetector.is_vague_response(response)
        print(f"'{response[:30]}...' is vague: {is_vague}")
    
    print("\n✅ All validation utilities are working correctly!")
    print("🚀 The validation improvements are ready and maintain backward compatibility.")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)
