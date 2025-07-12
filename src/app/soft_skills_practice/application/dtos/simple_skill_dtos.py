from pydantic import BaseModel
from typing import List, Optional


class SimpleSkillDTO(BaseModel):
    """DTO simple para información de una soft skill"""
    skill_id: str
    name: str
    description: str
    category: str
    difficulty: str
    icon: Optional[str] = None
    color: Optional[str] = None
    estimated_duration_minutes: int = 15
    progress_percentage: float = 0.0


class SimpleAvailableSkillsResponseDTO(BaseModel):
    """DTO simple para respuesta de skills disponibles"""
    total_skills: int
    skills: List[SimpleSkillDTO]


class SimpleUserSkillProgressDTO(BaseModel):
    """DTO simple para progreso de usuario en una skill"""
    skill_id: str
    progress_percentage: float
    total_sessions: int = 0
    completed_sessions: int = 0
    average_score: Optional[float] = None


class SimpleUserProgressResponseDTO(BaseModel):
    """DTO simple para respuesta de progreso del usuario"""
    user_id: str
    total_skills_practiced: int
    skills_progress: List[SimpleUserSkillProgressDTO]
