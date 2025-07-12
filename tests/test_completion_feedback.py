#!/usr/bin/env python3
"""
Script para probar el feedback de finalización completo de simulaciones.
Ejecuta una simulación completa hasta su finalización y verifica que se genere
el feedback detallado correctamente.
"""

import requests
import json
import time
from datetime import datetime


# Configuración
BASE_URL = "http://localhost:8000"
USER_ID = "test_user_feedback_001"


def print_section(title):
    """Imprimir sección con formato"""
    print(f"\n{'='*60}")
    print(f"🔍 {title}")
    print('='*60)


def print_response(response, title):
    """Imprimir respuesta con formato"""
    print(f"\n📋 {title}")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(json.dumps(data, indent=2, ensure_ascii=False))
    else:
        print(f"Error: {response.text}")
    print("-" * 40)


def test_completion_feedback():
    """Probar el feedback completo de finalización"""
    
    print_section("PRUEBA DE FEEDBACK DE FINALIZACIÓN COMPLETO")
    
    # 1. Obtener lista de escenarios disponibles
    print_section("1. Obtener escenarios disponibles")
    scenarios_response = requests.get(f"{BASE_URL}/scenarios/conflict_resolution")
    print_response(scenarios_response, "Escenarios de resolución de conflictos")
    
    if scenarios_response.status_code != 200:
        print("❌ No se pudieron obtener los escenarios")
        return
    
    scenarios = scenarios_response.json()["scenarios"]
    if not scenarios:
        print("❌ No hay escenarios disponibles")
        return
    
    scenario_id = scenarios[0]["scenario_id"]
    print(f"✅ Usando escenario: {scenarios[0]['title']} (ID: {scenario_id})")
    
    # 2. Iniciar simulación
    print_section("2. Iniciar nueva simulación")
    start_payload = {
        "user_id": USER_ID,
        "scenario_id": scenario_id,
        "difficulty_preference": 3
    }
    
    start_response = requests.post(f"{BASE_URL}/simulation/start", json=start_payload)
    print_response(start_response, "Respuesta de inicio")
    
    if start_response.status_code != 200:
        print("❌ No se pudo iniciar la simulación")
        return
    
    session_id = start_response.json()["session_id"]
    print(f"✅ Simulación iniciada con ID: {session_id}")
    
    # 3. Simular respuestas hasta completar
    print_section("3. Completar simulación paso a paso")
    
    step_responses = [
        {
            "user_response": "Como desarrollador senior, creo que el principal desafío es la comunicación efectiva entre equipos técnicos y no técnicos. Mi experiencia me dice que necesitamos establecer canales claros de comunicación y usar un lenguaje que todos puedan entender. He trabajado en proyectos similares donde implementamos reuniones diarias de sincronización.",
            "response_time_seconds": 95,
            "help_requested": False
        },
        {
            "user_response": "Entiendo perfectamente la frustración del cliente. Primero, me disculparía sinceramente por los inconvenientes causados. Luego explicaría en términos claros qué está causando los retrasos y cuáles son nuestros planes específicos para resolverlo. Propondría reuniones semanales de seguimiento para mantenerlo informado del progreso y le daría mi contacto directo para cualquier preocupación.",
            "response_time_seconds": 120,
            "help_requested": False
        },
        {
            "user_response": "Para resolver este conflicto, organizaría una reunión mediada donde cada parte pueda expresar sus preocupaciones. Como líder técnico, buscaría entender las perspectivas de ambos equipos y identificar los puntos en común. Propondría una solución híbrida que incorpore las mejores ideas de ambos enfoques, estableciendo claramente las responsabilidades de cada equipo.",
            "response_time_seconds": 150,
            "help_requested": False
        },
        {
            "user_response": "Mi plan sería: 1) Reorganizar las prioridades del sprint actual priorizando las funcionalidades críticas, 2) Comunicar transparentemente la situación a todos los stakeholders, 3) Implementar sesiones de pair programming para acelerar el desarrollo, 4) Establecer checkpoints diarios para monitorear el progreso, 5) Preparar un plan de contingencia para mitigar riesgos futuros.",
            "response_time_seconds": 180,
            "help_requested": False
        }
    ]
    
    for i, response_data in enumerate(step_responses, 1):
        print(f"\n🔄 Enviando respuesta {i}/4...")
        
        response = requests.post(
            f"{BASE_URL}/simulation/{session_id}/respond",
            json=response_data
        )
        
        print_response(response, f"Respuesta del paso {i}")
        
        if response.status_code != 200:
            print(f"❌ Error en el paso {i}")
            continue
        
        result = response.json()
        
        # Verificar si la simulación se completó
        if result.get("is_completed"):
            print(f"🎉 ¡Simulación completada en el paso {i}!")
            
            # Verificar si hay feedback de finalización
            if "completion_feedback" in result:
                print_section("4. FEEDBACK DE FINALIZACIÓN DETALLADO")
                
                feedback = result["completion_feedback"]
                
                # Mostrar métricas de rendimiento
                print("\n📊 MÉTRICAS DE RENDIMIENTO:")
                performance = feedback["performance"]
                print(f"• Puntuación general: {performance['overall_score']}/100")
                print(f"• Puntuación promedio por paso: {performance['average_step_score']}/100")
                print(f"• Tiempo total: {performance['total_time_minutes']} minutos")
                print(f"• Tiempo promedio de respuesta: {performance['average_response_time_seconds']} segundos")
                print(f"• Ayuda solicitada: {performance['help_requests_count']} veces")
                print(f"• Porcentaje completado: {performance['completion_percentage']}%")
                print(f"• Nivel de confianza: {performance['confidence_level']}")
                
                # Mostrar evaluación por habilidades
                print("\n🎯 EVALUACIÓN POR HABILIDADES:")
                for assessment in feedback["skill_assessments"]:
                    print(f"\n• {assessment['skill_name']} ({assessment['level']}):")
                    print(f"  - Puntuación: {assessment['score']}/100")
                    print(f"  - Fortalezas: {', '.join(assessment['strengths'])}")
                    print(f"  - Áreas de mejora: {', '.join(assessment['areas_for_improvement'])}")
                    print(f"  - Feedback específico: {assessment['specific_feedback']}")
                
                # Mostrar feedback general
                print(f"\n💬 FEEDBACK GENERAL:")
                print(feedback["overall_feedback"])
                
                # Mostrar logros
                print(f"\n🏆 LOGROS CLAVE:")
                for achievement in feedback["key_achievements"]:
                    print(f"• {achievement}")
                
                # Mostrar aprendizajes
                print(f"\n📚 APRENDIZAJES PRINCIPALES:")
                for learning in feedback["main_learnings"]:
                    print(f"• {learning}")
                
                # Mostrar recomendaciones
                print(f"\n🎯 PRÓXIMOS PASOS RECOMENDADOS:")
                for recommendation in feedback["next_steps_recommendations"]:
                    print(f"• {recommendation}")
                
                # Mostrar información adicional
                print(f"\n📈 INFORMACIÓN ADICIONAL:")
                print(f"• Ranking percentil: {feedback['percentile_ranking']}%")
                print(f"• Certificado obtenido: {'Sí' if feedback['certificate_earned'] else 'No'}")
                if feedback['badge_unlocked']:
                    print(f"• Badge desbloqueado: {feedback['badge_unlocked']}")
                print(f"• Completado en: {feedback['completed_at']}")
                
                print("\n✅ PRUEBA DE FEEDBACK COMPLETADA EXITOSAMENTE")
                return True
            else:
                print("⚠️ Simulación completada pero sin feedback detallado")
                
        else:
            print(f"✅ Paso {i} completado. Continuando...")
        
        # Pequeña pausa entre respuestas
        time.sleep(1)
    
    print("❌ La simulación no se completó después de todas las respuestas")
    return False


def test_status_endpoint_after_completion():
    """Probar el endpoint de status después de completar"""
    print_section("5. Verificar endpoint de status después de completar")
    
    # Nota: Necesitaríamos el session_id de la prueba anterior
    # Por ahora, solo documentamos que esto debería probarse
    print("📝 Esta prueba requiere un session_id de una simulación completada")
    print("📝 El endpoint /simulation/{session_id}/status debería mostrar el estado 'completed'")


if __name__ == "__main__":
    print("🚀 Iniciando prueba de feedback de finalización completo...")
    print(f"⏰ Hora de inicio: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        success = test_completion_feedback()
        if success:
            print("\n🎉 ¡TODAS LAS PRUEBAS PASARON!")
        else:
            print("\n❌ ALGUNAS PRUEBAS FALLARON")
            
    except Exception as e:
        print(f"\n💥 ERROR DURANTE LA PRUEBA: {str(e)}")
    
    print(f"\n⏰ Hora de finalización: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("🏁 Prueba finalizada")
