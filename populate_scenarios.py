#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para poblar la base de datos con escenarios de ejemplo
"""
import asyncio
import sys
import os

# Agregar src al path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from app.soft_skills_practice.infrastructure.persistence.database import db_connection
from app.soft_skills_practice.infrastructure.persistence.models.simulation_models import Scenario

# Escenarios de ejemplo por skill - Enfocados en profesionales de TI
SCENARIOS_DATA = [
    # Escenarios para Escucha Activa (active_listening)
    {
        "skill_type": "active_listening",
        "title": "Daily Standup con Conflictos Tecnicos",
        "description": "Facilita un daily standup donde dos desarrolladores discrepan sobre la arquitectura del microservicio",
        "difficulty_level": 2,
        "estimated_duration": 15,
        "initial_situation": "En el daily standup, el desarrollador senior cuestiona la decision de usar MongoDB mientras el desarrollador junior defiende su eleccion tecnica. Como Scrum Master necesitas...",
        "scenario_icon": "fas fa-code-branch",
        "scenario_color": "#4CAF50",
        "is_popular": True,
        "tags": ["scrum", "arquitectura", "team management"]
    },
    {
        "skill_type": "active_listening",
        "title": "Cliente no Entiende Limitaciones Tecnicas",
        "description": "Explica a un cliente por que su requerimiento no es tecnicamente viable en el tiempo solicitado",
        "difficulty_level": 3,
        "estimated_duration": 20,
        "initial_situation": "El cliente insiste en que necesita integracion en tiempo real con 15 APIs externas en 2 semanas, pero tecnicamente es imposible...",
        "scenario_icon": "fas fa-user-tie",
        "scenario_color": "#FF9800",
        "is_popular": True,
        "tags": ["cliente", "limitaciones tecnicas", "expectativas"]
    },
    
    # Escenarios para Hablar en Publico (public_speaking)
    {
        "skill_type": "public_speaking",
        "title": "Demo de Sprint a Stakeholders",
        "description": "Presenta los resultados del sprint a stakeholders no tecnicos que no entienden el valor del refactoring",
        "difficulty_level": 3,
        "estimated_duration": 20,
        "initial_situation": "Debes explicar por que el 60% del sprint se dedico a refactoring y deuda tecnica a stakeholders que solo quieren ver nuevas features...",
        "scenario_icon": "fas fa-presentation",
        "scenario_color": "#2196F3",
        "is_popular": True,
        "tags": ["demo", "stakeholders", "deuda tecnica"]
    },
    {
        "skill_type": "public_speaking",
        "title": "Presentacion de Arquitectura Cloud",
        "description": "Presenta la migracion a microservicios en AWS a un comite tecnico senior",
        "difficulty_level": 4,
        "estimated_duration": 25,
        "initial_situation": "Debes convencer al comite tecnico de migrar el monolito legacy a microservicios en AWS, justificando costos y riesgos...",
        "scenario_icon": "fas fa-cloud",
        "scenario_color": "#9C27B0",
        "is_popular": True,
        "tags": ["cloud", "arquitectura", "migracion"]
    },
    
    # Escenarios para Liderazgo (team_motivation)
    {
        "skill_type": "team_motivation",
        "title": "Equipo Quemado por Crunch",
        "description": "Motiva a tu equipo de desarrollo despues de 3 meses de releases urgentes y hotfixes",
        "difficulty_level": 4,
        "estimated_duration": 20,
        "initial_situation": "Tu equipo ha trabajado fines de semana durante 3 meses arreglando bugs criticos en produccion. La moral esta por el suelo y hay riesgo de renuncias...",
        "scenario_icon": "fas fa-battery-empty",
        "scenario_color": "#F44336",
        "is_popular": True,
        "tags": ["burnout", "crunch", "retencion"]
    },
    {
        "skill_type": "team_motivation",
        "title": "Junior Developer Frustrado",
        "description": "Ayuda a un desarrollador junior que se siente abrumado por la complejidad del codigo legacy",
        "difficulty_level": 2,
        "estimated_duration": 15,
        "initial_situation": "Un developer junior esta frustrado porque no entiende el codigo legacy de 10 anos y siente que no esta contribuyendo al equipo...",
        "scenario_icon": "fas fa-seedling",
        "scenario_color": "#4CAF50",
        "is_popular": True,
        "tags": ["junior", "mentoring", "legacy code"]
    },
    
    # Escenarios para Resolucion de Conflictos (conflict_resolution)
    {
        "skill_type": "conflict_resolution",
        "title": "DevOps vs Development sobre CI/CD",
        "description": "Resuelve tension entre DevOps que quiere automatizar todo y developers que prefieren deployments manuales",
        "difficulty_level": 3,
        "estimated_duration": 25,
        "initial_situation": "El equipo de DevOps implemento un pipeline CI/CD estricto, pero los developers se quejan de que es muy lento y prefieren deployments manuales rapidos...",
        "scenario_icon": "fas fa-cogs",
        "scenario_color": "#FF5722",
        "is_popular": True,
        "tags": ["devops", "ci/cd", "automation"]
    },
    {
        "skill_type": "conflict_resolution",
        "title": "QA vs Development sobre Testing",
        "description": "Media entre QA que reporta muchos bugs y developers que dicen que los casos de prueba son irreales",
        "difficulty_level": 3,
        "estimated_duration": 20,
        "initial_situation": "QA esta reportando 50 bugs por sprint, pero los developers argumentan que muchos son edge cases que nunca ocurren en produccion real...",
        "scenario_icon": "fas fa-bug",
        "scenario_color": "#9C27B0",
        "is_popular": True,
        "tags": ["qa", "testing", "quality"]
    },
    
    # Escenarios para Comunicacion Escrita (written_communication)
    {
        "skill_type": "written_communication",
        "title": "Documentacion de API Critica",
        "description": "Documenta una API compleja para que otros equipos puedan integrarla sin consultas constantes",
        "difficulty_level": 3,
        "estimated_duration": 25,
        "initial_situation": "Desarrollaste una API de facturacion critica y otros 5 equipos necesitan integrarla. Debes crear documentacion que evite 20 preguntas diarias...",
        "scenario_icon": "fas fa-file-code",
        "scenario_color": "#2196F3",
        "is_popular": True,
        "tags": ["documentacion", "api", "integracion"]
    },
    
    # Escenarios para Toma de Decisiones (decision_making)
    {
        "skill_type": "decision_making",
        "title": "Elegir Stack Tecnologico para MVP",
        "description": "Decide el stack tecnologico para un MVP con timeline agresivo y equipo mixto junior/senior",
        "difficulty_level": 4,
        "estimated_duration": 30,
        "initial_situation": "Tienes 3 meses para lanzar un MVP, equipo de 2 seniors y 3 juniors, y debes elegir entre React/Node.js, Angular/.NET o Vue/Python...",
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
