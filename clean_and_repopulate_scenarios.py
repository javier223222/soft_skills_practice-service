#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para limpiar y repoblar escenarios con caracteres correctos
"""
import asyncio
import sys
import os

# Agregar src al path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from app.soft_skills_practice.infrastructure.persistence.database import db_connection
from app.soft_skills_practice.infrastructure.persistence.models.simulation_models import Scenario

async def clean_and_repopulate():
    """Limpiar todos los escenarios y repoblar con caracteres correctos"""
    try:
        print("🔄 Conectando a MongoDB...")
        await db_connection.connect()
        print("✅ Conexión exitosa!")
        
        # Eliminar todos los escenarios existentes
        print("🧹 Eliminando escenarios existentes...")
        await Scenario.delete_all()
        print("✅ Escenarios eliminados")
        
        # Escenarios corregidos sin caracteres especiales
        scenarios_data = [
            # Escenarios para Escucha Activa (active_listening)
            {
                "skill_type": "active_listening",
                "title": "Daily Standup con Conflictos Tecnicos",
                "description": "Facilita un daily standup donde dos desarrolladores discrepan sobre la arquitectura del microservicio",
                "difficulty_level": 2,
                "estimated_duration": 15,
                "initial_situation": "En el daily standup, el desarrollador senior cuestiona la decision de usar MongoDB mientras el desarrollador junior defiende su eleccion tecnica. Como Scrum Master necesitas mediar y encontrar una solucion constructiva.",
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
                "initial_situation": "El cliente insiste en que necesita integracion en tiempo real con 15 APIs externas en 2 semanas, pero tecnicamente es imposible. Debes explicar las limitaciones sin frustrar al cliente.",
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
                "initial_situation": "Debes explicar por que el 60% del sprint se dedico a refactoring y deuda tecnica a stakeholders que solo quieren ver nuevas features visibles.",
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
                "initial_situation": "Debes convencer al comite tecnico de migrar el monolito legacy a microservicios en AWS, justificando costos, beneficios y riesgos de la migracion.",
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
                "initial_situation": "Tu equipo ha trabajado fines de semana durante 3 meses arreglando bugs criticos en produccion. La moral esta por el suelo y hay riesgo de renuncias masivas.",
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
                "initial_situation": "Un developer junior esta frustrado porque no entiende el codigo legacy de 10 anos y siente que no esta contribuyendo al equipo de manera significativa.",
                "scenario_icon": "fas fa-seedling",
                "scenario_color": "#4CAF50",
                "is_popular": True,
                "tags": ["junior", "mentoring", "legacy code"]
            }
        ]
        
        # Crear nuevos escenarios
        created_count = 0
        for scenario_data in scenarios_data:
            new_scenario = Scenario(**scenario_data)
            await new_scenario.insert()
            print(f"   ➕ Creado: {scenario_data['title']}")
            created_count += 1
        
        print(f"\n📊 Resumen:")
        print(f"   └─ Escenarios creados: {created_count}")
        print("✅ Escenarios repoblados exitosamente")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        await db_connection.disconnect()

if __name__ == "__main__":
    asyncio.run(clean_and_repopulate())
