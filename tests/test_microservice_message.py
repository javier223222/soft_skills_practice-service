#!/usr/bin/env python3
"""
Ejemplo completo del mensaje que se envía entre microservicios
cuando una simulación se completa
"""

import redis
import json
from datetime import datetime
from typing import Dict, Any

def create_simulation_completion_message(
    user_id: str,
    simulation_id: str,
    score: int,
    additional_data: Dict[str, Any] = None
) -> Dict[str, Any]:
    """
    Crear mensaje completo para cuando se termina una simulación
    
    Este es el mensaje que recibirá el microservicio de usuarios/perfil
    con toda la información necesaria para actualizar el perfil del usuario
    """
    
    message = {
        # Identificación básica
        "type": "simulation_completed",
        "user_id": user_id,
        "simulation_id": simulation_id,
        
        # Puntuación y rendimiento
        "score": score,
        "max_score": 100,  # Puntuación máxima posible
        "percentage": round((score / 100) * 100, 2),
        
        # Detalles de la simulación
        "simulation_data": {
            "title": "Reunión con Cliente Difícil",
            "category": "comunicacion",
            "difficulty": "intermediate",
            "duration_seconds": 420,  # Duración real de la simulación
            "total_steps": 5,
            "completed_steps": 5
        },
        
        # Habilidades practicadas y evaluadas
        "skills_practiced": [
            {
                "skill_id": "comunicacion_asertiva",
                "skill_name": "Comunicación Asertiva",
                "score": 88,
                "improvement": "+12"  # Mejora respecto a simulaciones anteriores
            },
            {
                "skill_id": "resolucion_conflictos",
                "skill_name": "Resolución de Conflictos", 
                "score": 82,
                "improvement": "+5"
            },
            {
                "skill_id": "negociacion",
                "skill_name": "Negociación",
                "score": 85,
                "improvement": "+8"
            }
        ],
        
        # Decisiones tomadas durante la simulación
        "choices_made": [
            {
                "step": 1,
                "choice_id": "approach_calm",
                "choice_text": "Mantener la calma y escuchar activamente",
                "points_earned": 20
            },
            {
                "step": 2,
                "choice_id": "empathy_response",
                "choice_text": "Mostrar empatía hacia las preocupaciones del cliente",
                "points_earned": 18
            },
            {
                "step": 3,
                "choice_id": "solution_focused",
                "choice_text": "Proponer soluciones concretas",
                "points_earned": 22
            },
            {
                "step": 4,
                "choice_id": "follow_up",
                "choice_text": "Establecer seguimiento claro",
                "points_earned": 15
            },
            {
                "step": 5,
                "choice_id": "relationship_maintenance",
                "choice_text": "Reforzar la relación comercial",
                "points_earned": 10
            }
        ],
        
        # Logros y badges desbloqueados
        "achievements": [
            {
                "achievement_id": "first_difficult_client",
                "name": "Primer Cliente Difícil",
                "description": "Completaste tu primera simulación de cliente difícil",
                "points_awarded": 50,
                "badge_icon": "🏆"
            }
        ],
        
        # Progreso y estadísticas
        "progress_data": {
            "total_simulations_completed": 12,
            "total_points_earned": 1250,
            "current_level": 3,
            "points_to_next_level": 150,
            "streak_days": 5,  # Días consecutivos practicando
            "weekly_progress": 85  # Porcentaje de objetivo semanal cumplido
        },
        
        # Datos para analytics y gamificación
        "gamification": {
            "experience_points": 85,
            "coins_earned": 25,
            "energy_consumed": 10,
            "energy_remaining": 85,
            "daily_goal_progress": 60  # Porcentaje del objetivo diario
        },
        
        # Feedback y recomendaciones
        "feedback": {
            "overall_performance": "Excelente",
            "strengths": [
                "Mantuviste la calma bajo presión",
                "Mostraste gran empatía",
                "Propusiste soluciones creativas"
            ],
            "areas_for_improvement": [
                "Podrías ser más específico en los seguimientos",
                "Considera explorar más opciones antes de decidir"
            ],
            "next_recommended_simulation": "sim_789",
            "next_recommended_skill": "liderazgo_equipos"
        },
        
        # Metadatos del evento
        "event_metadata": {
            "timestamp": datetime.now().isoformat(),
            "source_service": "soft-skills-practice-service",
            "target_service": "user-profile-service",
            "event_version": "1.0",
            "correlation_id": f"sim_completion_{user_id}_{int(datetime.now().timestamp())}",
            "session_id": f"session_{user_id}_20250705"
        }
    }
    
    # Agregar datos adicionales si se proporcionan
    if additional_data:
        message.update(additional_data)
    
    return message

