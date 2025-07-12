from pydantic import BaseModel
from typing import List, Optional


class ScenarioDTO(BaseModel):
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


class ScenariosResponseDTO(BaseModel):
    """DTO para respuesta de escenarios por skill"""
    skill_type: str
    total_scenarios: int
    popular_scenarios: List[ScenarioDTO]
    all_scenarios: List[ScenarioDTO]
