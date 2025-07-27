"""
Utilities for input validation and sanitization
"""

import re
import html
from typing import Optional, List, Dict, Any
from pydantic import validator
import logging

logger = logging.getLogger(__name__)


class ValidationUtils:
    """Utilities for enhanced input validation"""
    
    # Regex patterns for common validations
    USER_ID_PATTERN = r'^[a-zA-Z0-9_-]{3,50}$'
    SESSION_ID_PATTERN = r'^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}$'
    SKILL_TYPE_PATTERN = r'^[a-zA-Z_]{3,30}$'
    
    # Dangerous patterns to filter
    DANGEROUS_PATTERNS = [
        '<script', 'javascript:', 'onload=', 'onerror=', 'onclick=',
        'eval(', 'setTimeout(', 'setInterval(', 'Function(',
        'document.', 'window.', 'alert(', 'confirm('
    ]
    
    # Allowed skill types
    ALLOWED_SKILLS = {
        'active_listening', 'communication', 'leadership', 'teamwork', 
        'problem_solving', 'conflict_resolution', 'decision_making',
        'written_communication', 'public_speaking', 'team_motivation'
    }
    
    @staticmethod
    def validate_user_id(user_id: str) -> bool:
        """Validate user ID format"""
        if not user_id or not isinstance(user_id, str):
            return False
        return bool(re.match(ValidationUtils.USER_ID_PATTERN, user_id))
    
    @staticmethod
    def validate_session_id(session_id: str) -> bool:
        """Validate session ID format (UUID)"""
        if not session_id or not isinstance(session_id, str):
            return False
        return bool(re.match(ValidationUtils.SESSION_ID_PATTERN, session_id))
    
    @staticmethod
    def validate_skill_type(skill_type: str) -> bool:
        """Validate skill type"""
        if not skill_type or not isinstance(skill_type, str):
            return False
        
        # Check format
        if not re.match(ValidationUtils.SKILL_TYPE_PATTERN, skill_type):
            return False
        
        # Check if it's in allowed list
        return skill_type.lower() in ValidationUtils.ALLOWED_SKILLS
    
    @staticmethod
    def validate_difficulty_range(difficulty: Optional[int]) -> bool:
        """Validate difficulty is in valid range"""
        if difficulty is None:
            return True
        return isinstance(difficulty, int) and 1 <= difficulty <= 5
    
    @staticmethod
    def validate_response_length(response: str, min_words: int = 3, max_words: int = 500) -> bool:
        """Validate response has appropriate length"""
        if not response or not isinstance(response, str):
            return False
        
        word_count = len(response.strip().split())
        return min_words <= word_count <= max_words


class SanitizationUtils:
    """Utilities for input sanitization"""
    
    @staticmethod
    def sanitize_text_input(text: str) -> str:
        """Comprehensive text sanitization"""
        if not text:
            return ""
        
        # Basic cleanup
        sanitized = text.strip()
        
        # HTML escape
        sanitized = html.escape(sanitized)
        
        # Remove dangerous patterns (case insensitive)
        for pattern in ValidationUtils.DANGEROUS_PATTERNS:
            sanitized = re.sub(re.escape(pattern), '', sanitized, flags=re.IGNORECASE)
        
        # Normalize whitespace
        sanitized = re.sub(r'\s+', ' ', sanitized).strip()
        
        return sanitized
    
    @staticmethod
    def sanitize_alphanumeric(text: str) -> str:
        """Keep only alphanumeric characters, underscores, and hyphens"""
        if not text:
            return ""
        
        # Keep only safe characters
        sanitized = re.sub(r'[^a-zA-Z0-9_-]', '', text.strip())
        return sanitized
    
    @staticmethod
    def sanitize_skill_type(skill_type: str) -> str:
        """Sanitize skill type input"""
        if not skill_type:
            return ""
        
        # Convert to lowercase and keep only letters and underscores
        sanitized = re.sub(r'[^a-zA-Z_]', '', skill_type.strip().lower())
        return sanitized
    
    @staticmethod
    def truncate_text(text: str, max_length: int = 1000) -> str:
        """Truncate text to safe length"""
        if not text:
            return ""
        
        if len(text) <= max_length:
            return text
        
        return text[:max_length].strip() + "..."