def send_simulation_completion_to_queue(user_id: str, simulation_id: str, score: int):
    """
    Enviar mensaje de simulación completada a la cola de Redis
    """
    print("📤 ENVIANDO MENSAJE DE SIMULACIÓN COMPLETADA")
    print("=" * 50)
    
    try:
        r = redis.Redis(host='localhost', port=6379, decode_responses=True)
        
        # Crear mensaje completo
        message = create_simulation_completion_message(user_id, simulation_id, score)
        
        # Enviar a múltiples colas para diferentes servicios
        queues = [
            "queue:user_profile_updates",      # Para actualizar perfil del usuario
            "queue:analytics_events",          # Para analytics y métricas
            "queue:notification_triggers",     # Para generar notificaciones
            "queue:gamification_updates"       # Para sistema de gamificación
        ]
        
        for queue in queues:
            r.lpush(queue, json.dumps(message))
            print(f"✅ Mensaje enviado a {queue}")
        
        # También publicar en canal para notificaciones en tiempo real
        r.publish(f"user_events:{user_id}", json.dumps({
            "type": "simulation_completed",
            "user_id": user_id,
            "score": score,
            "message": f"¡Simulación completada con {score} puntos!",
            "timestamp": datetime.now().isoformat()
        }))
        print(f"✅ Notificación en tiempo real publicada para usuario {user_id}")
        
        print(f"\n📋 DATOS ENVIADOS AL MICROSERVICIO:")
        print(f"   👤 Usuario: {user_id}")
        print(f"   🎯 Puntuación: {score}/100")
        print(f"   🎮 Simulación: {simulation_id}")
        print(f"   🏆 Logros desbloqueados: {len(message['achievements'])}")
        print(f"   💪 Habilidades evaluadas: {len(message['skills_practiced'])}")
        print(f"   📈 XP ganados: {message['gamification']['experience_points']}")
        print(f"   🪙 Monedas ganadas: {message['gamification']['coins_earned']}")
        
        r.close()
        return True
        
    except Exception as e:
        print(f"❌ Error enviando mensaje: {e}")
        return False

def simulate_microservice_receiving_message():
    """
    Simular cómo el microservicio receptor procesaría el mensaje
    """
    print("\n📥 SIMULACIÓN: MICROSERVICIO RECEPTOR PROCESANDO MENSAJE")
    print("=" * 60)
    
    try:
        r = redis.Redis(host='localhost', port=6379, decode_responses=True)
        
        # Simular que el microservicio de perfil de usuario recibe el mensaje
        message_json = r.rpop("queue:user_profile_updates")
        
        if message_json:
            message = json.loads(message_json)
            
            print("🔍 Datos recibidos por el microservicio de perfil:")
            print(f"   👤 ID Usuario: {message['user_id']}")
            print(f"   🎯 Puntuación: {message['score']}")
            print(f"   📊 Porcentaje: {message['percentage']}%")
            print(f"   ⏱️  Duración: {message['simulation_data']['duration_seconds']} segundos")
            
            print("\n💪 Habilidades a actualizar en el perfil:")
            for skill in message['skills_practiced']:
                print(f"   • {skill['skill_name']}: {skill['score']} ({skill['improvement']})")
            
            print("\n🏆 Logros a agregar al perfil:")
            for achievement in message['achievements']:
                print(f"   • {achievement['name']}: +{achievement['points_awarded']} puntos")
            
            print("\n📈 Progreso del usuario:")
            progress = message['progress_data']
            print(f"   • Total simulaciones: {progress['total_simulations_completed']}")
            print(f"   • Puntos totales: {progress['total_points_earned']}")
            print(f"   • Nivel actual: {progress['current_level']}")
            print(f"   • Racha: {progress['streak_days']} días")
            
            print("\n🎮 Datos de gamificación:")
            gamif = message['gamification']
            print(f"   • XP ganados: {gamif['experience_points']}")
            print(f"   • Monedas: {gamif['coins_earned']}")
            print(f"   • Energía restante: {gamif['energy_remaining']}")
            
            print("\n📝 Feedback para mostrar al usuario:")
            feedback = message['feedback']
            print(f"   • Rendimiento: {feedback['overall_performance']}")
            print(f"   • Fortalezas: {len(feedback['strengths'])} identificadas")
            print(f"   • Áreas de mejora: {len(feedback['areas_for_improvement'])} identificadas")
            print(f"   • Próxima simulación recomendada: {feedback['next_recommended_simulation']}")
            
            print("\n✅ El microservicio puede actualizar completamente el perfil del usuario")
            return True
        else:
            print("❌ No hay mensajes en la cola")
            return False
            
    except Exception as e:
        print(f"❌ Error procesando mensaje: {e}")
        return False
    finally:
        r.close()

