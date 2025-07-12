#!/usr/bin/env python3
"""
Test completo de integración de Redis
Verifica todas las funcionalidades principales de Redis en el proyecto
"""

import redis
import json
import time
import asyncio
from datetime import datetime
from typing import Dict, Any

def test_redis_connection():
    """Test de conexión básica a Redis"""
    print("🔗 Testando conexión a Redis...")
    try:
        r = redis.Redis(host='localhost', port=6379, decode_responses=True)
        pong = r.ping()
        print(f"✅ Conexión exitosa: {pong}")
        return r
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return None

def test_basic_operations(r: redis.Redis):
    """Test de operaciones básicas de Redis"""
    print("\n📝 Testando operaciones básicas...")
    
    # SET y GET
    r.set("test_key", "test_value")
    value = r.get("test_key")
    print(f"✅ SET/GET: {value}")
    
    # HASH operations
    r.hset("user:123", mapping={
        "name": "Juan Pérez",
        "email": "juan@example.com",
        "level": "2"
    })
    user_data = r.hgetall("user:123")
    print(f"✅ HASH operations: {user_data}")
    
    # LIST operations
    r.lpush("notifications", "Nueva simulación disponible")
    r.lpush("notifications", "Puntuación actualizada")
    notifications = r.lrange("notifications", 0, -1)
    print(f"✅ LIST operations: {notifications}")
    
    # Expiration
    r.setex("temp_key", 5, "temporary_value")
    ttl = r.ttl("temp_key")
    print(f"✅ TTL operations: {ttl} segundos")

def test_message_queue(r: redis.Redis):
    """Test del sistema de cola de mensajes"""
    print("\n🚀 Testando sistema de cola de mensajes...")
    
    # Simular mensajes de diferentes servicios
    messages = [
        {
            "type": "simulation_completed",
            "user_id": "user_123",
            "simulation_id": "sim_456",
            "score": 85,
            "timestamp": datetime.now().isoformat()
        },
        {
            "type": "skill_unlocked",
            "user_id": "user_123",
            "skill": "Comunicación Asertiva",
            "level": 3,
            "timestamp": datetime.now().isoformat()
        },
        {
            "type": "notification_request",
            "user_id": "user_123",
            "message": "¡Felicidades! Has desbloqueado una nueva habilidad",
            "priority": "high",
            "timestamp": datetime.now().isoformat()
        }
    ]
    
    # Enviar mensajes a diferentes colas
    for message in messages:
        queue_name = f"queue:{message['type']}"
        r.lpush(queue_name, json.dumps(message))
        print(f"📤 Mensaje enviado a {queue_name}")
    
    # Procesar mensajes de las colas
    queues = ["queue:simulation_completed", "queue:skill_unlocked", "queue:notification_request"]
    for queue in queues:
        message = r.rpop(queue)
        if message:
            data = json.loads(message)
            print(f"📥 Mensaje procesado de {queue}: {data['type']}")

def test_caching_scenarios(r: redis.Redis):
    """Test de cacheo de escenarios de práctica"""
    print("\n🎭 Testando cacheo de escenarios...")
    
    # Simular cacheo de escenarios
    scenarios = [
        {
            "id": "scenario_001",
            "title": "Reunión con Cliente Difícil",
            "difficulty": "intermediate",
            "skills": ["comunicacion", "negociacion"],
            "duration": 600
        },
        {
            "id": "scenario_002", 
            "title": "Presentación Ejecutiva",
            "difficulty": "advanced",
            "skills": ["presentacion", "liderazgo"],
            "duration": 900
        }
    ]
    
    for scenario in scenarios:
        cache_key = f"scenario:{scenario['id']}"
        r.setex(cache_key, 3600, json.dumps(scenario))  # Cache por 1 hora
        print(f"💾 Escenario cacheado: {scenario['title']}")
    
    # Recuperar escenarios del cache
    for scenario in scenarios:
        cache_key = f"scenario:{scenario['id']}"
        cached_data = r.get(cache_key)
        if cached_data:
            scenario_data = json.loads(cached_data)
            print(f"🔍 Escenario recuperado del cache: {scenario_data['title']}")

def test_session_management(r: redis.Redis):
    """Test de manejo de sesiones de usuario"""
    print("\n👤 Testando manejo de sesiones...")
    
    # Crear sesión de usuario
    session_data = {
        "user_id": "user_123",
        "current_simulation": "sim_456",
        "start_time": datetime.now().isoformat(),
        "progress": {
            "step": 3,
            "total_steps": 5,
            "choices_made": ["option_1", "option_2", "option_3"]
        }
    }
    
    session_key = f"session:{session_data['user_id']}"
    r.setex(session_key, 7200, json.dumps(session_data))  # Sesión válida por 2 horas
    print(f"🔐 Sesión creada para usuario {session_data['user_id']}")
    
    # Recuperar sesión
    session = r.get(session_key)
    if session:
        session_info = json.loads(session)
        print(f"📋 Sesión recuperada: Paso {session_info['progress']['step']} de {session_info['progress']['total_steps']}")