class VagueResponseDetector:
    """Utility to detect vague or inappropriate responses"""
    
    VAGUE_RESPONSES = {
        'hello', 'hi', 'hey', 'ok', 'yes', 'no', 'sure', 'maybe',
        'idk', 'dunno', 'whatever', 'fine', 'good', 'bad', 'nice',
        'cool', 'great', 'awesome', 'lol', 'haha', 'hmm', 'uhm',
        'ddd', 'aaa', 'bbb', 'ccc', 'eee', 'fff', 'ggg', 'hhh'
    }
    
    @staticmethod
    def is_vague_response(response: str) -> Dict[str, Any]:
        """
        Detect if response is vague or inappropriate
        Returns dict with detection results
        """
        if not response or not isinstance(response, str):
            return {
                "is_vague": True,
                "reason": "empty_response",
                "suggested_score": 5,
                "feedback": "Please provide a response to continue with the simulation."
            }
        
        cleaned_response = response.strip().lower()
        word_count = len(response.strip().split())
        char_count = len(cleaned_response.replace(' ', ''))
        
        # Too short
        if word_count < 3:
            return {
                "is_vague": True,
                "reason": "too_short",
                "suggested_score": 10,
                "feedback": "Your response is too brief. Please provide more detail about your approach."
            }
        
        # Obviously vague responses
        if cleaned_response in VagueResponseDetector.VAGUE_RESPONSES:
            return {
                "is_vague": True,
                "reason": "vague_response",
                "suggested_score": 15,
                "feedback": "Please provide a more detailed response that addresses the scenario."
            }
        
        # Repetitive characters (like "aaa" or "ddd")
        if char_count > 0 and len(set(cleaned_response.replace(' ', ''))) < max(3, char_count * 0.3):
            return {
                "is_vague": True,
                "reason": "repetitive_characters",
                "suggested_score": 5,
                "feedback": "Please provide a meaningful response to the scenario."
            }
        
        # All good
        return {
            "is_vague": False,
            "reason": "appropriate",
            "suggested_score": None,
            "feedback": None
        }


# Custom Pydantic validators
class ValidationMixins:
    """Mixin class with common validators for Pydantic models"""
    
    @validator('user_id', allow_reuse=True)
    def validate_user_id(cls, v):
        if v and not ValidationUtils.validate_user_id(v):
            raise ValueError('Invalid user ID format. Must be 3-50 alphanumeric characters, underscores, or hyphens.')
        return SanitizationUtils.sanitize_alphanumeric(v) if v else v
    
    @validator('skill_type', allow_reuse=True)
    def validate_skill_type(cls, v):
        if v:
            sanitized = SanitizationUtils.sanitize_skill_type(v)
            if not ValidationUtils.validate_skill_type(sanitized):
                raise ValueError(f'Invalid skill type. Must be one of: {", ".join(ValidationUtils.ALLOWED_SKILLS)}')
            return sanitized
        return v
    
    @validator('difficulty_preference', allow_reuse=True)
    def validate_difficulty(cls, v):
        if v is not None and not ValidationUtils.validate_difficulty_range(v):
            raise ValueError('Difficulty must be between 1 and 5')
        return v
    
    @validator('user_response', allow_reuse=True)
    def validate_user_response(cls, v):
        if v:
            # Sanitize the response
            sanitized = SanitizationUtils.sanitize_text_input(v)
            
            # Check if response is too long
            if len(sanitized) > 2000:
                sanitized = SanitizationUtils.truncate_text(sanitized, 2000)
            
            return sanitized
        return v
