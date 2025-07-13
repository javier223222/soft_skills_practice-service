import asyncio
from fastapi import FastAPI, HTTPException,Request
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv

from app.soft_skills_practice.infrastructure.persistence.database import db_connection
from app.soft_skills_practice.infrastructure.messaging.message_queue_service import message_queue_service

from app.soft_skills_practice.application.use_cases.get_paginated_user_skills_use_case import GetPaginatedUserSkillsUseCase
from app.soft_skills_practice.application.use_cases.get_paginated_scenarios_by_skill_use_case import GetPaginatedScenariosBySkillUseCase

from app.soft_skills_practice.application.use_cases.start_simulation_by_scenario_use_case import StartSimulationByScenarioUseCase
from app.soft_skills_practice.application.use_cases.start_simulation_by_skill_use_case import StartSimulationBySkillUseCase
from app.soft_skills_practice.application.use_cases.respond_simulation_use_case import RespondSimulationUseCase
from app.soft_skills_practice.application.use_cases.get_simulation_status_use_case import GetSimulationStatusUseCase
from app.soft_skills_practice.application.use_cases.generate_completion_feedback_use_case import GenerateCompletionFeedbackUseCase
from app.soft_skills_practice.application.use_cases.get_popular_scenarios_use_case import GetPopularScenariosUseCase
from app.soft_skills_practice.application.dtos.pagination_dtos import PaginationParamsDTO
from app.soft_skills_practice.application.dtos.simulation_dtos import (
    StartSimulationRequestDTO, 
    RespondSimulationRequestDTO,
    SimulationCompletedResponseDTO,
    StartSimulationRequestBySoftSkillDTO
)

from app.soft_skills_practice.application.services.gemini_service import GeminiService
from app.soft_skills_practice.application.services.user_mobile_service import UserMobileService

from app.soft_skills_practice.infrastructure.persistence.repositories.skill_catalog_repository import SkillCatalogRepository
from app.soft_skills_practice.infrastructure.persistence.repositories.simulation_session_repository import SimulationSessionRepository
from app.soft_skills_practice.infrastructure.persistence.repositories.simulation_step_repository import SimulationStepRepository
from app.soft_skills_practice.infrastructure.persistence.repositories.scenario_repository import ScenarioRepository