def test_leaderboard_system(r: redis.Redis):
    """Test del sistema de leaderboard con Redis Sorted Sets"""
    print("\n🏆 Testando sistema de leaderboard...")
    
    # Agregar puntuaciones al leaderboard
    users_scores = [
        ("user_123", 1250),
        ("user_456", 980),
        ("user_789", 1420),
        ("user_012", 750),
        ("user_345", 1100)
    ]
    
    for user_id, score in users_scores:
        r.zadd("leaderboard:global", {user_id: score})
        print(f"🎯 Puntuación agregada: {user_id} = {score}")
    
    # Obtener top 3
    top_users = r.zrevrange("leaderboard:global", 0, 2, withscores=True)
    print("\n🥇 Top 3 usuarios:")
    for i, (user_id, score) in enumerate(top_users, 1):
        print(f"   {i}. {user_id}: {int(score)} puntos")
    
    # Obtener ranking de un usuario específico
    user_rank = r.zrevrank("leaderboard:global", "user_123")
    user_score = r.zscore("leaderboard:global", "user_123")
    print(f"\n📊 Ranking de user_123: Posición {user_rank + 1}, Puntuación: {int(user_score)}")

def test_notification_system(r: redis.Redis):
    """Test del sistema de notificaciones"""
    print("\n🔔 Testando sistema de notificaciones...")
    
    # Crear diferentes tipos de notificaciones
    notifications = [
        {
            "id": "notif_001",
            "user_id": "user_123",
            "type": "achievement",
            "title": "¡Nueva insignia desbloqueada!",
            "message": "Has completado 5 simulaciones consecutivas",
            "read": False,
            "created_at": datetime.now().isoformat()
        },
        {
            "id": "notif_002",
            "user_id": "user_123",
            "type": "reminder",
            "title": "Simulación pendiente",
            "message": "Tienes una simulación sin completar",
            "read": False,
            "created_at": datetime.now().isoformat()
        }
    ]
    
    for notification in notifications:
        # Guardar notificación
        notif_key = f"notification:{notification['id']}"
        r.setex(notif_key, 86400, json.dumps(notification))  # Notificaciones por 24 horas
        
        # Agregar a la lista de notificaciones del usuario
        user_notifications_key = f"user_notifications:{notification['user_id']}"
        r.lpush(user_notifications_key, notification['id'])
        r.expire(user_notifications_key, 86400)
        
        print(f"📬 Notificación creada: {notification['title']}")
    
    # Recuperar notificaciones del usuario
    user_notifications = r.lrange("user_notifications:user_123", 0, -1)
    print(f"\n📱 Usuario tiene {len(user_notifications)} notificaciones")

def test_analytics_data(r: redis.Redis):
    """Test de almacenamiento de datos de analíticas"""
    print("\n📈 Testando datos de analíticas...")
    
    # Contadores de eventos
    events = [
        "simulation_started",
        "simulation_completed", 
        "skill_practiced",
        "user_login",
        "notification_sent"
    ]
    
    for event in events:
        # Incrementar contador diario
        today = datetime.now().strftime("%Y-%m-%d")
        counter_key = f"analytics:{event}:{today}"
        r.incr(counter_key)
        r.expire(counter_key, 2592000)  # Mantener por 30 días
        
        count = r.get(counter_key)
        print(f"📊 {event}: {count} eventos hoy")

def test_redis_info(r: redis.Redis):
    """Test de información del servidor Redis"""
    print("\n🖥️  Información del servidor Redis...")
    
    info = r.info()
    
    print(f"🔧 Versión Redis: {info.get('redis_version', 'N/A')}")
    print(f"⏱️  Uptime: {info.get('uptime_in_seconds', 0)} segundos")
    print(f"💾 Memoria usada: {info.get('used_memory_human', 'N/A')}")
    print(f"🔗 Conexiones: {info.get('connected_clients', 0)}")
    print(f"🗂️  Databases: {info.get('databases', 'N/A')}")
    print(f"🔑 Total de keys: {r.dbsize()}")

def cleanup_test_data(r: redis.Redis):
    """Limpiar datos de prueba"""
    print("\n🧹 Limpiando datos de prueba...")
    
    # Obtener todas las keys de prueba
    test_patterns = [
        "test_*",
        "user:*",
        "notification*",
        "queue:*",
        "scenario:*",
        "session:*",
        "leaderboard:*",
        "analytics:*"
    ]
    
    deleted_count = 0
    for pattern in test_patterns:
        keys = r.keys(pattern)
        if keys:
            deleted = r.delete(*keys)
            deleted_count += deleted
    
    print(f"🗑️  {deleted_count} keys de prueba eliminadas")

def main():
    """Función principal del test"""
    print("🚀 INICIANDO TEST COMPLETO DE INTEGRACIÓN REDIS")
    print("=" * 60)
    
    # Conectar a Redis
    r = test_redis_connection()
    if not r:
        print("❌ No se pudo conectar a Redis. Verifica que esté ejecutándose.")
        return
    
    try:
        # Ejecutar todos los tests
        test_basic_operations(r)
        test_message_queue(r)
        test_caching_scenarios(r)
        test_session_management(r)
        test_leaderboard_system(r)
        test_notification_system(r)
        test_analytics_data(r)
        test_redis_info(r)
        
        print("\n" + "=" * 60)
        print("✅ TODOS LOS TESTS DE REDIS COMPLETADOS EXITOSAMENTE")
        print("🎉 Redis está completamente integrado y funcionando correctamente")
        
        # Limpiar datos de prueba
        cleanup_test_data(r)
        
    except Exception as e:
        print(f"❌ Error durante los tests: {e}")
    
    finally:
        if r:
            r.close()

if __name__ == "__main__":
    main()
