
import asyncio
import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime
import aio_pika
from aio_pika import Message, DeliveryMode
from aio_pika.abc import AbstractConnection, AbstractChannel
from ...application.config.app_config import config
logger = logging.getLogger(__name__)

class RabbitMQProducer:
    def __init__(self):
        self.rabbitmq_url = config.rabbitmq_url
        self.connection: Optional[AbstractConnection] = None
        self.channel: Optional[AbstractChannel] = None
        self.is_connected = False
        self.retry_count = 3
        self.retry_delay = 5

    async def connect(self):
        
        for attempt in range(self.retry_count):
            try:
                self.connection = await aio_pika.connect_robust(
                    self.rabbitmq_url,
                    heartbeat=600,
                    blocked_connection_timeout=300,
                )
                self.channel = await self.connection.channel()
                await self.channel.set_qos(prefetch_count=100)
                self.is_connected = True
                logger.info("RabbitMQ Producer conectado exitosamente")
                return
            except Exception as e:
                logger.error(f"Intento {attempt + 1} fallido: {e}")
                if attempt < self.retry_count - 1:
                    await asyncio.sleep(self.retry_delay)
                else:
                    logger.error(f" Error conectando a RabbitMQ después de {self.retry_count} intentos")
                    raise

    async def disconnect(self):
       
        try:
            if self.connection and not self.connection.is_closed:
                await self.connection.close()
            self.is_connected = False
            logger.info(" RabbitMQ Producer desconectado")
        except Exception as e:
            logger.error(f"Error desconectando RabbitMQ: {e}")

    async def ensure_connection(self):
        
        if not self.is_connected or self.connection.is_closed:
            await self.connect()

    async def declare_queue(self, queue_name: str, durable: bool = True):
        
        await self.ensure_connection()
        queue = await self.channel.declare_queue(queue_name, durable=durable)
        logger.info(f"Cola '{queue_name}' declarada")
        return queue

    async def publish_message(
        self,
        message: Dict[str, Any],
        queue_name: str,
        routing_key: str = None,
        priority: int = 0
    ):
        
        try:
            await self.ensure_connection()
            
            
            await self.declare_queue(queue_name)
            
            
            enriched_message = {
                **message,
                "timestamp": datetime.utcnow().isoformat(),
                "service": "soft-skills-practice-service",
                "version": "1.0.0",
                "queue": queue_name
            }

            message_body = json.dumps(enriched_message, ensure_ascii=False).encode('utf-8')

            
            await self.channel.default_exchange.publish(
                Message(
                    message_body,
                    delivery_mode=DeliveryMode.PERSISTENT,
                    content_type="application/json",
                    priority=priority,
                    headers={
                        "source": "soft-skills-practice-service",
                        "message_type": message.get("event_type", "unknown")
                    }
                ),
                routing_key=routing_key or queue_name
            )

            logger.info(f"Mensaje publicado a cola '{queue_name}': {message.get('event_type', 'unknown')}")

        except Exception as e:
            logger.error(f"Error publicando mensaje a {queue_name}: {e}")
            raise

    async def health_check(self) -> bool:
        """Verificar estado de la conexión"""
        try:
            if not self.connection or self.connection.is_closed:
                return False
            return True
        except:
            return False

        

rabbitmq_producer = RabbitMQProducer()