"""
Servicio de cola de mensajes para comunicación entre microservicios
Utiliza Redis como broker para enviar eventos de actualización de puntos
"""

import asyncio
import json
import redis.asyncio as redis
from typing import Dict, Any, Optional
from datetime import datetime
import os
from dotenv import load_dotenv
import logging

load_dotenv()

logger = logging.getLogger(__name__)

class MessageQueueService:
    """Servicio para manejo de colas de mensajes con Redis"""
    
    def __init__(self):
        self.redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
        self.redis_client: Optional[redis.Redis] = None
        
        # Nombres de colas
        self.PROFILE_UPDATES_QUEUE = "profile_updates"
        self.POINTS_UPDATES_QUEUE = "points_updates"
        self.ACHIEVEMENTS_QUEUE = "achievements_updates"
        
    async def connect(self):
        """Conectar al servidor Redis"""
        try:
            self.redis_client = redis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5
            )
            
            # Verificar conexión
            await self.redis_client.ping()
            logger.info("✅ Conectado a Redis para colas de mensajes")
            
        except Exception as e:
            logger.error(f"❌ Error conectando a Redis: {e}")
            self.redis_client = None
            raise
    
    async def disconnect(self):
        """Desconectar del servidor Redis"""
        if self.redis_client:
            await self.redis_client.close()
            logger.info("🔌 Desconectado de Redis")
    
    async def publish_points_update(
        self, 
        user_id: str, 
        points_earned: int, 
        simulation_data: Dict[str, Any]
    ) -> bool:
        """
        Publicar evento de actualización de puntos al microservicio de perfil
        
        Args:
            user_id: ID del usuario
            points_earned: Puntos ganados en la simulación
            simulation_data: Datos adicionales de la simulación
        
        Returns:
            bool: True si el mensaje fue enviado exitosamente
        """
        if not self.redis_client:
            logger.warning("⚠️  Redis no conectado, no se puede enviar mensaje")
            return False
        
        try:
            message = {
                "event_type": "points_earned",
                "timestamp": datetime.utcnow().isoformat(),
                "user_id": user_id,
                "points_earned": points_earned,
                "source_service": "soft-skills-practice-service",
                "simulation_data": {
                    "session_id": simulation_data.get("session_id"),
                    "skill_type": simulation_data.get("skill_type"),
                    "scenario_title": simulation_data.get("scenario_title"),
                    "final_score": simulation_data.get("final_score", 0),
                    "completion_percentage": simulation_data.get("completion_percentage", 100),
                    "time_spent_minutes": simulation_data.get("time_spent_minutes", 0),
                    "difficulty_level": simulation_data.get("difficulty_level", 1)
                },
                "metadata": {
                    "message_id": f"pts_{user_id}_{int(datetime.utcnow().timestamp())}",
                    "retry_count": 0,
                    "max_retries": 3
                }
            }
            
            # Publicar mensaje en la cola
            result = await self.redis_client.lpush(
                self.POINTS_UPDATES_QUEUE, 
                json.dumps(message)
            )
            
            logger.info(f"📤 Mensaje de puntos enviado: {user_id} -> {points_earned} puntos")
            return result > 0
            
        except Exception as e:
            logger.error(f"❌ Error enviando mensaje de puntos: {e}")
            return False
    
    async def publish_achievement_unlock(
        self,
        user_id: str,
        achievement_data: Dict[str, Any]
    ) -> bool:
        """
        Publicar evento de logro desbloqueado
        
        Args:
            user_id: ID del usuario
            achievement_data: Datos del logro desbloqueado
        
        Returns:
            bool: True si el mensaje fue enviado exitosamente
        """
        if not self.redis_client:
            logger.warning("⚠️  Redis no conectado, no se puede enviar mensaje")
            return False
        
        try:
            message = {
                "event_type": "achievement_unlocked",
                "timestamp": datetime.utcnow().isoformat(),
                "user_id": user_id,
                "source_service": "soft-skills-practice-service",
                "achievement_data": {
                    "achievement_id": achievement_data.get("achievement_id"),
                    "title": achievement_data.get("title"),
                    "description": achievement_data.get("description"),
                    "icon": achievement_data.get("icon"),
                    "rarity": achievement_data.get("rarity", "common"),
                    "points_value": achievement_data.get("points_value", 0)
                },
                "metadata": {
                    "message_id": f"ach_{user_id}_{int(datetime.utcnow().timestamp())}",
                    "retry_count": 0,
                    "max_retries": 3
                }
            }
            
            result = await self.redis_client.lpush(
                self.ACHIEVEMENTS_QUEUE,
                json.dumps(message)
            )
            
            logger.info(f"🏆 Mensaje de logro enviado: {user_id} -> {achievement_data.get('title')}")
            return result > 0
            
        except Exception as e:
            logger.error(f"❌ Error enviando mensaje de logro: {e}")
            return False
    
    async def publish_level_up(
        self,
        user_id: str,
        level_data: Dict[str, Any]
    ) -> bool:
        """
        Publicar evento de subida de nivel
        
        Args:
            user_id: ID del usuario
            level_data: Datos de la subida de nivel
        
        Returns:
            bool: True si el mensaje fue enviado exitosamente
        """
        if not self.redis_client:
            logger.warning("⚠️  Redis no conectado, no se puede enviar mensaje")
            return False
        
        try:
            message = {
                "event_type": "level_up",
                "timestamp": datetime.utcnow().isoformat(),
                "user_id": user_id,
                "source_service": "soft-skills-practice-service",
                "level_data": {
                    "previous_level": level_data.get("previous_level"),
                    "new_level": level_data.get("new_level"),
                    "total_points": level_data.get("total_points"),
                    "points_in_new_level": level_data.get("points_in_new_level")
                },
                "metadata": {
                    "message_id": f"lvl_{user_id}_{int(datetime.utcnow().timestamp())}",
                    "retry_count": 0,
                    "max_retries": 3
                }
            }
            
            result = await self.redis_client.lpush(
                self.PROFILE_UPDATES_QUEUE,
                json.dumps(message)
            )
            
            logger.info(f"⬆️  Mensaje de level up enviado: {user_id} -> Nivel {level_data.get('new_level')}")
            return result > 0
            
        except Exception as e:
            logger.error(f"❌ Error enviando mensaje de level up: {e}")
            return False
    
    async def publish_skill_progress_update(
        self,
        user_id: str,
        skill_progress_data: Dict[str, Any]
    ) -> bool:
        """
        Publicar evento de actualización de progreso en habilidad
        
        Args:
            user_id: ID del usuario
            skill_progress_data: Datos del progreso en la habilidad
        
        Returns:
            bool: True si el mensaje fue enviado exitosamente
        """
        if not self.redis_client:
            logger.warning("⚠️  Redis no conectado, no se puede enviar mensaje")
            return False
        
        try:
            message = {
                "event_type": "skill_progress_updated",
                "timestamp": datetime.utcnow().isoformat(),
                "user_id": user_id,
                "source_service": "soft-skills-practice-service",
                "skill_progress": {
                    "skill_type": skill_progress_data.get("skill_type"),
                    "skill_name": skill_progress_data.get("skill_name"),
                    "previous_progress": skill_progress_data.get("previous_progress", 0),
                    "new_progress": skill_progress_data.get("new_progress", 0),
                    "sessions_completed": skill_progress_data.get("sessions_completed", 0),
                    "average_score": skill_progress_data.get("average_score", 0),
                    "improvement_areas": skill_progress_data.get("improvement_areas", [])
                },
                "metadata": {
                    "message_id": f"skill_{user_id}_{int(datetime.utcnow().timestamp())}",
                    "retry_count": 0,
                    "max_retries": 3
                }
            }
            
            result = await self.redis_client.lpush(
                self.PROFILE_UPDATES_QUEUE,
                json.dumps(message)
            )
            
            logger.info(f"📈 Mensaje de progreso de skill enviado: {user_id} -> {skill_progress_data.get('skill_type')}")
            return result > 0
            
        except Exception as e:
            logger.error(f"❌ Error enviando mensaje de progreso de skill: {e}")
            return False
    
    async def get_queue_size(self, queue_name: str) -> int:
        """Obtener el tamaño de una cola específica"""
        if not self.redis_client:
            return 0
        
        try:
            return await self.redis_client.llen(queue_name)
        except Exception as e:
            logger.error(f"❌ Error obteniendo tamaño de cola {queue_name}: {e}")
            return 0
    
    async def get_queue_stats(self) -> Dict[str, int]:
        """Obtener estadísticas de todas las colas"""
        return {
            "points_updates": await self.get_queue_size(self.POINTS_UPDATES_QUEUE),
            "achievements": await self.get_queue_size(self.ACHIEVEMENTS_QUEUE),
            "profile_updates": await self.get_queue_size(self.PROFILE_UPDATES_QUEUE)
        }

# Instancia global del servicio
message_queue_service = MessageQueueService()
