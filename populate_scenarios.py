
import asyncio
import sys
import os
from dotenv import load_dotenv


load_dotenv()

sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from app.soft_skills_practice.infrastructure.persistence.database import db_connection
from app.soft_skills_practice.infrastructure.persistence.models.simulation_models import Scenario


SCENARIOS_DATA = [
    {
        "skill_type": "active_listening",
        "title": "Daily Standup with Technical Conflicts",
        "description": "Facilitate a daily standup where two developers disagree about the microservice architecture.",
        "difficulty_level": 2,
        "estimated_duration": 15,
        "initial_situation": "In the daily standup, the senior developer questions the decision to use MongoDB while the junior developer defends their technical choice. As Scrum Master you need to...",
        "scenario_icon": "fas fa-code-branch",
        "scenario_color": "#4CAF50",
        "is_popular": True,
        "tags": ["scrum", "architecture", "team management"]
    },
    {
        "skill_type": "active_listening",
        "title": "Client Does Not Understand Technical Limitations",
        "description": "Explain to a client why their requirement is not technically feasible in the requested time.",
        "difficulty_level": 3,
        "estimated_duration": 20,
        "initial_situation": "The client insists they need real-time integration with 15 external APIs in 2 weeks, but technically it is impossible...",
        "scenario_icon": "fas fa-user-tie",
        "scenario_color": "#FF9800",
        "is_popular": True,
        "tags": ["client", "technical limitations", "expectations"]
    },


    {
        "skill_type": "public_speaking",
        "title": "Sprint Demo to Stakeholders",
        "description": "Present the sprint results to non-technical stakeholders who do not understand the value of refactoring.",
        "difficulty_level": 3,
        "estimated_duration": 20,
        "initial_situation": "You must explain why 60% of the sprint was dedicated to refactoring and technical debt to stakeholders who only want to see new features...",
        "scenario_icon": "fas fa-presentation",
        "scenario_color": "#2196F3",
        "is_popular": True,
        "tags": ["demo", "stakeholders", "technical debt"]
    },
    {
        "skill_type": "public_speaking",
        "title": "Cloud Architecture Presentation",
        "description": "Present the migration to microservices on AWS to a senior technical committee.",
        "difficulty_level": 4,
        "estimated_duration": 25,
        "initial_situation": "You must convince the technical committee to migrate the legacy monolith to microservices on AWS, justifying costs and risks...",
        "scenario_icon": "fas fa-cloud",
        "scenario_color": "#9C27B0",
        "is_popular": True,
        "tags": ["cloud", "architecture", "migration"]
    },


    {
        "skill_type": "team_motivation",
        "title": "Team Burned Out by Crunch",
        "description": "Motivate your development team after 3 months of urgent releases and hotfixes.",
        "difficulty_level": 4,
        "estimated_duration": 20,
        "initial_situation": "Your team has worked weekends for 3 months fixing critical bugs in production. Morale is very low and there is a risk of resignations...",
        "scenario_icon": "fas fa-battery-empty",
        "scenario_color": "#F44336",
        "is_popular": True,
        "tags": ["burnout", "crunch", "retention"]
    },
    {
        "skill_type": "team_motivation",
        "title": "Frustrated Junior Developer",
        "description": "Help a junior developer who feels overwhelmed by the complexity of legacy code.",
        "difficulty_level": 2,
        "estimated_duration": 15,
        "initial_situation": "A junior developer is frustrated because they do not understand the 10-year-old legacy code and feel they are not contributing to the team...",
        "scenario_icon": "fas fa-seedling",
        "scenario_color": "#4CAF50",
        "is_popular": True,
        "tags": ["junior", "mentoring", "legacy code"]
    },


    {
        "skill_type": "conflict_resolution",
        "title": "DevOps vs Development on CI/CD",
        "description": "Resolve tension between DevOps who want to automate everything and developers who prefer manual deployments.",
        "difficulty_level": 3,
        "estimated_duration": 25,
        "initial_situation": "The DevOps team implemented a strict CI/CD pipeline, but developers complain that it is too slow and prefer fast manual deployments...",
        "scenario_icon": "fas fa-cogs",
        "scenario_color": "#FF5722",
        "is_popular": True,
        "tags": ["devops", "ci/cd", "automation"]
    },
    {
        "skill_type": "conflict_resolution",
        "title": "QA vs Development on Testing",
        "description": "Mediate between QA who reports many bugs and developers who say the test cases are unrealistic.",
        "difficulty_level": 3,
        "estimated_duration": 20,
        "initial_situation": "QA is reporting 50 bugs per sprint, but developers argue that many are edge cases that never occur in real production...",
        "scenario_icon": "fas fa-bug",
        "scenario_color": "#9C27B0",
        "is_popular": True,
        "tags": ["qa", "testing", "quality"]
    },


    {
        "skill_type": "written_communication",
        "title": "Critical API Documentation",
        "description": "Document a complex API so other teams can integrate it without constant questions.",
        "difficulty_level": 3,
        "estimated_duration": 25,
        "initial_situation": "You developed a critical billing API and 5 other teams need to integrate it. You must create documentation that avoids 20 daily questions...",
        "scenario_icon": "fas fa-file-code",
        "scenario_color": "#2196F3",
        "is_popular": True,
        "tags": ["documentation", "api", "integration"]
    },


    {
        "skill_type": "decision_making",
        "title": "Choose Tech Stack for MVP",
        "description": "Decide the tech stack for an MVP with an aggressive timeline and a mixed junior/senior team.",
        "difficulty_level": 4,
        "estimated_duration": 30,
        "initial_situation": "You have 3 months to launch an MVP, a team of 2 seniors and 3 juniors, and must choose between React/Node.js, Angular/.NET or Vue/Python...",
        "scenario_icon": "fas fa-code",
        "scenario_color": "#FF9800",
        "is_popular": True,
        "tags": ["stack", "mvp", "timeline"]
    }
]

