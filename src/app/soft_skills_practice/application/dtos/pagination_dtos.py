from pydantic import BaseModel, Field
from typing import List, Optional


from .scenario_dtos import ScenarioDTO

class PaginationParamsDTO(BaseModel):
    
    page: int = Field(default=1, ge=1, description="Number of the page to retrieve (1-based index)")
    page_size: int = Field(default=10, ge=1, le=100, description="Page size (maximum 100)")


class PaginationMetaDTO(BaseModel):
    
    current_page: int
    page_size: int
    total_items: int
    total_pages: int
    has_next: bool
    has_previous: bool


class PaginatedSkillDTO(BaseModel):
    
    skill_id: str
    skill_name: str 
    skill_type: str  
    name: str  
    description: str
    category: str
    difficulty: str
    visual_config: dict = Field(default_factory=lambda: {
        "icon": "🎯",
        "color_hex": "#4A90E2",
        "emoji": "🎯"
    })
    estimated_duration_minutes: int = 15
    user_progress: dict = Field(default_factory=lambda: {
        "progress_percentage": 0.0,
        "current_level": 1,
        "points_earned": 0,
        "sessions_completed": 0,
        "average_score": 0.0
    })
    scenarios_count: int = 0


class PaginatedSkillsResponseDTO(BaseModel):
   
    user_id: str
    skills: List[PaginatedSkillDTO]
    pagination: PaginationMetaDTO



class PaginatedScenariosResponseDTO(BaseModel):

    skill_type: str
    scenarios: List[ScenarioDTO]
    pagination: PaginationMetaDTO
