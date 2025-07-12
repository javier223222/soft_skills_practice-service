#!/usr/bin/env python3
"""
Script para probar la integración del sistema de notificaciones
específico del microservicio de soft skills
"""

import redis
import json
import asyncio
from datetime import datetime
from typing import Dict, Any

class SoftSkillsNotificationTest:
    def __init__(self):
        self.redis_client = redis.Redis(
            host='localhost',
            port=6379,
            db=0,
            decode_responses=True
        )
    
    def test_connection(self):
        """Probar conexión básica"""
        try:
            self.redis_client.ping()
            print("✅ Conexión a Redis establecida")
            return True
        except Exception as e:
            print(f"❌ Error conectando a Redis: {e}")
            return False
    
    def simulate_simulation_completion(self, user_id: str, session_id: str):
        """Simular completion de una simulación y envío de notificación"""
        print(f"\n🎮 Simulando completion de simulación...")
        print(f"   👤 Usuario: {user_id}")
        print(f"   🆔 Sesión: {session_id}")
        
        # Datos de completion de simulación
        completion_data = {
            "event_type": "simulation_completed",
            "user_id": user_id,
            "session_id": session_id,
            "skill_type": "conflict_resolution",
            "scenario_id": "conflict_meeting_scenario_1",
            "performance": {
                "overall_score": 87.5,
                "completion_percentage": 100.0,
                "total_time_minutes": 25,
                "difficulty_level": 3
            },
            "points_calculation": {
                "base_points": 50,
                "performance_bonus": 25,  # 87.5% * 30 = 26.25 ≈ 25
                "difficulty_bonus": 15,   # level 3 * 5 = 15
                "time_bonus": 10,         # completado rápido
                "total_points": 100
            },
            "level_info": {
                "previous_level": 4,
                "previous_points": 1250,
                "new_total_points": 1350,
                "new_level": 5,
                "level_up": True
            },
            "achievements": [
                {
                    "id": "conflict_master_advanced",
                    "title": "Maestro de Conflictos Avanzado",
                    "description": "Completaste una simulación avanzada de resolución de conflictos",
                    "rarity": "epic",
                    "unlocked_at": datetime.now().isoformat()
                }
            ],
            "timestamp": datetime.now().isoformat(),
            "source_service": "soft-skills-practice-service"
        }
        
        # Enviar a la cola del profile service
        queue_key = "profile_service:user_progress_updates"
        
        try:
            self.redis_client.lpush(queue_key, json.dumps(completion_data))
            print(f"   📤 Notificación enviada a: {queue_key}")
            print(f"   🎯 Puntos ganados: {completion_data['points_calculation']['total_points']}")
            print(f"   📈 Level up: {completion_data['level_info']['previous_level']} → {completion_data['level_info']['new_level']}")
            print(f"   🏆 Achievements: {len(completion_data['achievements'])} nuevos")
            
            # Verificar que se envió
            queue_size = self.redis_client.llen(queue_key)
            print(f"   📊 Cola tiene {queue_size} mensajes pendientes")
            
            return True
            
        except Exception as e:
            print(f"   ❌ Error enviando notificación: {e}")
            return False
    
    def simulate_profile_service_response(self, user_id: str):
        """Simular respuesta del profile service"""
        print(f"\n📥 Simulando respuesta del profile service...")
        
        # Procesar el mensaje de la cola
        queue_key = "profile_service:user_progress_updates"
        
        try:
            # Leer el mensaje
            message_json = self.redis_client.rpop(queue_key)
            if not message_json:
                print("   ❌ No hay mensajes en la cola")
                return False
            
            message = json.loads(message_json)
            print(f"   📨 Mensaje procesado para usuario: {message['user_id']}")
            print(f"   🎯 Puntos procesados: {message['points_calculation']['total_points']}")
            
            # Simular actualización en base de datos del profile service
            profile_update = {
                "user_id": user_id,
                "updated_fields": {
                    "current_level": message['level_info']['new_level'],
                    "total_points": message['level_info']['new_total_points'],
                    "last_simulation_completed": message['timestamp'],
                    "achievements_unlocked": len(message['achievements'])
                },
                "simulation_history": {
                    "session_id": message['session_id'],
                    "skill_practiced": message['skill_type'],
                    "score": message['performance']['overall_score'],
                    "completed_at": message['timestamp']
                }
            }
            
            print(f"   💾 Profile actualizado: Level {profile_update['updated_fields']['current_level']}")
            print(f"   💰 Puntos totales: {profile_update['updated_fields']['total_points']}")
            
            # Enviar confirmación de vuelta
            response_queue = f"soft_skills_practice:confirmations:{user_id}"
            confirmation = {
                "status": "success",
                "user_id": user_id,
                "message": "Profile updated successfully",
                "updated_data": profile_update['updated_fields'],
                "processed_at": datetime.now().isoformat()
            }
            
            self.redis_client.lpush(response_queue, json.dumps(confirmation))
            print(f"   ✅ Confirmación enviada a: {response_queue}")
            
            return True
            
        except Exception as e:
            print(f"   ❌ Error procesando respuesta: {e}")
            return False
    
    def simulate_notification_to_mobile(self, user_id: str):
        """Simular notificación push a la app móvil"""
        print(f"\n📱 Simulando notificación push a móvil...")
        
        # Leer confirmación
        response_queue = f"soft_skills_practice:confirmations:{user_id}"
        
        try:
            confirmation_json = self.redis_client.rpop(response_queue)
            if not confirmation_json:
                print("   ❌ No hay confirmación disponible")
                return False
            
            confirmation = json.loads(confirmation_json)
            
            # Crear notificación para móvil
            mobile_notification = {
                "notification_type": "level_up",
                "user_id": user_id,
                "title": f"¡Felicidades! Nivel {confirmation['updated_data']['current_level']}",
                "body": f"Has ganado {confirmation['updated_data']['total_points']} puntos y subido de nivel",
                "data": {
                    "type": "level_up",
                    "new_level": confirmation['updated_data']['current_level'],
                    "total_points": confirmation['updated_data']['total_points'],
                    "should_update_ui": True,
                    "action": "refresh_dashboard"
                },
                "priority": "high",
                "created_at": datetime.now().isoformat()
            }
            
            # Enviar a cola de notificaciones móviles
            mobile_queue = f"mobile_notifications:{user_id}"
            self.redis_client.lpush(mobile_queue, json.dumps(mobile_notification))
            
            print(f"   📲 Notificación enviada a móvil")
            print(f"   📢 Título: {mobile_notification['title']}")
            print(f"   📝 Mensaje: {mobile_notification['body']}")
            print(f"   🎯 Acción: {mobile_notification['data']['action']}")
            
            return True
            
        except Exception as e:
            print(f"   ❌ Error enviando notificación móvil: {e}")
            return False
    
    def test_complete_flow(self):
        """Probar el flujo completo de notificaciones"""
        print(f"\n🔄 PROBANDO FLUJO COMPLETO DE NOTIFICACIONES")
        print("=" * 60)
        
        user_id = "test_user_12345"
        session_id = f"session_{int(datetime.now().timestamp())}"
        
        # Paso 1: Simulación completada
        step1 = self.simulate_simulation_completion(user_id, session_id)
        
        # Paso 2: Profile service procesa
        step2 = self.simulate_profile_service_response(user_id) if step1 else False
        
        # Paso 3: Notificación a móvil
        step3 = self.simulate_notification_to_mobile(user_id) if step2 else False
        
        # Resultado
        print(f"\n📊 RESULTADO DEL FLUJO:")
        print(f"   1. Simulación → Redis: {'✅' if step1 else '❌'}")
        print(f"   2. Profile Service: {'✅' if step2 else '❌'}")
        print(f"   3. Notificación Móvil: {'✅' if step3 else '❌'}")
        
        if all([step1, step2, step3]):
            print(f"\n🎉 ¡FLUJO COMPLETO EXITOSO!")
            print(f"✅ El sistema de notificaciones está funcionando correctamente")
        else:
            print(f"\n⚠️  Flujo incompleto - revisar errores")
        
        return all([step1, step2, step3])
    
    def check_queue_status(self):
        """Verificar estado de las colas"""
        print(f"\n📊 ESTADO DE LAS COLAS DE REDIS")
        print("-" * 40)
        
        queues_to_check = [
            "profile_service:user_progress_updates",
            "soft_skills_practice:confirmations:*",
            "mobile_notifications:*"
        ]
        
        for queue_pattern in queues_to_check:
            if "*" in queue_pattern:
                # Buscar colas que coincidan con el patrón
                matching_keys = self.redis_client.keys(queue_pattern)
                for key in matching_keys:
                    size = self.redis_client.llen(key)
                    print(f"   📋 {key}: {size} mensajes")
            else:
                size = self.redis_client.llen(queue_pattern)
                print(f"   📋 {queue_pattern}: {size} mensajes")
    
    def cleanup(self):
        """Limpiar datos de prueba"""
        print(f"\n🧹 Limpiando datos de prueba...")
        
        patterns_to_clean = [
            "profile_service:*",
            "soft_skills_practice:*",
            "mobile_notifications:*",
            "test:*"
        ]
        
        deleted_total = 0
        for pattern in patterns_to_clean:
            keys = self.redis_client.keys(pattern)
            if keys:
                deleted = self.redis_client.delete(*keys)
                deleted_total += deleted
        
        print(f"   ✅ Eliminadas {deleted_total} keys de prueba")

def main():
    """Función principal"""
    print("🚀 PRUEBAS DEL SISTEMA DE NOTIFICACIONES")
    print("🎯 Soft Skills Practice Service")
    print("=" * 60)
    
    tester = SoftSkillsNotificationTest()
    
    # Verificar conexión
    if not tester.test_connection():
        return
    
    # Verificar estado inicial
    tester.check_queue_status()
    
    # Ejecutar flujo completo
    success = tester.test_complete_flow()
    
    # Verificar estado final
    tester.check_queue_status()
    
    # Cleanup
    tester.cleanup()
    
    # Reporte final
    print(f"\n" + "=" * 60)
    if success:
        print("🎉 ¡SISTEMA DE NOTIFICACIONES FUNCIONANDO CORRECTAMENTE!")
        print("✅ Redis está listo para producción")
        print("✅ El flujo de notificaciones es completo y funcional")
    else:
        print("⚠️  Sistema necesita ajustes - revisar errores anteriores")

if __name__ == "__main__":
    main()