async def populate_scenarios():
    """Poblar la base de datos con escenarios de ejemplo"""
    try:
        print("🔄 Conectando a MongoDB...")
        await db_connection.connect()
        print("✅ Conexión exitosa!")
        
        created_count = 0
        updated_count = 0
        # Eliminar todos los escenarios existentes antes de poblar
        deleted =await Scenario.delete_all()

        print(f"🗑️ Escenarios eliminados: {deleted.deleted_count}")

        
        for scenario_data in SCENARIOS_DATA:
            # Verificar si ya existe un escenario similar
            existing = await Scenario.find_one({
                "skill_type": scenario_data["skill_type"],
                "title": scenario_data["title"]
            })
            
            if existing:
                # Actualizar escenario existente
                for key, value in scenario_data.items():
                    setattr(existing, key, value)
                await existing.save()
                print(f"   ✏️ Actualizado: {scenario_data['title']}")
                updated_count += 1
            else:
                # Crear nuevo escenario
                new_scenario = Scenario(**scenario_data)
                await new_scenario.insert()
                print(f"   ➕ Creado: {scenario_data['title']}")
                created_count += 1
        
        # Mostrar resumen
        print(f"\n📊 Resumen:")
        print(f"   └─ Escenarios creados: {created_count}")
        print(f"   └─ Escenarios actualizados: {updated_count}")
        
        # Mostrar estadísticas por skill
        skills = set(s["skill_type"] for s in SCENARIOS_DATA)
        print(f"\n📂 Escenarios por skill:")
        for skill in skills:
            count = await Scenario.find({"skill_type": skill}).count()
            print(f"   └─ {skill}: {count} escenarios")
        
        print("✅ Escenarios poblados exitosamente")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        await db_connection.disconnect()

if __name__ == "__main__":
    asyncio.run(populate_scenarios())
