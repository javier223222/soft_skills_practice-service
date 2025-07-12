#!/usr/bin/env python3
"""
Script simple para probar los endpoints sin la configuración completa
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import json
from datetime import datetime

app = FastAPI(
    title="Soft Skills Practice Service",
    description="Microservicio para práctica de soft skills con IA",
    version="1.0.0"
)

# DTOs básicos para los tests
class PaginationResponse(BaseModel):
    current_page: int
    page_size: int
    total_items: int
    total_pages: int
    has_next: bool
    has_previous: bool

class SkillResponse(BaseModel):
    skill_id: str
    name: str
    description: str
    category: str
    difficulty_level: int
    estimated_time_minutes: int
    icon: str
    color: str
    progress_percentage: float = 0.0

class ScenarioResponse(BaseModel):
    scenario_id: str
    title: str
    description: str
    skill_type: str
    difficulty_level: int
    estimated_duration_minutes: int
    popularity_score: float
    icon: str
    color: str

class StartSimulationRequest(BaseModel):
    user_id: str
    scenario_id: str
    difficulty_preference: Optional[int] = 3

class RespondSimulationRequest(BaseModel):
    user_response: str
    response_time_seconds: Optional[float] = None

@app.get("/")
async def health_check():
    """Endpoint básico de health check"""
    return {
        "status": "ok",
        "service": "soft-skills-practice-service",
        "message": "Servicio funcionando correctamente"
    }

@app.get("/health")
async def detailed_health():
    """Health check detallado"""
    return {
        "status": "healthy",
        "service": "soft-skills-practice-service",
        "version": "1.0.0",
        "database": "mock-connected"
    }

@app.get("/softskill/{user_id}")
async def get_user_soft_skills_progress(
    user_id: str, 
    page: int = 1, 
    page_size: int = 10
):
    """
    Obtener todas las soft skills disponibles con el progreso del usuario (paginado)
    """
    # Mock data
    mock_skills = [
        {
            "skill_id": "communication",
            "name": "Comunicación Efectiva",
            "description": "Habilidades de comunicación verbal y no verbal",
            "category": "interpersonal",
            "difficulty_level": 2,
            "estimated_time_minutes": 45,
            "icon": "💬",
            "color": "#3498db",
            "progress_percentage": 25.5
        },
        {
            "skill_id": "leadership",
            "name": "Liderazgo",
            "description": "Capacidad de dirigir y motivar equipos",
            "category": "management",
            "difficulty_level": 4,
            "estimated_time_minutes": 60,
            "icon": "👑",
            "color": "#e74c3c",
            "progress_percentage": 0.0
        },
        {
            "skill_id": "conflict_resolution",
            "name": "Resolución de Conflictos",
            "description": "Mediación y resolución de disputas",
            "category": "interpersonal",
            "difficulty_level": 3,
            "estimated_time_minutes": 50,
            "icon": "🤝",
            "color": "#2ecc71",
            "progress_percentage": 75.0
        }
    ]
    
    # Simular paginación
    total_items = len(mock_skills)
    total_pages = (total_items + page_size - 1) // page_size
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    skills_page = mock_skills[start_idx:end_idx]
    
    return {
        "user_id": user_id,
        "skills": skills_page,
        "pagination": {
            "current_page": page,
            "page_size": page_size,
            "total_items": total_items,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_previous": page > 1
        }
    }

@app.get("/scenarios/{skill_type}")
async def get_paginated_scenarios_by_skill(
    skill_type: str,
    page: int = 1,
    page_size: int = 10
):
    """
    Obtener escenarios disponibles para una soft skill específica (CON PAGINACIÓN)
    """
    # Mock data
    mock_scenarios = [
        {
            "scenario_id": f"{skill_type}_scenario_1",
            "title": f"Reunión de Equipo - {skill_type}",
            "description": "Escenario de práctica en reuniones de trabajo",
            "skill_type": skill_type,
            "difficulty_level": 2,
            "estimated_duration_minutes": 30,
            "popularity_score": 4.5,
            "icon": "👥",
            "color": "#3498db"
        },
        {
            "scenario_id": f"{skill_type}_scenario_2",
            "title": f"Presentación Ejecutiva - {skill_type}",
            "description": "Práctica de presentaciones a nivel ejecutivo",
            "skill_type": skill_type,
            "difficulty_level": 4,
            "estimated_duration_minutes": 45,
            "popularity_score": 4.2,
            "icon": "📊",
            "color": "#e74c3c"
        }
    ]
    
    total_items = len(mock_scenarios)
    total_pages = (total_items + page_size - 1) // page_size
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    scenarios_page = mock_scenarios[start_idx:end_idx]
    
    return {
        "skill_type": skill_type,
        "scenarios": scenarios_page,
        "pagination": {
            "current_page": page,
            "page_size": page_size,
            "total_items": total_items,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_previous": page > 1
        }
    }

@app.post("/simulation/start")
async def start_simulation(request: StartSimulationRequest):
    """
    Iniciar una nueva simulación de soft skills
    """
    # Mock response
    session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    return {
        "success": True,
        "session_id": session_id,
        "user_id": request.user_id,
        "scenario": {
            "scenario_id": request.scenario_id,
            "title": "Escenario Mock de Práctica",
            "description": "Escenario de prueba para validar endpoints"
        },
        "initial_test": {
            "question": "¿Cómo manejarías una situación de conflicto en tu equipo?",
            "context": "Te encuentras en una reunión donde dos miembros del equipo no están de acuerdo.",
            "test_type": "open_question"
        },
        "session_info": {
            "session_id": session_id,
            "skill_type": "conflict_resolution",
            "status": "active",
            "current_step": 1,
            "total_steps": 5,
            "difficulty_level": request.difficulty_preference or 3,
            "started_at": datetime.now().isoformat()
        },
        "message": "Simulación iniciada exitosamente",
        "next_action": "complete_initial_test"
    }

@app.post("/simulation/{session_id}/respond")
async def respond_simulation(session_id: str, request: RespondSimulationRequest):
    """
    Responder en una simulación activa
    """
    # Mock response normal
    return {
        "success": True,
        "session_id": session_id,
        "step_number": 2,
        "user_response": request.user_response,
        "ai_feedback": "Excelente respuesta. Has demostrado comprensión del conflicto.",
        "evaluation": {
            "score": 85,
            "strengths": ["Escucha activa", "Empatía"],
            "areas_for_improvement": ["Asertividad"],
            "confidence": "high"
        },
        "next_step": {
            "question": "¿Qué harías si la situación escalara?",
            "context": "El conflicto se ha intensificado.",
            "step_type": "scenario_continuation"
        },
        "is_completed": False,
        "message": "Respuesta procesada correctamente",
        "next_action": "continue_simulation"
    }

@app.get("/simulation/{session_id}/status")
async def get_simulation_status(session_id: str):
    """
    Obtener el estado completo de una simulación
    """
    return {
        "success": True,
        "session_info": {
            "session_id": session_id,
            "user_id": "test_user",
            "skill_type": "conflict_resolution",
            "status": "active",
            "current_step": 2,
            "total_steps": 5,
            "difficulty_level": 3,
            "started_at": datetime.now().isoformat()
        },
        "scenario_info": {
            "title": "Conflicto en Reunión de Equipo",
            "description": "Práctica de mediación en conflictos"
        },
        "steps_completed": 1,
        "current_step": {
            "question": "¿Qué harías si la situación escalara?",
            "context": "El conflicto se ha intensificado."
        },
        "progress_summary": {
            "completion_percentage": 40.0,
            "average_score": 85.0,
            "total_time_minutes": 15
        },
        "is_active": True,
        "next_action": "respond_to_current_step"
    }

# ========== ENDPOINTS ESPECÍFICOS PARA APLICACIÓN MÓVIL ==========

@app.get("/mobile/user/{user_id}/level")
async def get_user_level(user_id: str):
    """
    Obtener información del nivel del usuario para la aplicación móvil
    """
    return {
        "success": True,
        "user_id": user_id,
        "current_level": 5,
        "current_points": 1250,
        "points_to_next_level": 750,
        "total_points_earned": 1250,
        "level_progress_percentage": 62.5,
        "achievements_unlocked": 8,
        "simulations_completed": 12
    }

@app.get("/mobile/user/{user_id}/achievements")
async def get_user_achievements(user_id: str):
    """
    Obtener logros del usuario para la aplicación móvil
    """
    mock_achievements = [
        {
            "achievement_id": "first_simulation",
            "title": "Primera Simulación",
            "description": "Completaste tu primera simulación",
            "icon": "🎯",
            "unlocked_at": "2024-01-15T10:30:00",
            "rarity": "common"
        },
        {
            "achievement_id": "conflict_master",
            "title": "Maestro de Conflictos",
            "description": "Completaste 5 simulaciones de resolución de conflictos",
            "icon": "🤝",
            "unlocked_at": "2024-01-20T14:45:00",
            "rarity": "rare"
        }
    ]
    
    return {
        "success": True,
        "user_id": user_id,
        "total_achievements": len(mock_achievements),
        "achievements": mock_achievements
    }

@app.get("/mobile/user/{user_id}/dashboard")
async def get_user_mobile_dashboard(user_id: str):
    """
    Obtener datos del dashboard para la aplicación móvil
    """
    return {
        "success": True,
        "user_id": user_id,
        "level_info": {
            "current_level": 5,
            "current_points": 1250,
            "points_to_next_level": 750,
            "total_points_earned": 1250,
            "level_progress_percentage": 62.5,
            "next_level": 6
        },
        "achievements_summary": {
            "total_unlocked": 8,
            "recent_achievements": [
                {
                    "title": "Maestro de Conflictos",
                    "icon": "🤝",
                    "rarity": "rare"
                },
                {
                    "title": "Comunicador Experto",
                    "icon": "💬",
                    "rarity": "epic"
                }
            ]
        },
        "stats": {
            "simulations_completed": 12,
            "achievements_unlocked": 8,
            "current_streak": 5,
            "favorite_skill": "conflict_resolution"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
