"""
Shared Value Objects para todos los bounded contexts
"""
from abc import ABC
from typing import Any, List
from pydantic import BaseModel, validator
from datetime import datetime
from enum import Enum


class ValueObject(BaseModel, ABC):
    """Base class para todos los value objects"""
    
    class Config:
        frozen = True  # Inmutable
        validate_assignment = True


class UserId(ValueObject):
    """Value Object para identificación de usuario"""
    value: str
    
    @validator('value')
    def validate_user_id(cls, v):
        if not v or len(v.strip()) < 10:
            raise ValueError("User ID must be at least 10 characters")
        return v.strip()


class SessionId(ValueObject):
    """Value Object para identificación de sesión"""
    value: str
    
    @validator('value')
    def validate_session_id(cls, v):
        if not v or len(v.strip()) < 8:
            raise ValueError("Session ID must be at least 8 characters")
        return v.strip()


class SkillType(ValueObject):
    """Value Object para tipo de habilidad"""
    value: str
    
    @validator('value')
    def validate_skill_type(cls, v):
        allowed_skills = {
            'communication', 'leadership', 'teamwork', 'problem_solving',
            'time_management', 'emotional_intelligence', 'adaptability',
            'conflict_resolution', 'decision_making', 'critical_thinking',
            'active_listening', 'negotiation', 'stress_management'
        }
        if v.lower() not in allowed_skills:
            raise ValueError(f"Invalid skill type: {v}")
        return v.lower()


class DifficultyLevel(ValueObject):
    """Value Object para nivel de dificultad"""
    value: int
    
    @validator('value')
    def validate_difficulty(cls, v):
        if not 1 <= v <= 5:
            raise ValueError("Difficulty level must be between 1 and 5")
        return v


class ProficiencyLevel(str, Enum):
    """Enum para niveles de competencia"""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


class Score(ValueObject):
    """Value Object para puntajes"""
    value: float
    max_value: float = 100.0
    
    @validator('value')
    def validate_score(cls, v, values):
        max_val = values.get('max_value', 100.0)
        if not 0 <= v <= max_val:
            raise ValueError(f"Score must be between 0 and {max_val}")
        return round(v, 2)


class TimeSpent(ValueObject):
    """Value Object para tiempo transcurrido"""
    minutes: int
    
    @validator('minutes')
    def validate_minutes(cls, v):
        if v < 0:
            raise ValueError("Time cannot be negative")
        return v


class Percentage(ValueObject):
    """Value Object para porcentajes"""
    value: float
    
    @validator('value')
    def validate_percentage(cls, v):
        if not 0 <= v <= 100:
            raise ValueError("Percentage must be between 0 and 100")
        return round(v, 2)


class SeniorityLevel(ValueObject):
    """Value Object para nivel de seniority"""
    value: str
    
    @validator('value')
    def validate_seniority(cls, v):
        allowed_levels = {'junior', 'mid', 'senior', 'lead', 'principal', 'architect'}
        if v.lower() not in allowed_levels:
            raise ValueError(f"Invalid seniority level: {v}")
        return v.lower()


class TechnicalSpecialization(ValueObject):
    """Value Object para especialización técnica"""
    value: str
    
    @validator('value')
    def validate_specialization(cls, v):
        if not v or len(v.strip()) < 3:
            raise ValueError("Technical specialization must be at least 3 characters")
        return v.strip().title()