def show_message_structure():
    """
    Mostrar la estructura completa del mensaje
    """
    print("\n📋 ESTRUCTURA COMPLETA DEL MENSAJE ENTRE MICROSERVICIOS")
    print("=" * 60)
    
    # Crear mensaje de ejemplo
    sample_message = create_simulation_completion_message(
        user_id="user_123",
        simulation_id="sim_456", 
        score=85
    )
    
    print("📤 El mensaje JSON que se envía contiene:")
    print("\n🔑 DATOS PRINCIPALES:")
    print(f"   • user_id: {sample_message['user_id']}")
    print(f"   • simulation_id: {sample_message['simulation_id']}")
    print(f"   • score: {sample_message['score']}")
    print(f"   • percentage: {sample_message['percentage']}%")
    
    print("\n🎮 DATOS DE LA SIMULACIÓN:")
    sim_data = sample_message['simulation_data']
    print(f"   • title: {sim_data['title']}")
    print(f"   • category: {sim_data['category']}")
    print(f"   • difficulty: {sim_data['difficulty']}")
    print(f"   • duration: {sim_data['duration_seconds']} segundos")
    
    print("\n💪 HABILIDADES EVALUADAS:")
    for skill in sample_message['skills_practiced']:
        print(f"   • {skill['skill_name']}: {skill['score']} puntos")
    
    print("\n🏆 LOGROS DESBLOQUEADOS:")
    for achievement in sample_message['achievements']:
        print(f"   • {achievement['name']}: +{achievement['points_awarded']} puntos")
    
    print("\n📊 PROGRESO Y GAMIFICACIÓN:")
    progress = sample_message['progress_data']
    gamif = sample_message['gamification']
    print(f"   • Nivel actual: {progress['current_level']}")
    print(f"   • XP ganados: {gamif['experience_points']}")
    print(f"   • Monedas ganadas: {gamif['coins_earned']}")
    
    print("\n🎯 TOTAL DE CAMPOS EN EL MENSAJE:")
    print(f"   • Campos principales: {len(sample_message)}")
    print(f"   • Habilidades evaluadas: {len(sample_message['skills_practiced'])}")
    print(f"   • Decisiones registradas: {len(sample_message['choices_made'])}")
    print(f"   • Logros obtenidos: {len(sample_message['achievements'])}")

def main():
    """
    Demostración completa del sistema de mensajes entre microservicios
    """
    print("🚀 DEMOSTRACIÓN: MENSAJES ENTRE MICROSERVICIOS")
    print("🔄 Simulación → Perfil de Usuario")
    print("=" * 70)
    
    # 1. Mostrar estructura del mensaje
    show_message_structure()
    
    # 2. Enviar mensaje de simulación completada
    print("\n" + "=" * 70)
    success = send_simulation_completion_to_queue(
        user_id="user_123",
        simulation_id="sim_456",
        score=85
    )
    
    if success:
        # 3. Simular recepción por el microservicio
        print("\n" + "=" * 70)
        simulate_microservice_receiving_message()
    
    print("\n" + "=" * 70)
    print("✅ DEMOSTRACIÓN COMPLETADA")
    print("📤 El microservicio de simulaciones envía:")
    print("   • ID del usuario ✅")
    print("   • Puntuación obtenida ✅") 
    print("   • Datos completos de la simulación ✅")
    print("   • Habilidades evaluadas ✅")
    print("   • Progreso y logros ✅")
    print("   • Datos de gamificación ✅")
    print("   • Feedback detallado ✅")
    
    print("\n📥 El microservicio de perfil recibe:")
    print("   • Toda la información necesaria para actualizar el perfil")
    print("   • Datos para generar notificaciones")
    print("   • Información para analytics")
    print("   • Progreso de gamificación")

if __name__ == "__main__":
    main()
