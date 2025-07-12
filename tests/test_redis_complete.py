#!/usr/bin/env python3
"""
Script para probar Redis - Conexión, Message Queue y Notificaciones
"""

import redis
import json
import time
from datetime import datetime
from typing import Dict, Any

class RedisConnectionTest:
    def __init__(self, host='localhost', port=6379, db=0):
        self.host = host
        self.port = port
        self.db = db
        self.redis_client = None
        
    def connect(self):
        """Conectar a Redis"""
        try:
            self.redis_client = redis.Redis(
                host=self.host,
                port=self.port,
                db=self.db,
                decode_responses=True
            )
            # Test básico de conexión
            self.redis_client.ping()
            print(f"✅ Conexión exitosa a Redis {self.host}:{self.port}")
            return True
        except Exception as e:
            print(f"❌ Error conectando a Redis: {e}")
            return False
    
    def test_basic_operations(self):
        """Probar operaciones básicas de Redis"""
        print(f"\n📋 Probando operaciones básicas...")
        
        try:
            # SET y GET
            test_key = "test:soft_skills"
            test_value = "Hello from Soft Skills Service!"
            
            self.redis_client.set(test_key, test_value)
            retrieved_value = self.redis_client.get(test_key)
            
            print(f"   SET/GET: ✅ '{test_key}' = '{retrieved_value}'")
            
            # Hash operations
            hash_key = "user:test_123"
            user_data = {
                "name": "Test User",
                "level": "5",
                "points": "1250",
                "last_login": datetime.now().isoformat()
            }
            
            self.redis_client.hset(hash_key, mapping=user_data)
            retrieved_hash = self.redis_client.hgetall(hash_key)
            
            print(f"   HASH: ✅ Usuario almacenado: {retrieved_hash}")
            
            # List operations (para colas)
            queue_key = "notifications:queue"
            notification = {
                "user_id": "test_123",
                "type": "points_earned",
                "data": {"points": 100, "level": 5}
            }
            
            self.redis_client.lpush(queue_key, json.dumps(notification))
            queue_length = self.redis_client.llen(queue_key)
            
            print(f"   LIST/QUEUE: ✅ Cola tiene {queue_length} elementos")
            
            # Cleanup
            self.redis_client.delete(test_key, hash_key)
            
            return True
            
        except Exception as e:
            print(f"   ❌ Error en operaciones básicas: {e}")
            return False
    
    def test_message_queue(self):
        """Probar funcionalidad de cola de mensajes"""
        print(f"\n📨 Probando Message Queue...")
        
        try:
            queue_name = "soft_skills:notifications"
            
            # Simular notificaciones de puntos
            notifications = [
                {
                    "id": f"notif_{int(time.time())}_{i}",
                    "user_id": f"user_{i}",
                    "type": "simulation_completed",
                    "data": {
                        "points_earned": 50 + (i * 10),
                        "new_level": 3 + i,
                        "simulation_id": f"sim_{i}",
                        "skill_type": "communication"
                    },
                    "timestamp": datetime.now().isoformat(),
                    "status": "pending"
                }
                for i in range(1, 4)
            ]
            
            # Enviar notificaciones a la cola
            for notification in notifications:
                self.redis_client.lpush(queue_name, json.dumps(notification))
                print(f"   📤 Enviado: {notification['type']} para {notification['user_id']}")
            
            # Verificar tamaño de la cola
            queue_size = self.redis_client.llen(queue_name)
            print(f"   📊 Cola tiene {queue_size} mensajes pendientes")
            
            # Procesar mensajes (simular consumer)
            processed = 0
            while self.redis_client.llen(queue_name) > 0:
                message_json = self.redis_client.rpop(queue_name)
                if message_json:
                    message = json.loads(message_json)
                    print(f"   📥 Procesado: {message['type']} - {message['data']['points_earned']} puntos")
                    processed += 1
            
            print(f"   ✅ Procesados {processed} mensajes exitosamente")
            return True
            
        except Exception as e:
            print(f"   ❌ Error en message queue: {e}")
            return False
    
    def test_points_notification_simulation(self):
        """Simular el sistema de notificaciones de puntos"""
        print(f"\n🎯 Simulando Sistema de Notificaciones de Puntos...")
        
        try:
            # Simular completion de simulación
            user_id = "user_test_123"
            simulation_data = {
                "session_id": "session_20250705_160055",
                "user_id": user_id,
                "skill_type": "conflict_resolution",
                "completion_status": "completed",
                "points_earned": 85,
                "old_level": 4,
                "new_level": 5,
                "achievements_unlocked": ["conflict_master"],
                "completed_at": datetime.now().isoformat()
            }
            
            # Enviar notificación al profile service
            profile_queue = "profile_service:notifications"
            notification = {
                "event_type": "user_progress_update",
                "user_id": user_id,
                "data": simulation_data,
                "timestamp": datetime.now().isoformat(),
                "source_service": "soft_skills_practice"
            }
            
            self.redis_client.lpush(profile_queue, json.dumps(notification))
            print(f"   📤 Notificación enviada al profile service")
            print(f"   📊 Puntos ganados: {simulation_data['points_earned']}")
            print(f"   📈 Nivel actualizado: {simulation_data['old_level']} → {simulation_data['new_level']}")
            print(f"   🏆 Logros desbloqueados: {simulation_data['achievements_unlocked']}")
            
            # Verificar que llegó
            queue_size = self.redis_client.llen(profile_queue)
            print(f"   ✅ Cola del profile service tiene {queue_size} mensajes")
            
            # Simular respuesta del profile service
            response_queue = f"soft_skills_practice:responses:{user_id}"
            response = {
                "status": "success",
                "user_id": user_id,
                "updated_data": {
                    "current_level": simulation_data['new_level'],
                    "total_points": 1335,  # 1250 + 85
                    "achievements_count": 9
                },
                "processed_at": datetime.now().isoformat()
            }
            
            self.redis_client.lpush(response_queue, json.dumps(response))
            print(f"   📥 Respuesta simulada del profile service recibida")
            
            # Cleanup
            self.redis_client.delete(profile_queue, response_queue)
            
            return True
            
        except Exception as e:
            print(f"   ❌ Error en simulación de notificaciones: {e}")
            return False
    
    def test_redis_info(self):
        """Obtener información del servidor Redis"""
        print(f"\n📊 Información del servidor Redis...")
        
        try:
            info = self.redis_client.info()
            
            print(f"   📌 Versión Redis: {info.get('redis_version')}")
            print(f"   💾 Memoria usada: {info.get('used_memory_human')}")
            print(f"   🔗 Conexiones: {info.get('connected_clients')}")
            print(f"   ⏱️  Uptime: {info.get('uptime_in_seconds')} segundos")
            print(f"   🗄️  Database 0 keys: {info.get('db0', {}).get('keys', 0) if 'db0' in info else 0}")
            
            return True
            
        except Exception as e:
            print(f"   ❌ Error obteniendo info de Redis: {e}")
            return False
    
    def cleanup_test_data(self):
        """Limpiar datos de prueba"""
        print(f"\n🧹 Limpiando datos de prueba...")
        
        try:
            # Buscar y eliminar keys de prueba
            test_patterns = [
                "test:*",
                "user:test_*",
                "notifications:*",
                "soft_skills:*",
                "profile_service:*"
            ]
            
            deleted_count = 0
            for pattern in test_patterns:
                keys = self.redis_client.keys(pattern)
                if keys:
                    deleted = self.redis_client.delete(*keys)
                    deleted_count += deleted
            
            print(f"   ✅ Eliminadas {deleted_count} keys de prueba")
            
        except Exception as e:
            print(f"   ❌ Error en cleanup: {e}")

