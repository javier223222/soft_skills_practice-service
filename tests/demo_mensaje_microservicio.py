#!/usr/bin/env python3
"""
Demostración simple: ¿Qué datos recibe el microservicio cuando termina una simulación?
"""

import redis
import json
from datetime import datetime

def mensaje_minimo_simulacion_completada():
    """
    Versión mínima del mensaje que SIEMPRE se envía
    """
    return {
        # DATOS OBLIGATORIOS que siempre se envían
        "type": "simulation_completed",
        "user_id": "user_123",           # ✅ ID del usuario
        "simulation_id": "sim_456",      # ✅ ID de la simulación
        "score": 85,                     # ✅ Puntuación obtenida
        "timestamp": datetime.now().isoformat()
    }

def mensaje_completo_simulacion_completada():
    """
    Versión completa con todos los datos útiles
    """
    return {
        # DATOS BÁSICOS OBLIGATORIOS
        "type": "simulation_completed", 
        "user_id": "user_123",          # ✅ ID del usuario
        "simulation_id": "sim_456",     # ✅ ID de la simulación
        "score": 85,                    # ✅ Puntuación obtenida (0-100)
        "max_score": 100,
        "percentage": 85.0,
        "timestamp": datetime.now().isoformat(),
        
        # DATOS ADICIONALES ÚTILES
        "simulation_title": "Reunión con Cliente Difícil",
        "simulation_category": "comunicacion",
        "difficulty": "intermediate",
        "duration_seconds": 420,
        "total_steps": 5,
        "completed_steps": 5,
        
        # HABILIDADES PRACTICADAS
        "skills_evaluated": [
            {"skill_name": "Comunicación Asertiva", "score": 88},
            {"skill_name": "Resolución de Conflictos", "score": 82},
            {"skill_name": "Negociación", "score": 85}
        ],
        
        # PROGRESO DEL USUARIO
        "user_progress": {
            "total_simulations": 12,
            "current_level": 3,
            "total_points": 1250,
            "experience_gained": 85
        },
        
        # LOGROS DESBLOQUEADOS
        "achievements_unlocked": [
            {"name": "Primer Cliente Difícil", "points": 50}
        ]
    }

def simular_envio_y_recepcion():
    """
    Simular el envío y recepción del mensaje entre microservicios
    """
    print("🚀 SIMULACIÓN: ¿QUE DATOS RECIBE EL OTRO MICROSERVICIO?")
    print("=" * 60)
    
    # Conectar a Redis
    r = redis.Redis(host='localhost', port=6379, decode_responses=True)
    
    # 1. ENVIAR mensaje desde microservicio de simulaciones
    print("📤 MICROSERVICIO DE SIMULACIONES ENVÍA:")
    
    mensaje = mensaje_completo_simulacion_completada()
    
    # Enviar a la cola del microservicio de perfil
    r.lpush("queue:user_profile_service", json.dumps(mensaje))
    
    print(f"   👤 user_id: {mensaje['user_id']}")
    print(f"   🎯 score: {mensaje['score']}")
    print(f"   🎮 simulation_id: {mensaje['simulation_id']}")
    print(f"   📊 percentage: {mensaje['percentage']}%")
    print(f"   ⏱️  duration: {mensaje['duration_seconds']} segundos")
    print(f"   💪 skills evaluated: {len(mensaje['skills_evaluated'])}")
    print(f"   🏆 achievements: {len(mensaje['achievements_unlocked'])}")
    
    # 2. RECIBIR mensaje en microservicio de perfil
    print("\n📥 MICROSERVICIO DE PERFIL RECIBE:")
    
    mensaje_recibido = r.rpop("queue:user_profile_service")
    if mensaje_recibido:
        data = json.loads(mensaje_recibido)
        
        print(f"   ✅ ID Usuario: {data['user_id']}")
        print(f"   ✅ Puntuación: {data['score']}/100")
        print(f"   ✅ Simulación: {data['simulation_id']}")
        print(f"   ✅ Título: {data['simulation_title']}")
        print(f"   ✅ Categoría: {data['simulation_category']}")
        print(f"   ✅ Duración: {data['duration_seconds']} segundos")
        
        print("\n   💪 Habilidades evaluadas:")
        for skill in data['skills_evaluated']:
            print(f"      • {skill['skill_name']}: {skill['score']} puntos")
        
        print("\n   📈 Progreso del usuario:")
        progress = data['user_progress']
        print(f"      • Total simulaciones: {progress['total_simulations']}")
        print(f"      • Nivel actual: {progress['current_level']}")
        print(f"      • Puntos totales: {progress['total_points']}")
        print(f"      • XP ganados: {progress['experience_gained']}")
        
        print("\n   🏆 Logros desbloqueados:")
        for achievement in data['achievements_unlocked']:
            print(f"      • {achievement['name']}: +{achievement['points']} puntos")
    
    r.close()

def ejemplo_uso_datos():
    """
    Ejemplo de cómo el microservicio de perfil usaría estos datos
    """
    print("\n🔧 ¿CÓMO USA ESTOS DATOS EL MICROSERVICIO DE PERFIL?")
    print("=" * 60)
    
    print("El microservicio de perfil puede:")
    print("✅ Actualizar el perfil del usuario con:")
    print("   • Nueva puntuación total")
    print("   • Progreso en habilidades específicas")
    print("   • Nuevo nivel alcanzado")
    print("   • Logros desbloqueados")
    
    print("\n✅ Generar notificaciones:")
    print("   • 'Simulación completada con 85 puntos'")
    print("   • 'Nueva insignia desbloqueada: Primer Cliente Difícil'")
    print("   • 'Has subido al nivel 3'")
    
    print("\n✅ Actualizar estadísticas:")
    print("   • Incrementar contador de simulaciones")
    print("   • Actualizar promedio de puntuaciones")
    print("   • Registrar tiempo de práctica")
    
    print("\n✅ Enviar datos a otros servicios:")
    print("   • Analytics: Para métricas de uso")
    print("   • Notificaciones: Para apps móviles")
    print("   • Gamificación: Para sistema de puntos")

def main():
    """
    Demostración principal
    """
    print("🎯 RESPUESTA A TU PREGUNTA:")
    print("¿El microservicio recibe ID del usuario y puntuación?")
    print("=" * 60)
    
    print("✅ SÍ, el microservicio receptor recibe:")
    print("   • user_id (ID del usuario)")
    print("   • score (puntuación obtenida)")
    print("   • Y MUCHO MÁS...")
    print()
    
    # Mostrar mensaje mínimo
    mensaje_min = mensaje_minimo_simulacion_completada()
    print("📋 DATOS MÍNIMOS GARANTIZADOS:")
    for key, value in mensaje_min.items():
        print(f"   • {key}: {value}")
    
    print("\n📋 PERO NORMALMENTE SE ENVÍAN MUCHOS MÁS DATOS:")
    
    # Simular envío completo
    simular_envio_y_recepcion()
    
    # Explicar uso
    ejemplo_uso_datos()
    
    print("\n🎉 CONCLUSIÓN:")
    print("El microservicio receptor NO SOLO recibe user_id y score,")
    print("sino un mensaje completo con toda la información necesaria")
    print("para actualizar el perfil del usuario completamente.")

if __name__ == "__main__":
    main()
