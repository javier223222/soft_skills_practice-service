import asyncio
import sys
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Agregar src al path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from app.soft_skills_practice.infrastructure.persistence.database import db_connection
from app.soft_skills_practice.infrastructure.persistence.repositories import (
    SimulationSessionRepository,
    SimulationStepRepository,
    UserRecommendationsRepository,
    ScenarioRepository
)
from app.soft_skills_practice.infrastructure.persistence.models.simulation_models import (
    SimulationSession,
    SimulationStep,
    UserRecommendations,
    Scenario
)

async def test_repositories():
    """Probar todos los repositorios"""
    try:
        print("🔄 Conectando a MongoDB...")
        await db_connection.connect()
        print("✅ Conexión exitosa!")
        
        # Inicializar repositorios
        session_repo = SimulationSessionRepository()
        step_repo = SimulationStepRepository()
        recommendations_repo = UserRecommendationsRepository()
        scenario_repo = ScenarioRepository()
        
        # Test Session Repository
        print("\n🔄 Probando SimulationSessionRepository...")
        test_session = SimulationSession(
            user_id="test_user_456",
            user_name="Test User",
            skill_type="leadership",
            scenario_title="Test Leadership Scenario"
        )
        
        # Crear sesión usando repositorio
        created_session = await session_repo.create(test_session)
        print(f"✅ Sesión creada: {created_session.session_id}")
        
        # Buscar por user_id
        user_sessions = await session_repo.find_by_user_id("test_user_456")
        print(f"✅ Sesiones encontradas para usuario: {len(user_sessions)}")
        
        # Test Recommendations Repository
        print("\n🔄 Probando UserRecommendationsRepository...")
        await recommendations_repo.update_skill_progress(
            user_id="test_user_456",
            skill_name="leadership",
            score=85.5,
            session_duration=15
        )
        print("✅ Progreso de habilidad actualizado")
        
        # Obtener analytics
        analytics = await recommendations_repo.get_user_skill_analytics("test_user_456")
        print(f"✅ Analytics obtenidos: {analytics['total_skills']} habilidades")
        
        # Test Scenario Repository
        print("\n🔄 Probando ScenarioRepository...")
        test_scenario = Scenario(
            skill_type="leadership",
            title="Test Leadership Challenge",
            description="A challenging leadership scenario for testing",
            difficulty_level=3,
            estimated_duration=20,
            initial_situation="Your team is facing a major deadline...",
            is_popular=True
        )
        
        created_scenario = await scenario_repo.create(test_scenario)
        print(f"✅ Escenario creado: {created_scenario.scenario_id}")
        
        # Buscar por skill type
        leadership_scenarios = await scenario_repo.find_by_skill_type("leadership")
        print(f"✅ Escenarios de liderazgo encontrados: {len(leadership_scenarios)}")
        
        # Test Step Repository
        print("\n🔄 Probando SimulationStepRepository...")
        test_step = SimulationStep(
            session_id=created_session.session_id,
            step_number=1,
            step_type="pre_test",
            message_type="pre_test_question"
        )
        
        created_step = await step_repo.create(test_step)
        print(f"✅ Step creado: {created_step.id}")
        
        # Buscar steps por sesión
        session_steps = await step_repo.find_by_session_id(created_session.session_id)
        print(f"✅ Steps encontrados para sesión: {len(session_steps)}")
        
        # Limpiar datos de prueba
        print("\n🔄 Limpiando datos de prueba...")
        await session_repo.delete(created_session)
        await step_repo.delete(created_step)
        await scenario_repo.delete(created_scenario)
        
        # Las recomendaciones las dejamos para mantener el progreso
        print("✅ Datos de prueba limpiados")
        
        await db_connection.disconnect()
        print("✅ Prueba de repositorios completada exitosamente")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en la prueba: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    asyncio.run(test_repositories())