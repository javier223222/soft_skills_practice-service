from pydantic import BaseModel, validator
from typing import List, Optional
from ..utils.validation_utils import ValidationMixins, SanitizationUtils

class ScenarioDTO(BaseModel, ValidationMixins):
    """DTO para información de un escenario"""
    scenario_id: str
    skill_type: str
    title: str
    description: str
    difficulty_level: int
    estimated_duration: int
    initial_situation: str
    scenario_icon: Optional[str] = None
    scenario_image_url: Optional[str] = None
    scenario_color: Optional[str] = None
    usage_count: int = 0
    is_popular: bool = False
    average_rating: float = 0.0
    tags: List[str] = []
    
    @validator('title', 'description', 'initial_situation')
    def validate_text_fields(cls, v):
        if v:
            return SanitizationUtils.sanitize_text_input(v)
        return v
    
    @validator('scenario_image_url')
    def validate_url(cls, v):
        if v:
            # Basic URL sanitization
            return SanitizationUtils.sanitize_text_input(v)
        return v

class ScenariosResponseDTO(BaseModel, ValidationMixins):
    """DTO para respuesta de escenarios por skill"""
    skill_type: str
    total_scenarios: int
    popular_scenarios: List[ScenarioDTO]
    all_scenarios: List[ScenarioDTO]