load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestión del ciclo de vida de la aplicación"""
    
    await db_connection.connect()
    print("✅ Conexión a MongoDB establecida")
    
    try:
        await message_queue_service.connect()
        print("✅ Conexión a Redis (Message Queue) establecida")
    except Exception as e:
        print(f"⚠️  Advertencia: No se pudo conectar a Redis: {e}")
        print("ℹ️  El servicio funcionará sin notificaciones automáticas")
    
    yield
    
   
    await db_connection.disconnect()
    print("❌ Conexión a MongoDB cerrada")
    
    await message_queue_service.disconnect()
    print("❌ Conexión a Redis cerrada")


app = FastAPI(
    title="Soft Skills Practice Service",
    description="Microservicio para práctica de soft skills con IA",
    version="1.0.0",
    lifespan=lifespan
)

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
        "database": "connected"
    }



@app.get("/softskill/{user_id}")
async def get_user_soft_skills_progress(
    user_id: str, 
    page: int = 1, 
    page_size: int = 10,

):
    """
    Obtener todas las soft skills disponibles con el progreso del usuario (paginado)
    
    - Si es un usuario nuevo (sin sesiones previas), se auto-registra implícitamente
    - Retorna skills con progress_percentage = 0.0 para usuarios nuevos
    - Soporte para paginación con parámetros page y page_size
    - page: número de página (inicia en 1)
    - page_size: elementos por página (máximo 100)
    """
    try:
      
        if not user_id or user_id.strip() == "":
            raise HTTPException(status_code=400, detail="El user_id no puede estar vacío")
        
      
        if page < 1:
            raise HTTPException(status_code=400, detail="El número de página debe ser mayor a 0")
        if page_size < 1 or page_size > 100:
            raise HTTPException(status_code=400, detail="El tamaño de página debe estar entre 1 y 100")
        
        
        pagination_params = PaginationParamsDTO(page=page, page_size=page_size)
        
        
        skill_catalog_repo = SkillCatalogRepository()
        simulation_session_repo = SimulationSessionRepository()
        get_paginated_skills_use_case = GetPaginatedUserSkillsUseCase(skill_catalog_repo, simulation_session_repo)
        
        
        paginated_response = await get_paginated_skills_use_case.execute(user_id, pagination_params)
        
        return {
            "user_id": paginated_response.user_id,
            "skills": [skill.dict() for skill in paginated_response.skills],
            "pagination": {
                "current_page": paginated_response.pagination.current_page,
                "page_size": paginated_response.pagination.page_size,
                "total_items": paginated_response.pagination.total_items,
                "total_pages": paginated_response.pagination.total_pages,
                "has_next": paginated_response.pagination.has_next,
                "has_previous": paginated_response.pagination.has_previous
            }
        }
        
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener soft skills: {str(e)}")



@app.get("/scenarios/{skill_type}")
async def get_paginated_scenarios_by_skill(
    skill_type: str,
    page: int = 1,
    page_size: int = 10

):
   
    try:
        
        if not skill_type or skill_type.strip() == "":
            raise HTTPException(status_code=400, detail="El skill_type no puede estar vacío")
        

        if page < 1:
            raise HTTPException(status_code=400, detail="El número de página debe ser mayor a 0")
        if page_size < 1 or page_size > 100:
            raise HTTPException(status_code=400, detail="El tamaño de página debe estar entre 1 y 100")
        
        
        pagination_params = PaginationParamsDTO(page=page, page_size=page_size)
        
        
        scenario_repo = ScenarioRepository()
        get_paginated_scenarios_use_case = GetPaginatedScenariosBySkillUseCase(scenario_repo)
        
        # Obtener escenarios paginados
        paginated_response = await get_paginated_scenarios_use_case.execute(skill_type, pagination_params)
        
        return {
            "skill_type": paginated_response.skill_type,
            "scenarios": [scenario.dict() for scenario in paginated_response.scenarios],
            "pagination": {
                "current_page": paginated_response.pagination.current_page,
                "page_size": paginated_response.pagination.page_size,
                "total_items": paginated_response.pagination.total_items,
                "total_pages": paginated_response.pagination.total_pages,
                "has_next": paginated_response.pagination.has_next,
                "has_previous": paginated_response.pagination.has_previous
            }
        }
        
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener escenarios paginados: {str(e)}")


@app.get("/popular/scenarios")
async def get_paginated_popular_scenaries(
    user_agent:Request,
    page: int = 1,
    page_size: int = 10,
   
):
    try:
        print(f"User-Agent: {user_agent.headers.get('User-Agen', 'Desconocido')}")
        if page < 1:
            raise HTTPException(status_code=400, detail="El número de página debe ser mayor a 0")
        if page_size < 1 or page_size > 100:
            raise HTTPException(status_code=400, detail="El tamaño de página debe estar entre 1 y 100")
        pagination_params=PaginationParamsDTO(page=page,page_size=page_size)
        scenario_repo=ScenarioRepository()
        get_paginated_popular_scenaries_use_case=GetPopularScenariosUseCase(scenario_repository=scenario_repo)
        paginated_response=await get_paginated_popular_scenaries_use_case.execute(pagination_params=pagination_params)
        return {
            
            "scenarios": [scenario.dict() for scenario in paginated_response["scenarios"]],
            "pagination": {
                "current_page": paginated_response["pagination"]["current_page"],
                "page_size": paginated_response["pagination"]["page_size"],
                "total_items": paginated_response["pagination"]["total_items"],
                "total_pages": paginated_response["pagination"]["total_pages"],
                "has_next": paginated_response["pagination"]["has_next"],
                "has_previous": paginated_response["pagination"]["has_previous"]
            }
        }

    except ValueError as ve:
        raise HTTPException(status_code=400,detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500,detail=str(e))

@app.post("/simulation/softskill/start/")
async def start_softskill_simulation(request:StartSimulationRequestBySoftSkillDTO):
    try:
     if not request.user_id or request.user_id.strip() == "":
        raise HTTPException(status_code=400, detail="El user_id no puede estar vacío")
     if not request.skill_type or request.skill_type.strip() == "":
        raise HTTPException(status_code=400, detail="El skill_type no puede estar vacío")
     if request.difficulty_preference and (request.difficulty_preference < 1 or request.difficulty_preference > 5):
        raise HTTPException(status_code=400, detail="La dificultad debe estar entre 1 y 5")
     if not request.tecnical_specialization or request.tecnical_specialization.strip() == "":
        raise HTTPException(status_code=400, detail="La especialización técnica no puede estar vacía")
     if not request.seniority_level or request.seniority_level.strip() == "":
        raise HTTPException(status_code=400, detail="El nivel de seniority no puede estar vacío")
     
     scenario_repo = ScenarioRepository()
     simulation_session_repo = SimulationSessionRepository()
     simulation_step_repo = SimulationStepRepository()
     gemini_service = GeminiService()
        
       
     start_simulation_use_case = StartSimulationBySkillUseCase(
            scenario_repo,
            simulation_session_repo,
            simulation_step_repo,
            gemini_service
        )
     return await start_simulation_use_case.execute(request)
    
        
     
    
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al iniciar simulación de soft skill: {str(e)}")
    
    
   
    raise HTTPException(status_code=501, detail="Esta funcionalidad aún no está implementada")


@app.post("/simulation/scenario/start")
async def start_simulation(request: StartSimulationRequestDTO):
    """
    Iniciar una nueva simulación de soft skills
    
    - Crea una nueva sesión de simulación para el usuario
    - Genera un test inicial personalizado con IA
    - Registra tracking completo de la interacción
    - Retorna información del escenario y test inicial
    """
    try:
          
        
        if not request.user_id or request.user_id.strip() == "":
            raise HTTPException(status_code=400, detail="El user_id no puede estar vacío")
        
        if not request.scenario_id or request.scenario_id.strip() == "":
            raise HTTPException(status_code=400, detail="El scenario_id no puede estar vacío")
        
        if request.difficulty_preference and (request.difficulty_preference < 1 or request.difficulty_preference > 5):
            raise HTTPException(status_code=400, detail="La dificultad debe estar entre 1 y 5")
        
        
        scenario_repo = ScenarioRepository()
        simulation_session_repo = SimulationSessionRepository()
        simulation_step_repo = SimulationStepRepository()
        gemini_service = GeminiService()
        
       
        start_simulation_use_case = StartSimulationByScenarioUseCase( scenario_repo,
            simulation_session_repo,
            simulation_step_repo,
            gemini_service)
        
        
        simulation_response = await start_simulation_use_case.execute(request)
        
        return {
            "success": True,
            "session_id": simulation_response.session_id,
            "user_id": simulation_response.user_id,
            "scenario": simulation_response.scenario,
            "initial_test": simulation_response.first_test,
            "session_info": {
                "session_id": simulation_response.session_info.session_id,
                "skill_type": simulation_response.session_info.skill_type,
                "status": simulation_response.session_info.status,
                "current_step": simulation_response.session_info.current_step,
                "total_steps": simulation_response.session_info.total_steps,
                "difficulty_level": simulation_response.session_info.difficulty_level,
                "started_at": simulation_response.session_info.started_at.isoformat()
            },
            "message": simulation_response.message,
            "next_action": "complete_initial_test"
        }
        
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al iniciar simulación: {str(e)}")

@app.post("/simulation/{session_id}/respond")
async def respond_simulation(session_id: str, request: RespondSimulationRequestDTO):
    """
    Responder en una simulación activa
    
    - Procesa la respuesta del usuario al paso actual
    - Evalúa la respuesta con IA (Gemini)
    - Genera feedback personalizado
    - Crea el siguiente paso de la simulación
    - Actualiza el progreso y tracking completo
    """
    try:
        
        if not session_id or session_id.strip() == "":
            raise HTTPException(status_code=400, detail="El session_id no puede estar vacío")
        
        if not request.user_response or request.user_response.strip() == "":
            raise HTTPException(status_code=400, detail="La respuesta del usuario no puede estar vacía")
        
        if request.response_time_seconds and request.response_time_seconds < 0:
            raise HTTPException(status_code=400, detail="El tiempo de respuesta no puede ser negativo")
        
        
        simulation_session_repo = SimulationSessionRepository()
        simulation_step_repo = SimulationStepRepository()
        scenario_repo = ScenarioRepository()
        gemini_service = GeminiService()
        
        
        generate_completion_feedback_use_case = GenerateCompletionFeedbackUseCase(
            simulation_session_repo,
            simulation_step_repo,
            scenario_repo,
            gemini_service
        )
        
       

        
        respond_simulation_use_case = RespondSimulationUseCase(
            simulation_session_repo,
            simulation_step_repo,
            scenario_repo,
            gemini_service,
            generate_completion_feedback_use_case,
            
        )
        
        
        simulation_response = await respond_simulation_use_case.execute(session_id, request)
        
        
        if isinstance(simulation_response, SimulationCompletedResponseDTO):
            return {
                "success": True,
                "session_id": simulation_response.session_id,
                "is_completed": simulation_response.is_completed,
                "completion_feedback": {
                    "session_id": simulation_response.completion_feedback.session_id,
                    "user_id": simulation_response.completion_feedback.user_id,
                    "scenario_title": simulation_response.completion_feedback.scenario_title,
                    "skill_type": simulation_response.completion_feedback.skill_type,
                    "completion_status": simulation_response.completion_feedback.completion_status,
                    "performance": {
                        "overall_score": simulation_response.completion_feedback.performance.overall_score,
                        "average_step_score": simulation_response.completion_feedback.performance.average_step_score,
                        "total_time_minutes": simulation_response.completion_feedback.performance.total_time_minutes,
                        "average_response_time_seconds": simulation_response.completion_feedback.performance.average_response_time_seconds,
                        "help_requests_count": simulation_response.completion_feedback.performance.help_requests_count,
                        "completion_percentage": simulation_response.completion_feedback.performance.completion_percentage,
                        "confidence_level": simulation_response.completion_feedback.performance.confidence_level
                    },
                    "skill_assessments": [
                        {
                            "skill_name": assessment.skill_name,
                            "score": assessment.score,
                            "level": assessment.level,
                            "strengths": assessment.strengths,
                            "areas_for_improvement": assessment.areas_for_improvement,
                            "specific_feedback": assessment.specific_feedback
                        }
                        for assessment in simulation_response.completion_feedback.skill_assessments
                    ],
                    "overall_feedback": simulation_response.completion_feedback.overall_feedback,
                    "key_achievements": simulation_response.completion_feedback.key_achievements,
                    "main_learnings": simulation_response.completion_feedback.main_learnings,
                    "next_steps_recommendations": simulation_response.completion_feedback.next_steps_recommendations,
                    "percentile_ranking": simulation_response.completion_feedback.percentile_ranking,
                    "completed_at": simulation_response.completion_feedback.completed_at.isoformat(),
                    "certificate_earned": simulation_response.completion_feedback.certificate_earned,
                    "badge_unlocked": simulation_response.completion_feedback.badge_unlocked
                },
                "message": simulation_response.message,
                "next_action": "view_detailed_feedback"
            }
        
        
        return {
            "success": True,
            "session_id": simulation_response.session_id,
            "step_number": simulation_response.step_number,
            "user_response": simulation_response.user_response,
            "ai_feedback": simulation_response.ai_feedback,
            "evaluation": simulation_response.evaluation,
            "next_step": simulation_response.next_step,
            "is_completed": simulation_response.is_completed,
            "message": simulation_response.message,
            "next_action": "continue_simulation" if not simulation_response.is_completed else "simulation_completed"
        }
        
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al procesar respuesta de simulación: {str(e)}")

@app.get("/simulation/{session_id}/status")
async def get_simulation_status(session_id: str):
    """
    Obtener el estado completo de una simulación
    
    - Información detallada de la sesión y progreso
    - Historial completo de pasos y respuestas
    - Evaluaciones y feedback recibido
    - Métricas de tiempo y rendimiento
    - Estado actual y siguiente acción recomendada
    """
    try:
        
        if not session_id or session_id.strip() == "":
            raise HTTPException(status_code=400, detail="El session_id no puede estar vacío")
        
        
        simulation_session_repo = SimulationSessionRepository()
        simulation_step_repo = SimulationStepRepository()
        scenario_repo = ScenarioRepository()
        
        
        get_status_use_case = GetSimulationStatusUseCase(
            simulation_session_repo,
            simulation_step_repo,
            scenario_repo
        )
        
        
        status_response = await get_status_use_case.execute(session_id)
        
        return {
            "success": True,
            "session_info": {
                "session_id": status_response.session_info.session_id,
                "user_id": status_response.session_info.user_id,
                "skill_type": status_response.session_info.skill_type,
                "status": status_response.session_info.status,
                "current_step": status_response.session_info.current_step,
                "total_steps": status_response.session_info.total_steps,
                "difficulty_level": status_response.session_info.difficulty_level,
                "started_at": status_response.session_info.started_at.isoformat()
            },
            "scenario_info": status_response.scenario_info,
            "steps_completed": status_response.steps_completed,
            "current_step": status_response.current_step,
            "progress_summary": status_response.progress_summary,
            "is_active": status_response.is_active,
            "next_action": "respond_to_current_step" if status_response.current_step else ("simulation_completed" if not status_response.is_active else "continue_simulation")
        }
        
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener estado de simulación: {str(e)}")




@app.get("/mobile/user/{user_id}/level")
async def get_user_level(user_id: str):
    """
    Obtener información del nivel del usuario para la aplicación móvil
    
    - Nivel actual del usuario
    - Puntos en el nivel actual
    - Puntos necesarios para el siguiente nivel
    - Progreso del nivel
    - Logros desbloqueados
    """
    try:
        if not user_id or user_id.strip() == "":
            raise HTTPException(status_code=400, detail="El user_id no puede estar vacío")
        
        
        simulation_session_repo = SimulationSessionRepository()
        user_mobile_service = UserMobileService(simulation_session_repo)
        
        
        level_info = await user_mobile_service.get_user_level_info(user_id)
        
        return {
            "success": True,
            "user_id": level_info.user_id,
            "current_level": level_info.current_level,
            "current_points": level_info.current_points,
            "points_to_next_level": level_info.points_to_next_level,
            "total_points_earned": level_info.total_points_earned,
            "level_progress_percentage": level_info.level_progress_percentage,
            "achievements_unlocked": level_info.achievements_unlocked,
            "simulations_completed": level_info.simulations_completed
        }
        
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener nivel del usuario: {str(e)}")


@app.get("/mobile/user/{user_id}/achievements")
async def get_user_achievements(user_id: str):
    """
    Obtener logros del usuario para la aplicación móvil
    
    - Lista de logros desbloqueados
    - Información detallada de cada logro
    - Fecha de desbloqueo
    - Rareza del logro
    """
    try:
        if not user_id or user_id.strip() == "":
            raise HTTPException(status_code=400, detail="El user_id no puede estar vacío")
        
        
        simulation_session_repo = SimulationSessionRepository()
        user_mobile_service = UserMobileService(simulation_session_repo)
        
        
        achievements = await user_mobile_service.get_user_achievements(user_id)
        
        return {
            "success": True,
            "user_id": user_id,
            "total_achievements": len(achievements),
            "achievements": [
                {
                    "achievement_id": achievement.achievement_id,
                    "title": achievement.title,
                    "description": achievement.description,
                    "icon": achievement.icon,
                    "unlocked_at": achievement.unlocked_at.isoformat(),
                    "rarity": achievement.rarity
                }
                for achievement in achievements
            ]
        }
        
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener logros del usuario: {str(e)}")


@app.get("/mobile/user/{user_id}/dashboard")
async def get_user_mobile_dashboard(user_id: str):
    """
    Obtener datos del dashboard para la aplicación móvil
    
    - Información de nivel y progreso
    - Logros recientes
    - Estadísticas generales
    - Datos necesarios para las vistas principales
    """
    try:
        if not user_id or user_id.strip() == "":
            raise HTTPException(status_code=400, detail="El user_id no puede estar vacío")
        
        
        simulation_session_repo = SimulationSessionRepository()
        user_mobile_service = UserMobileService(simulation_session_repo)
        
        
        level_info = await user_mobile_service.get_user_level_info(user_id)
        achievements = await user_mobile_service.get_user_achievements(user_id)
        
        
        recent_achievements = sorted(achievements, key=lambda x: x.unlocked_at, reverse=True)[:3]
        
        return {
            "success": True,
            "user_id": user_id,
            "level_info": {
                "current_level": level_info.current_level,
                "current_points": level_info.current_points,
                "points_to_next_level": level_info.points_to_next_level,
                "total_points_earned": level_info.total_points_earned,
                "level_progress_percentage": level_info.level_progress_percentage,
                "next_level": level_info.current_level + 1
            },
            "achievements_summary": {
                "total_unlocked": len(achievements),
                "recent_achievements": [
                    {
                        "title": achievement.title,
                        "icon": achievement.icon,
                        "rarity": achievement.rarity
                    }
                    for achievement in recent_achievements
                ]
            },
            "stats": {
                "simulations_completed": level_info.simulations_completed,
                "achievements_unlocked": level_info.achievements_unlocked,
                "current_streak": 0,  # TODO: Implementar streak
                "favorite_skill": "conflict_resolution"  # TODO: Calcular skill favorita
            }
        }
        
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener dashboard del usuario: {str(e)}")


