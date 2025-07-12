from pydantic import BaseModel, Field
from typing import List, Optional


class PaginationParamsDTO(BaseModel):
    """DTO para parámetros de paginación"""
    page: int = Field(default=1, ge=1, description="Número de página (inicia en 1)")
    page_size: int = Field(default=10, ge=1, le=100, description="Tamaño de página (máximo 100)")
    

class PaginationMetaDTO(BaseModel):
    """DTO para metadatos de paginación"""
    current_page: int
    page_size: int
    total_items: int
    total_pages: int
    has_next: bool
    has_previous: bool


class PaginatedSkillDTO(BaseModel):
    """DTO para skill con progreso paginado - coherente con vistas móviles"""
    skill_id: str
    skill_name: str  # Nombre técnico 
    skill_type: str  # Tipo de skill (conflict_resolution, etc.)
    name: str  # Nombre para mostrar
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
    """DTO para respuesta paginada de skills con progreso"""
    user_id: str
    skills: List[PaginatedSkillDTO]
    pagination: PaginationMetaDTO


# Import necesario para evitar importaciones circulares
from .scenario_dtos import ScenarioDTO

class PaginatedScenariosResponseDTO(BaseModel):
    """DTO para respuesta paginada de escenarios"""
    skill_type: str
    scenarios: List[ScenarioDTO]
    pagination: PaginationMetaDTO
