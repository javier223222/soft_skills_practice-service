import asyncio
import sys
import os
from dotenv import load_dotenv


load_dotenv()


sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from app.soft_skills_practice.infrastructure.persistence.database import db_connection
from app.soft_skills_practice.infrastructure.persistence.repositories.skill_catalog_repository import SkillCatalogRepository

async def populate_skills_catalog():
    """Poblar catálogo inicial de soft skills"""
    try:
        print("🔄 Conectando a MongoDB...")
        await db_connection.connect()
        print("✅ Conexión exitosa!")
        
        repo = SkillCatalogRepository()
        
       
        skills_data = [
            {
                "skill_name": "active_listening",
                "display_name": "Escucha Activa",
                "description": "Capacidad de escuchar y comprender completamente a otros",
                "category": "communication",
                "tags": ["listening", "empathy", "understanding"],
                "primary_color": "#4CAF50",
                "secondary_color": "#66BB6A",
                "gradient_start": "#4CAF50",
                "gradient_end": "#66BB6A",
                "emoji": "👂",
                "icon_url": "/icons/skills/active-listening.svg",
                "icon_name": "fas fa-ear-listen",
                "background_color": "#E8F5E8",
                "icon_color": "#4CAF50",
                "display_order": 1,
                "is_featured": True
            },
            {
                "skill_name": "public_speaking",
                "display_name": "Hablar en Público",
                "description": "Habilidad para presentar ideas claramente ante audiencias",
                "category": "communication",
                "tags": ["presentation", "confidence", "clarity"],
                "primary_color": "#2196F3",
                "secondary_color": "#42A5F5",
                "gradient_start": "#2196F3",
                "gradient_end": "#42A5F5",
                "emoji": "🎤",
                "icon_url": "/icons/skills/public-speaking.svg",
                "icon_name": "fas fa-microphone",
                "background_color": "#E3F2FD",
                "icon_color": "#2196F3",
                "display_order": 2,
                "is_featured": True
            },
            {
                "skill_name": "written_communication",
                "display_name": "Comunicación Escrita",
                "description": "Capacidad de escribir de manera clara y efectiva",
                "category": "communication",
                "tags": ["writing", "clarity", "professional"],
                "primary_color": "#FF9800",
                "secondary_color": "#FFB74D",
                "gradient_start": "#FF9800",
                "gradient_end": "#FFB74D",
                "emoji": "✍️",
                "icon_url": "/icons/skills/written-communication.svg",
                "icon_name": "fas fa-pen-nib",
                "background_color": "#FFF3E0",
                "icon_color": "#FF9800",
                "display_order": 3,
                "is_featured": False
            },
            {
                "skill_name": "nonverbal_communication",
                "display_name": "Comunicación No Verbal",
                "description": "Uso efectivo del lenguaje corporal y gestos",
                "category": "communication",
                "tags": ["body_language", "gestures", "presence"],
                "primary_color": "#9C27B0",
                "secondary_color": "#BA68C8",
                "gradient_start": "#9C27B0",
                "gradient_end": "#BA68C8",
                "emoji": "🤝",
                "icon_url": "/icons/skills/nonverbal-communication.svg",
                "icon_name": "fas fa-handshake",
                "background_color": "#F3E5F5",
                "icon_color": "#9C27B0",
                "display_order": 4,
                "is_featured": False
            },
            {
                "skill_name": "team_motivation",
                "display_name": "Motivación de Equipos",
                "description": "Capacidad de inspirar y motivar a los miembros del equipo",
                "category": "leadership",
                "tags": ["motivation", "inspiration", "team_building"],
                "primary_color": "#F44336",
                "secondary_color": "#EF5350",
                "gradient_start": "#F44336",
                "gradient_end": "#EF5350",
                "emoji": "🚀",
                "icon_url": "/icons/skills/team-motivation.svg",
                "icon_name": "fas fa-rocket",
                "background_color": "#FFEBEE",
                "icon_color": "#F44336",
                "display_order": 1,
                "is_featured": True
            },
            {
                "skill_name": "decision_making",
                "display_name": "Toma de Decisiones",
                "description": "Habilidad para tomar decisiones efectivas bajo presión",
                "category": "leadership",
                "tags": ["decisions", "analysis", "judgment"],
                "primary_color": "#3F51B5",
                "secondary_color": "#5C6BC0",
                "gradient_start": "#3F51B5",
                "gradient_end": "#5C6BC0",
                "emoji": "⚖️",
                "icon_url": "/icons/skills/decision-making.svg",
                "icon_name": "fas fa-balance-scale",
                "background_color": "#E8EAF6",
                "icon_color": "#3F51B5",
                "display_order": 2,
                "is_featured": False
            },
            {
                "skill_name": "delegation",
                "display_name": "Delegación",
                "description": "Capacidad de asignar tareas y responsabilidades efectivamente",
                "category": "leadership",
                "tags": ["delegation", "trust", "responsibility"],
                "primary_color": "#009688",
                "secondary_color": "#4DB6AC",
                "gradient_start": "#009688",
                "gradient_end": "#4DB6AC",
                "emoji": "🎯",
                "icon_url": "/icons/skills/delegation.svg",
                "icon_name": "fas fa-bullseye",
                "background_color": "#E0F2F1",
                "icon_color": "#009688",
                "display_order": 3,
                "is_featured": False
            },
            {
                "skill_name": "conflict_resolution",
                "display_name": "Resolución de Conflictos",
                "description": "Habilidad para mediar y resolver disputas",
                "category": "leadership",
                "tags": ["conflict", "mediation", "problem_solving"],
                "primary_color": "#FF5722",
                "secondary_color": "#FF7043",
                "gradient_start": "#FF5722",
                "gradient_end": "#FF7043",
                "emoji": "🤝",
                "icon_url": "/icons/skills/conflict-resolution.svg",
                "icon_name": "fas fa-handshake",
                "background_color": "#FBE9E7",
                "icon_color": "#FF5722",
                "display_order": 4,
                "is_featured": False
            },
            {
                "skill_name": "collaboration",
                "display_name": "Colaboración",
                "description": "Capacidad de trabajar efectivamente con otros",
                "category": "teamwork",
                "tags": ["collaboration", "cooperation", "synergy"],
                "primary_color": "#795548",
                "secondary_color": "#8D6E63",
                "gradient_start": "#795548",
                "gradient_end": "#8D6E63",
                "emoji": "👥",
                "icon_url": "/icons/skills/collaboration.svg",
                "icon_name": "fas fa-users",
                "background_color": "#EFEBE9",
                "icon_color": "#795548",
                "display_order": 1,
                "is_featured": True
            },
            {
                "skill_name": "adaptability",
                "display_name": "Adaptabilidad",
                "description": "Flexibilidad para adaptarse a cambios y nuevas situaciones",
                "category": "teamwork",
                "tags": ["flexibility", "change", "adaptation"],
                "primary_color": "#607D8B",
                "secondary_color": "#78909C",
                "gradient_start": "#607D8B",
                "gradient_end": "#78909C",
                "emoji": "🌱",
                "icon_url": "/icons/skills/adaptability.svg",
                "icon_name": "fas fa-leaf",
                "background_color": "#ECEFF1",
                "icon_color": "#607D8B",
                "display_order": 2,
                "is_featured": False
            },
            {
                "skill_name": "cultural_awareness",
                "display_name": "Conciencia Cultural",
                "description": "Comprensión y respeto por la diversidad cultural",
                "category": "teamwork",
                "tags": ["culture", "diversity", "inclusion"],
                "primary_color": "#8BC34A",
                "secondary_color": "#AED581",
                "gradient_start": "#8BC34A",
                "gradient_end": "#AED581",
                "emoji": "🌍",
                "icon_url": "/icons/skills/cultural-awareness.svg",
                "icon_name": "fas fa-globe",
                "background_color": "#F1F8E9",
                "icon_color": "#8BC34A",
                "display_order": 3,
                "is_featured": False
            },
            {
                "skill_name": "empathy",
                "display_name": "Empatía",
                "description": "Habilidad para entender y compartir los sentimientos de otros",
                "category": "emotional_intelligence",
                "tags": ["empathy", "understanding", "compassion"],
                "primary_color": "#E91E63",
                "secondary_color": "#EC407A",
                "gradient_start": "#E91E63",
                "gradient_end": "#EC407A",
                "emoji": "❤️",
                "icon_url": "/icons/skills/empathy.svg",
                "icon_name": "fas fa-heart",
                "background_color": "#FCE4EC",
                "icon_color": "#E91E63",
                "display_order": 1,
                "is_featured": True
            },
            {
                "skill_name": "self_awareness",
                "display_name": "Autoconciencia",
                "description": "Capacidad de reconocer y entender las propias emociones",
                "category": "emotional_intelligence",
                "tags": ["self_awareness", "emotions", "reflection"],
                "primary_color": "#9C27B0",
                "secondary_color": "#BA68C8",
                "gradient_start": "#9C27B0",
                "gradient_end": "#BA68C8",
                "emoji": "🧠",
                "icon_url": "/icons/skills/self-awareness.svg",
                "icon_name": "fas fa-brain",
                "background_color": "#F3E5F5",
                "icon_color": "#9C27B0",
                "display_order": 2,
                "is_featured": False
            },
            {
                "skill_name": "stress_management",
                "display_name": "Manejo del Estrés",
                "description": "Capacidad de manejar la presión y el estrés efectivamente",
                "category": "emotional_intelligence",
                "tags": ["stress", "pressure", "calmness"],
                "primary_color": "#00BCD4",
                "secondary_color": "#4DD0E1",
                "gradient_start": "#00BCD4",
                "gradient_end": "#4DD0E1",
                "emoji": "🧘",
                "icon_url": "/icons/skills/stress-management.svg",
                "icon_name": "fas fa-lotus",
                "background_color": "#E0F7FA",
                "icon_color": "#00BCD4",
                "display_order": 3,
                "is_featured": False
            },
            {
                "skill_name": "critical_thinking",
                "display_name": "Pensamiento Crítico",
                "description": "Capacidad de analizar información objetivamente",
                "category": "problem_solving",
                "tags": ["analysis", "logic", "reasoning"],
                "primary_color": "#673AB7",
                "secondary_color": "#7986CB",
                "gradient_start": "#673AB7",
                "gradient_end": "#7986CB",
                "emoji": "🔍",
                "icon_url": "/icons/skills/critical-thinking.svg",
                "icon_name": "fas fa-search",
                "background_color": "#EDE7F6",
                "icon_color": "#673AB7",
                "display_order": 1,
                "is_featured": True
            },
            {
                "skill_name": "creativity",
                "display_name": "Creatividad",
                "description": "Habilidad para generar ideas innovadoras",
                "category": "problem_solving",
                "tags": ["creativity", "innovation", "ideas"],
                "primary_color": "#FFEB3B",
                "secondary_color": "#FFF176",
                "gradient_start": "#FFEB3B",
                "gradient_end": "#FFF176",
                "emoji": "💡",
                "icon_url": "/icons/skills/creativity.svg",
                "icon_name": "fas fa-lightbulb",
                "background_color": "#FFFDE7",
                "icon_color": "#F57F17",
                "display_order": 2,
                "is_featured": False
            },
            {
                "skill_name": "analytical_thinking",
                "display_name": "Pensamiento Analítico",
                "description": "Capacidad de descomponer problemas complejos",
                "category": "problem_solving",
                "tags": ["analysis", "logic", "systematic"],
                "primary_color": "#FF9800",
                "secondary_color": "#FFB74D",
                "gradient_start": "#FF9800",
                "gradient_end": "#FFB74D",
                "emoji": "📊",
                "icon_url": "/icons/skills/analytical-thinking.svg",
                "icon_name": "fas fa-chart-bar",
                "background_color": "#FFF3E0",
                "icon_color": "#FF9800",
                "display_order": 3,
                "is_featured": False
            }
        ]
        
        created_count = 0
        updated_count = 0
        
        for skill_data in skills_data:
            
            existing = await repo.find_by_skill_name(skill_data["skill_name"])
            
            if existing:
               
                for key, value in skill_data.items():
                    setattr(existing, key, value)
                await existing.save()
                updated_count += 1
                print(f"   ✏️ Actualizada: {skill_data['display_name']}")
            else:
                
                await repo.create_skill(skill_data)
                created_count += 1
                print(f"   ✅ Creada: {skill_data['display_name']}")
        
        print(f"\n📊 Resumen:")
        print(f"   └─ Skills creadas: {created_count}")
        print(f"   └─ Skills actualizadas: {updated_count}")
        print(f"   └─ Total en catálogo: {created_count + updated_count}")
        
        # Verificar skills destacadas
        featured_skills = await repo.find_featured_skills()
        print(f"   └─ Skills destacadas: {len(featured_skills)}")
        
        # Mostrar skills por categoría
        categories = await repo.get_skills_by_category_with_stats()
        print(f"\n📂 Skills por categoría:")
        for category, skills in categories.items():
            print(f"   └─ {category}: {len(skills)} skills")
        
        await db_connection.disconnect()
        print("✅ Catálogo de skills poblado exitosamente")
        
        return True
        
    except Exception as e:
        print(f"❌ Error poblando catálogo: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    asyncio.run(populate_skills_catalog())