def main():
    """Función principal"""
    print("🚀 PRUEBAS COMPLETAS DE REDIS")
    print("=" * 50)
    
    # Inicializar tester
    redis_test = RedisConnectionTest()
    
    # Ejecutar pruebas
    if not redis_test.connect():
        print("❌ No se pudo conectar a Redis. Verifica que esté ejecutándose.")
        return
    
    tests_results = []
    
    # Test 1: Operaciones básicas
    tests_results.append(("Operaciones Básicas", redis_test.test_basic_operations()))
    
    # Test 2: Message Queue
    tests_results.append(("Message Queue", redis_test.test_message_queue()))
    
    # Test 3: Sistema de notificaciones
    tests_results.append(("Notificaciones de Puntos", redis_test.test_points_notification_simulation()))
    
    # Test 4: Info del servidor
    tests_results.append(("Información del Servidor", redis_test.test_redis_info()))
    
    # Cleanup
    redis_test.cleanup_test_data()
    
    # Reporte final
    print("\n" + "=" * 50)
    print("📋 REPORTE FINAL DE PRUEBAS")
    print("=" * 50)
    
    passed = 0
    for test_name, result in tests_results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name:<30} {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 Resultados: {passed}/{len(tests_results)} pruebas exitosas")
    
    if passed == len(tests_results):
        print("🎉 ¡TODAS LAS PRUEBAS DE REDIS EXITOSAS!")
        print("✅ Redis está listo para el sistema de notificaciones")
    else:
        print("⚠️  Algunas pruebas fallaron. Revisa la configuración.")

if __name__ == "__main__":
    main()
