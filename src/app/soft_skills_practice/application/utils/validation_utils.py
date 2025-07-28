"""
Validation utilities for input sanitization and data validation
"""
import re
import html
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, validator


class SanitizationUtils:
    """Utility class for sanitizing user inputs"""
    
    @staticmethod
    def sanitize_text_input(text: str) -> str:
        """Sanitize text input by removing potentially harmful content"""
        if not text:
            return ""
        
        # Remove HTML tags
        text = re.sub(r'<[^>]*>', '', text)
        
        # Escape HTML entities
        text = html.escape(text)
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Remove potentially harmful characters
        text = re.sub(r'[<>"\']', '', text)
        
        return text
    
    @staticmethod
    def sanitize_skill_type(skill_type: str) -> str:
        """Sanitize skill type to ensure it matches expected format"""
        if not skill_type:
            return ""
        
        # Convert to lowercase and replace spaces with underscores
        sanitized = skill_type.lower().strip()
        sanitized = re.sub(r'[^a-z0-9_]', '_', sanitized)
        sanitized = re.sub(r'_+', '_', sanitized)
        sanitized = sanitized.strip('_')
        
        return sanitized
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format"""
        if not email:
            return False
        
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))


class ValidationUtils:
    """Utility class for data validation"""
    
    @staticmethod
    def validate_user_id(user_id: str) -> bool:
        """Validate user ID format"""
        if not user_id:
            return False
        
        # User ID should be alphanumeric and possibly contain hyphens or underscores
        pattern = r'^[a-zA-Z0-9_-]+$'
        return bool(re.match(pattern, user_id)) and len(user_id) >= 3
    
    @staticmethod
    def validate_skill_level(level: str) -> bool:
        """Validate skill level"""
        valid_levels = ['beginner', 'intermediate', 'advanced']
        return level.lower() in valid_levels
    
    @staticmethod
    def validate_seniority_level(level: str) -> bool:
        """Validate seniority level"""
        valid_levels = ['junior', 'mid', 'senior', 'lead', 'principal']
        return level.lower() in valid_levels
    
    @staticmethod
    def validate_language(language: str) -> bool:
        """Validate language preference"""
        valid_languages = ['english', 'spanish', 'french', 'german', 'portuguese']
        return language.lower() in valid_languages


class VagueResponseDetector:
    """Utility class for detecting vague or insufficient responses"""
    
    VAGUE_PATTERNS = [
        r'\b(i think|maybe|perhaps|probably|possibly)\b',
        r'\b(not sure|don\'t know|unclear)\b',
        r'\b(ok|fine|good|bad)\b$',
        r'^.{1,10}$',  # Very short responses
    ]
    
    @staticmethod
    def is_vague_response(response: str) -> bool:
        """Check if a response is too vague or insufficient"""
        if not response or len(response.strip()) < 5:
            return True
        
        response_lower = response.lower().strip()
        
        for pattern in VagueResponseDetector.VAGUE_PATTERNS:
            if re.search(pattern, response_lower):
                return True
        
        # Check for meaningful content (at least some words)
        words = re.findall(r'\b\w+\b', response_lower)
        if len(words) < 3:
            return True
        
        return False
    
    @staticmethod
    def get_improvement_suggestions(response: str) -> List[str]:
        """Get suggestions for improving a vague response"""
        suggestions = []
        
        if len(response.strip()) < 20:
            suggestions.append("Try to provide more detailed explanations")
        
        if VagueResponseDetector.is_vague_response(response):
            suggestions.extend([
                "Be more specific about your approach",
                "Include concrete examples or scenarios",
                "Explain your reasoning step by step"
            ])
        
        return suggestions


class ValidationMixins:
    """Mixin class to add validation capabilities to Pydantic models"""
    
    @validator('*', pre=True)
    def validate_strings(cls, v):
        """Basic string validation for all string fields"""
        if isinstance(v, str):
            return SanitizationUtils.sanitize_text_input(v)
        return v
    
    def validate_required_fields(self) -> Dict[str, Any]:
        """Validate that all required fields are present and valid"""
        errors = {}
        
        for field_name, field_info in self.__fields__.items():
            if field_info.required:
                value = getattr(self, field_name, None)
                if value is None or (isinstance(value, str) and not value.strip()):
                    errors[field_name] = "This field is required"
        
        return errors
