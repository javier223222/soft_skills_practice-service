from pydantic import BaseModel,Field
from typing import List,Optional 
from datetime import datetime, timezone

class SkillDto(BaseModel):
    """DTO para información de una soft skill"""
    skill_name: str
    display_name: str
    description: str
    category: str  
    difficulty_levels: List[int] = Field(default=[1, 2, 3, 4, 5])
    estimated_time_per_level: int = 15
    total_scenarios: int = 0
    popular_scenarios_count: int = 0
    tags: List[str] = Field(default_factory=list)
    icon: Optional[str] = None
    color: Optional[str] = None

class SkillCategoryDto(BaseModel):
    """DTO para categoría de skills"""
    category_name: str
    display_name: str
    description: str
    skills: List[SkillDto]
    total_skills: int

class AvailableSkillsResponseDto(BaseModel):
    """DTO para respuesta de skills disponibles"""
    categories: List[SkillCategoryDto]
    total_skills: int
    total_categories: int
    featured_skills: List[SkillDto]  
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))