import os
import logging 
from typing import Dict,Any,List,Optional
from .rabbitmq_producer import RabbitMQProducer
from ...application.config.app_config import config

class EventPublisher:
    def __init__(self,rabbitmq_producer: RabbitMQProducer):
        self.rabbitmq_producer = rabbitmq_producer
        self.notification_queue = config.notifications_queue_name
        self.profile_queue = config.profile_queue_name
    
    async def publish_simulation_finished(
            self,
            feedbackResult:Any,
            
    ):
        """Publicar evento de finalización de simulación"""
        message = {
            "event": "simulation_finished",
            "data": feedbackResult
        }
        
        try:
            await self.rabbitmq_producer.publish_message(
                message,
                queue_name=self.notification_queue,
                priority=5
            )

            await self.rabbitmq_producer.publish_message(
                message,
                queue_name=self.profile_queue,
                priority=5)
            print(f"✅ Evento 'simulation_finished' publicado: {message}")
            return True
        except Exception as e:
            logging.error(f"Error al publicar evento 'simulation_finished': {e}")
            return False
        
        